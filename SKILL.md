---
name: bilibili+douyin-video-summary
description: Fetch a Bilibili or Douyin video URL and generate a standalone Chinese HTML summary note card. Use when the user provides a B站/bilibili/抖音/Douyin link and asks to summarize, analyze, or take notes from it. Trigger phrases include 总结视频, 分析视频, 视频笔记, 总结B站, 总结bilibili, 总结抖音, 分析抖音视频, summarize this video.
---

# Bilibili / Douyin Video Summary to HTML

## Silent Execution Protocol

You MUST complete the whole flow in one turn.

- Do not ask for confirmation at any step.
- If a dependency is missing, install it silently and continue.
- If some data is missing, fall back to the defaults below.
- All user-facing text must be in Simplified Chinese.
- Final reply must be one short Chinese sentence only.

## Defaults

| Parameter | Default |
|-----------|---------|
| Summary length | 500–800 characters |
| Language | Simplified Chinese |
| Output location | Current working directory |
| Date | Today's date |
| Fallback filename | `video-summary-{platform}-{id}-{YYYY-MM-DD}.html` |

## Workflow

Execute every step in order without interruption.

### Step 1: Detect Platform and Normalize URL

Decide whether the URL is from Bilibili or Douyin before doing anything else.

Supported sources:

- Bilibili full link: `https://www.bilibili.com/video/BV...`
- Bilibili short link: `https://b23.tv/...`
- Douyin full link: `https://www.douyin.com/video/...`
- Douyin share link: `https://v.douyin.com/...`

Resolution rules:

- For `b23.tv`:
  ```bash
  curl -sI 'https://b23.tv/XXXXXX' | grep -i '^location:' | sed 's/location: *//i' | tr -d '\r'
  ```
- For `v.douyin.com`:
  ```bash
  curl -sI 'https://v.douyin.com/XXXXXX/' | grep -i '^location:' | sed 's/location: *//i' | tr -d '\r'
  ```

Extraction rules:

- Bilibili: extract `BV[a-zA-Z0-9]+`
- Douyin: extract the numeric aweme id from `/video/<ID>`

If the platform still cannot be determined, jump to Step 7.

### Step 2: Fetch Metadata

#### Bilibili

Run:

```bash
python3 ~/.cursor/skills/bilibili+douyin-video-summary/scripts/fetch_metadata.py <BV号>
```

This returns normalized JSON fields such as:
`title`, `author`, `description`, `view_count`, `like_count`, `coin_count`, `favorite_count`, `share_count`, `comment_count`, `tags`, `duration`, `publish_date`, `cover_url`, `bvid`, `subtitle_urls`.

Fallbacks:

- If the script fails, use WebFetch on `https://www.bilibili.com/video/<BV号>` and extract best-effort metadata from the page.
- If metadata still cannot be obtained, jump to Step 7.

#### Douyin

Install `yt-dlp` if needed, then run:

```bash
pip3 install yt-dlp --quiet
python3 ~/.cursor/skills/bilibili+douyin-video-summary/scripts/fetch_douyin_metadata.py '<抖音链接>'
```

This returns the same normalized schema, plus:
`douyin_id`, `platform`, `platform_id`, `automatic_captions`, `raw_subtitles`, `webpage_url`.

Fallbacks:

- If the script fails, use WebFetch on the resolved Douyin page and extract best-effort metadata from HTML.
- If metadata still cannot be obtained, jump to Step 7.

### Step 3: Obtain Video Content Text

Try in order and stop at the first success.

#### P0: Existing subtitle files

If metadata includes subtitles, fetch and convert them to plain text.

For Bilibili CC subtitle JSON:

```bash
python3 ~/.cursor/skills/bilibili+douyin-video-summary/scripts/fetch_subtitles.py <subtitle_json_url>
```

For generic subtitle URLs or files:

```bash
python3 ~/.cursor/skills/bilibili+douyin-video-summary/scripts/extract_subtitle_text.py <subtitle_url_or_file>
```

Subtitle sources to check:

- Bilibili: `subtitle_urls`
- Douyin: `automatic_captions`, `raw_subtitles`, or subtitle URLs exposed by `yt-dlp`

If a usable transcript is extracted, go to Step 4.

#### P1: Bailian ASR via audio extraction

If `DASHSCOPE_API_KEY` exists, use ASR for both platforms.

1. Install `yt-dlp` if missing:
   ```bash
   pip3 install yt-dlp --quiet
   ```
2. Download audio:
   - Bilibili:
     ```bash
     yt-dlp -x --audio-format mp3 -o "/tmp/video_audio_%(id)s.%(ext)s" "https://www.bilibili.com/video/<BV号>"
     ```
   - Douyin:
     ```bash
     yt-dlp -x --audio-format mp3 -o "/tmp/video_audio_%(id)s.%(ext)s" "<抖音链接>"
     ```
3. Transcribe:
   ```bash
   python3 ~/.cursor/skills/bilibili+douyin-video-summary/scripts/bailian_asr.py /tmp/video_audio_*.mp3
   ```
4. If ASR succeeds, go to Step 4.

#### P2: Platform-specific local fallback

- Bilibili only:
  ```bash
  pip3 install bilibili-captions --quiet 2>/dev/null
  bilibili-captions <BV号> --output-format text --output /tmp/bili_captions_<BV号>.txt
  ```
  If successful, read the output text and go to Step 4.

