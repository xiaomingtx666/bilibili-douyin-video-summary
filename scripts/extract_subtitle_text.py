#!/usr/bin/env python3
"""Extract plain text from subtitle files such as JSON, VTT, SRT, or ASS."""

import json
import re
import sys
import urllib.request


HEADERS = {
    "User-Agent": "Mozilla/5.0",
}


def load_text(source):
    if source.startswith(("http://", "https://")):
        req = urllib.request.Request(source, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="ignore")
    with open(source, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def parse_json(text):
    data = json.loads(text)
    if isinstance(data, dict):
        if isinstance(data.get("body"), list):
            return "\n".join(item.get("content", "").strip() for item in data["body"] if item.get("content"))
        events = data.get("events") or []
        if events:
            return "\n".join(
                seg.strip()
                for event in events
                for seg in event.get("segs", [])
                if seg.get("utf8")
            )
    raise RuntimeError("Unsupported subtitle JSON structure")


def strip_markup(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{[^}]+\}", "", text)
    return text.strip()


def parse_vtt_or_srt(text):
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.upper() == "WEBVTT":
            continue
        if re.match(r"^\d+$", line):
            continue
        if "-->" in line:
            continue
        if line.startswith("NOTE") or line.startswith("STYLE"):
            continue
        cleaned = strip_markup(line)
        if cleaned:
            lines.append(cleaned)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_subtitle_text.py <subtitle_url_or_file>", file=sys.stderr)
        sys.exit(1)

    source = sys.argv[1].strip()
    try:
        text = load_text(source)
        stripped = text.lstrip()
        if stripped.startswith("{") or stripped.startswith("["):
            print(parse_json(text))
        else:
            print(parse_vtt_or_srt(text))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
