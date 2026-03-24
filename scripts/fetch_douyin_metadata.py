#!/usr/bin/env python3
"""Fetch Douyin metadata through yt-dlp and normalize it to the skill schema."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def _yt_dlp_cmd():
    """Return the yt-dlp command as a list, preferring the module invocation."""
    import shutil
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]


def format_duration(duration):
    if not duration:
        return ""
    duration = int(duration)
    if duration >= 3600:
        return f"{duration // 3600}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
    return f"{duration // 60}:{duration % 60:02d}"


def normalize_timestamp(value):
    if not value:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        pass

    text = str(value).strip()
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(text, fmt)
            return int(dt.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    return 0


def pick_tags(info):
    tags = []
    for key in ("tags", "categories"):
        values = info.get(key) or []
        for value in values:
            if value and value not in tags:
                tags.append(str(value))
    return tags[:12]


def build_cover_url(info):
    for key in ("thumbnail", "cover", "webpage_url_basename"):
        value = info.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value
    thumbnails = info.get("thumbnails") or []
    for item in reversed(thumbnails):
        url = item.get("url")
        if url:
            return url
    return ""


def extract_aweme_id(info, url):
    for key in ("display_id", "aweme_id", "id"):
        value = info.get(key)
        if value:
            return str(value)
    if "/video/" in url:
        return url.rstrip("/").split("/video/")[-1].split("?")[0]
    return ""


def fetch_info(url):
    command = _yt_dlp_cmd() + [
        "--dump-single-json",
        "--no-playlist",
        "--skip-download",
        url,
    ]
    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "yt-dlp metadata fetch failed")

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid yt-dlp JSON output: {exc}") from exc


def normalize(info, source_url):
    uploader = info.get("uploader") or info.get("creator") or info.get("channel") or ""
    return {
        "title": info.get("title", ""),
        "author": uploader,
        "description": info.get("description", ""),
        "view_count": info.get("view_count") or 0,
        "like_count": info.get("like_count") or 0,
        "coin_count": info.get("repost_count") or 0,
        "favorite_count": info.get("favorite_count") or info.get("collect_count") or 0,
        "share_count": info.get("share_count") or info.get("repost_count") or 0,
        "comment_count": info.get("comment_count") or 0,
        "tags": pick_tags(info),
        "duration": format_duration(info.get("duration")),
        "duration_seconds": info.get("duration") or 0,
        "publish_date": normalize_timestamp(info.get("timestamp") or info.get("upload_date")),
        "cover_url": build_cover_url(info),
        "douyin_id": extract_aweme_id(info, source_url),
        "platform": "douyin",
        "platform_id": extract_aweme_id(info, source_url),
        "webpage_url": info.get("webpage_url") or source_url,
        "subtitle_urls": [],
        "raw_subtitles": info.get("subtitles") or {},
        "automatic_captions": info.get("automatic_captions") or {},
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_douyin_metadata.py <Douyin URL>"}))
        sys.exit(1)

    url = sys.argv[1].strip()
    try:
        info = fetch_info(url)
        print(json.dumps(normalize(info, url), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