- Douyin:
  Skip this step if no subtitles or ASR are available.

#### P3: Best-Effort Summary from page info

If all transcript methods fail, use:

- title
- description
- tags
- visible page text
- top comments if they can be fetched from the page

If there is enough text to summarize, continue to Step 4.
Otherwise, jump to Step 7.

### Step 4: Generate Structured Chinese Summary

Use the transcript or fallback text plus metadata to produce a Chinese summary in `总—分—总` format.

Structure:

1. `总览摘要`
2. `核心要点` with 3–6 points
3. `总结与启示`

Rules:

- 500–800 Chinese characters total
- Plain, beginner-friendly language
- Cover the major topics instead of cherry-picking a few details
- If terminology is unavoidable, add a short parenthetical explanation
- Do not exceed 800 characters

### Step 5: Assemble the HTML Note Card

Read:

```bash
cat ~/.cursor/skills/bilibili+douyin-video-summary/templates.md
```

Always use the `Video Note Card Template`.

Fill these placeholders:

- `{VIDEO_TITLE}`
- `{AUTHOR}`
- `{AUTHOR_LABEL}`: Bilibili uses `UP主`; Douyin uses `作者`
- `{PLATFORM_NAME}`: `Bilibili` or `抖音`
- `{PLATFORM_ID_LABEL}`: Bilibili uses `BV号`; Douyin uses `作品ID`
- `{PLATFORM_ID}`: `bvid` or `douyin_id`
- `{PUBLISH_DATE_LABEL}`: always `发布`
- `{PUBLISH_DATE}`
- `{DURATION_LABEL}`: always `时长`
- `{DURATION}`
- `{VIEW_COUNT}`
- `{LIKE_COUNT}`
- `{VIEW_LABEL}`: usually `播放`
- `{LIKE_LABEL}`: usually `点赞`
- `{STAT3_VALUE}`
- `{STAT3_LABEL}`
- `{STAT4_VALUE}`
- `{STAT4_LABEL}`
- `{SHARE_COUNT}`
- `{SHARE_LABEL}`: Bilibili uses `分享`; Douyin uses `转发`
- `{COMMENT_COUNT}`
- `{COMMENT_LABEL}`: `评论`
- `{TAGS}`
- `{OVERVIEW_TEXT}`
- `{KEY_POINTS_HTML}`
- `{TAKEAWAY_TEXT}`
- `{COVER_URL}`
- `{VIDEO_URL}`
- `{DATE}`

Metric mapping:

- Bilibili:
  - `STAT3_VALUE` → `coin_count`
  - `STAT3_LABEL` → `投币`
  - `STAT4_VALUE` → `favorite_count`
  - `STAT4_LABEL` → `收藏`
- Douyin:
  - `STAT3_VALUE` → `favorite_count`
  - `STAT3_LABEL` → `收藏`
  - `STAT4_VALUE` → `N/A`
  - `STAT4_LABEL` → `扩展指标`

If Douyin metadata includes a better fourth metric from `yt-dlp`, use it instead of `N/A`.

Formatting rules:

- If count ≥ 10000, format as `X.X万`
- If count ≥ 100000000, format as `X.X亿`
- If tags are absent, omit the entire tags section
- If cover is absent, use the no-cover header

Missing field defaults:

- author → `未知作者`
- counts → `N/A`
- duration → `未知`
- publish date → `未知`
- platform id → `未知`

### Step 6: Save the HTML File

Filename rules:

1. Prefer the video title.
2. Convert to lowercase.
3. Replace spaces and punctuation with hyphens.
4. Keep ASCII letters, digits, hyphens, and CJK.
5. Truncate to 60 characters and append `.html`.
6. If title is unavailable, use `video-summary-{platform}-{id}-{YYYY-MM-DD}.html`.

Save to the current working directory.

Reply with exactly one short sentence:

`已生成视频笔记 `{filename}`，保存在当前目录。`

Do not paste the HTML.

### Step 7: Error Fallback

If the URL is invalid or metadata/text retrieval completely fails:

1. Read the `Error Page Template` from `templates.md`.
2. Generate an error HTML page containing:
   - attempted URL
   - error reason
   - retry suggestion
   - fill `{ATTEMPTED_URL}` and `{ERROR_REASON}`
3. Save as `video-fetch-failed-{YYYY-MM-DD}.html`.
4. Reply:
   `该视频无法访问（{错误原因}），已生成错误占位页 `{filename}`。`

## Source Priority

```text
Existing subtitles / captions
        │
        ▼
Bailian ASR via yt-dlp audio
        │
        ▼
Bilibili local captions fallback
        │
        ▼
Title + description + tags + page text + comments
        │
        ▼
Error placeholder HTML
```

## Bundled Files

- `scripts/fetch_metadata.py`: fetch Bilibili metadata
- `scripts/fetch_douyin_metadata.py`: fetch Douyin metadata through `yt-dlp`
- `scripts/fetch_subtitles.py`: fetch Bilibili CC subtitle JSON
- `scripts/extract_subtitle_text.py`: convert JSON / VTT / SRT subtitle sources into text
- `scripts/bailian_asr.py`: transcribe extracted audio
- `templates.md`: HTML note-card and error-page templates
