#!/usr/bin/env python3
"""Fetch Bilibili video metadata via public API. Output JSON to stdout."""

import json
import sys
import urllib.request
import urllib.error
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}

def bv_to_aid(bv: str):
    """Use Bilibili API to convert BV to aid if needed."""
    return None

def fetch_video_info(bv: str) -> dict:
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if data.get("code") != 0:
        raise RuntimeError(f"API error: code={data.get('code')}, message={data.get('message')}")

    d = data["data"]
    stat = d.get("stat", {})

    subtitle_urls = []
    subtitle_info = d.get("subtitle", {})
    for s in subtitle_info.get("list", []):
        sub_url = s.get("subtitle_url", "")
        if sub_url:
            if sub_url.startswith("//"):
                sub_url = "https:" + sub_url
            subtitle_urls.append({"lang": s.get("lan", ""), "url": sub_url})

    duration_sec = d.get("duration", 0)
    if duration_sec >= 3600:
        dur_str = f"{duration_sec // 3600}:{(duration_sec % 3600) // 60:02d}:{duration_sec % 60:02d}"
    else:
        dur_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"

    tags = []
    try:
        tag_url = f"https://api.bilibili.com/x/tag/archive/tags?bvid={bv}"
        tag_req = urllib.request.Request(tag_url, headers=HEADERS)
        with urllib.request.urlopen(tag_req, timeout=10) as tag_resp:
            tag_data = json.loads(tag_resp.read().decode("utf-8"))
        if tag_data.get("code") == 0:
            tags = [t["tag_name"] for t in tag_data.get("data", []) if "tag_name" in t]
    except Exception:
        pass

    return {
        "title": d.get("title", ""),
        "author": d.get("owner", {}).get("name", ""),
        "description": d.get("desc", ""),
        "view_count": stat.get("view", 0),
        "like_count": stat.get("like", 0),
        "coin_count": stat.get("coin", 0),
        "favorite_count": stat.get("favorite", 0),
        "share_count": stat.get("share", 0),
        "comment_count": stat.get("reply", 0),
        "danmaku_count": stat.get("danmaku", 0),
        "tags": tags,
        "duration": dur_str,
        "duration_seconds": duration_sec,
        "publish_date": d.get("pubdate", 0),
        "cover_url": d.get("pic", ""),
        "cid": d.get("cid", 0),
        "bvid": d.get("bvid", bv),
        "aid": d.get("aid", 0),
        "subtitle_urls": subtitle_urls,
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_metadata.py <BV号>"}))
        sys.exit(1)

    bv = sys.argv[1].strip()
    if not re.match(r"^BV[a-zA-Z0-9]+$", bv):
        bv_match = re.search(r"(BV[a-zA-Z0-9]+)", bv)
        if bv_match:
            bv = bv_match.group(1)
        else:
            print(json.dumps({"error": f"Invalid BV number: {bv}"}))
            sys.exit(1)

    try:
        info = fetch_video_info(bv)
        print(json.dumps(info, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
