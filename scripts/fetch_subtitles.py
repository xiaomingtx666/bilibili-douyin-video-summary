#!/usr/bin/env python3
"""Fetch Bilibili CC subtitle JSON and output plain text to stdout."""

import json
import sys
import urllib.request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}

def fetch_subtitle_text(url: str) -> str:
    if url.startswith("//"):
        url = "https:" + url

    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    body = data.get("body", [])
    if not body:
        raise RuntimeError("Subtitle body is empty")

    lines = [item.get("content", "") for item in body if item.get("content")]
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_subtitles.py <subtitle_json_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1].strip()
    try:
        text = fetch_subtitle_text(url)
        print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
