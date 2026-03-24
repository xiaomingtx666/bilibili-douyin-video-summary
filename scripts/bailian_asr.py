#!/usr/bin/env python3
"""
Upload a local audio file to Alibaba Bailian (DashScope) temp storage,
then submit ASR transcription task and output text to stdout.

Flow:
1. GET /uploads?action=getPolicy&model=fun-asr → get OSS upload credentials
2. POST to OSS upload_host with credentials + file → get oss:// URL
3. POST /services/audio/asr/transcription with oss:// URL + OssResourceResolve header
4. Poll task until SUCCEEDED
5. Fetch transcription result and print text

Requires: DASHSCOPE_API_KEY environment variable.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://dashscope.aliyuncs.com/api/v1"
MODEL = "fun-asr"
POLL_INTERVAL = 3
MAX_POLL_ATTEMPTS = 200


def get_api_key():
    key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DASHSCOPE_API_KEY environment variable is not set")
    return key


def get_upload_policy(api_key, model_name):
    """GET /uploads?action=getPolicy&model=<model> to obtain OSS upload credentials."""
    url = f"{API_BASE}/uploads?action=getPolicy&model={model_name}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "data" not in data:
        raise RuntimeError(f"Failed to get upload policy: {data}")
    return data["data"]


def upload_file_to_oss(policy_data, file_path):
    """Upload file to OSS using multipart/form-data POST. Returns oss:// URL."""
    import mimetypes

    file_name = os.path.basename(file_path)
    key = f"{policy_data['upload_dir']}/{file_name}"
    upload_host = policy_data["upload_host"]

    boundary = "----WebKitFormBoundary" + str(int(time.time() * 1000))

    fields = [
        ("OSSAccessKeyId", policy_data["oss_access_key_id"]),
        ("Signature", policy_data["signature"]),
        ("policy", policy_data["policy"]),
        ("x-oss-object-acl", policy_data["x_oss_object_acl"]),
        ("x-oss-forbid-overwrite", policy_data["x_oss_forbid_overwrite"]),
        ("key", key),
        ("success_action_status", "200"),
    ]

    body_parts = []
    for field_name, field_value in fields:
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'.encode())
        body_parts.append(f"{field_value}\r\n".encode())

    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        file_data = f.read()

    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode())
    body_parts.append(f"Content-Type: {content_type}\r\n\r\n".encode())
    body_parts.append(file_data)
    body_parts.append(f"\r\n--{boundary}--\r\n".encode())

    body = b"".join(body_parts)

    req = urllib.request.Request(upload_host, data=body, method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status not in (200, 201, 204):
            raise RuntimeError(f"OSS upload failed with status {resp.status}")

    return f"oss://{key}"


def submit_asr_task(api_key, file_url):
    """Submit transcription task with oss:// URL. Returns task_id."""
    url = f"{API_BASE}/services/audio/asr/transcription"
    body = json.dumps({
        "model": MODEL,
        "input": {"file_urls": [file_url]},
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
        "X-DashScope-OssResourceResolve": "enable",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    task_id = data.get("output", {}).get("task_id", "")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {data}")
    return task_id


def poll_task(api_key, task_id):
    """Poll until task completes. Returns the final output."""
    url = f"{API_BASE}/tasks/{task_id}"
    for i in range(MAX_POLL_ATTEMPTS):
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {api_key}",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        status = data.get("output", {}).get("task_status", "")
        if status == "SUCCEEDED":
            return data
        elif status in ("FAILED", "CANCELED"):
            raise RuntimeError(f"Task {status}: {json.dumps(data, ensure_ascii=False)}")

        print(f"  Task status: {status} (poll {i+1})...", file=sys.stderr)
        time.sleep(POLL_INTERVAL)

    raise RuntimeError("Task polling timed out")


def extract_text(result):
    """Extract transcribed text from the ASR result."""
    results = result.get("output", {}).get("results", [])
    all_text = []
    for r in results:
        transcript_url = r.get("transcription_url", "")
        if transcript_url:
            req = urllib.request.Request(transcript_url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                tr_data = json.loads(resp.read().decode("utf-8"))
            transcripts = tr_data.get("transcripts", [])
            for t in transcripts:
                sentences = t.get("sentences", [])
                for s in sentences:
                    text = s.get("text", "").strip()
                    if text:
                        all_text.append(text)
    return "\n".join(all_text)


def main():
    if len(sys.argv) < 2:
        print("Usage: bailian_asr.py <audio_file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1].strip()
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        api_key = get_api_key()

        print("Getting upload credentials...", file=sys.stderr)
        policy_data = get_upload_policy(api_key, MODEL)

        print("Uploading audio to temp storage...", file=sys.stderr)
        oss_url = upload_file_to_oss(policy_data, file_path)
        print(f"Upload done: {oss_url}", file=sys.stderr)

        print("Submitting ASR task...", file=sys.stderr)
        task_id = submit_asr_task(api_key, oss_url)
        print(f"Task submitted: {task_id}", file=sys.stderr)

        print("Polling for result...", file=sys.stderr)
        result = poll_task(api_key, task_id)

        text = extract_text(result)
        if text:
            print(text)
        else:
            print("Warning: ASR returned empty text", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
