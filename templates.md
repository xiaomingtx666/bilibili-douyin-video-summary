# HTML Templates

## Video Note Card Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{VIDEO_TITLE} — 视频笔记</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: #f0f2f5; color: #1a1a2e; line-height: 1.8; padding: 2rem 1rem;
    }
    .container { max-width: 800px; margin: 0 auto; }

    /* Cover Card */
    .cover-card {
      position: relative; border-radius: 16px; overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.12); margin-bottom: 1.5rem;
    }
    .cover-card img {
      width: 100%; height: 280px; object-fit: cover; display: block;
    }
    .cover-card .overlay {
      position: absolute; bottom: 0; left: 0; right: 0;
      background: linear-gradient(transparent, rgba(0,0,0,0.85));
      padding: 2rem 1.5rem 1.2rem;
    }
    .cover-card .overlay h1 {
      font-size: 1.6rem; font-weight: 700; color: #fff;
      line-height: 1.4; margin-bottom: 0.4rem;
    }
    .cover-card .overlay .author {
      font-size: 0.9rem; color: rgba(255,255,255,0.8);
    }
    .no-cover-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 16px; padding: 2.5rem 2rem;
      box-shadow: 0 8px 32px rgba(0,0,0,0.12); margin-bottom: 1.5rem;
    }
    .no-cover-header h1 {
      font-size: 1.6rem; font-weight: 700; color: #fff;
      line-height: 1.4; margin-bottom: 0.4rem;
    }
    .no-cover-header .author { font-size: 0.9rem; color: rgba(255,255,255,0.8); }

    /* Stats Bar */
    .stats-bar {
      display: flex; flex-wrap: wrap; gap: 0.5rem;
      background: #fff; border-radius: 12px; padding: 1rem 1.2rem;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 1.5rem;
    }
    .stat-item {
      display: flex; align-items: center; gap: 0.35rem;
      font-size: 0.85rem; color: #666; padding: 0.25rem 0.6rem;
      background: #f5f6fa; border-radius: 8px;
    }
    .stat-item svg { width: 16px; height: 16px; flex-shrink: 0; }
    .stat-item .val { font-weight: 600; color: #333; }

    /* Meta Info */
    .meta-row {
      display: flex; flex-wrap: wrap; gap: 0.8rem; align-items: center;
      margin-bottom: 1.5rem; font-size: 0.85rem; color: #888;
    }
    .meta-row span { display: flex; align-items: center; gap: 0.3rem; }

    /* Tags */
    .tags { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.5rem; }
    .tag {
      background: #eef2ff; color: #4f46e5; font-size: 0.8rem;
      padding: 0.2rem 0.7rem; border-radius: 999px; font-weight: 500;
    }

    /* Summary Card */
    .summary-card {
      background: #fff; border-radius: 16px; padding: 2rem;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 1.5rem;
    }
    .summary-card h2 {
      font-size: 1.2rem; color: #1a1a2e; margin-bottom: 1.2rem;
      padding-bottom: 0.6rem; border-bottom: 2px solid #eef2ff;
    }
    .summary-card h2 .icon { margin-right: 0.5rem; }

    /* Overview */
    .overview {
      background: linear-gradient(135deg, #f8f9ff 0%, #eef2ff 100%);
      border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;
      border-left: 4px solid #4f46e5;
    }
    .overview p { color: #374151; font-size: 0.95rem; }

    /* Key Points */
    .key-point {
      margin-bottom: 1.2rem; padding-left: 1rem;
      border-left: 3px solid #e5e7eb;
    }
    .key-point:hover { border-left-color: #4f46e5; }
    .key-point h3 {
      font-size: 1rem; color: #1a1a2e; margin-bottom: 0.3rem; font-weight: 600;
    }
    .key-point p { font-size: 0.9rem; color: #4b5563; }

    /* Takeaway */
    .takeaway {
      background: #fffbeb; border-radius: 12px; padding: 1.2rem 1.5rem;
      margin-top: 1.5rem; border-left: 4px solid #f59e0b;
    }
    .takeaway p { color: #92400e; font-size: 0.95rem; }

    /* Content Source Badge */
    .source-badge {
      display: inline-block; font-size: 0.75rem; padding: 0.15rem 0.5rem;
      border-radius: 999px; font-weight: 500; margin-bottom: 1rem;
    }
    .source-badge.subtitle { background: #d1fae5; color: #065f46; }
    .source-badge.asr { background: #dbeafe; color: #1e40af; }
    .source-badge.page-info { background: #fef3c7; color: #92400e; }

    /* Footer */
    .footer {
      text-align: center; padding: 1.5rem; font-size: 0.8rem; color: #9ca3af;
    }
    .footer a { color: #4f46e5; text-decoration: none; }
    .footer a:hover { text-decoration: underline; }

    @media (max-width: 640px) {
      body { padding: 1rem 0.5rem; }
      .cover-card img { height: 180px; }
      .cover-card .overlay h1, .no-cover-header h1 { font-size: 1.2rem; }
      .stats-bar { gap: 0.4rem; padding: 0.8rem; }
      .summary-card { padding: 1.2rem; }
    }
  </style>
</head>
<body>
  <div class="container">

    <!-- Cover / Header: use .cover-card if cover_url exists, otherwise .no-cover-header -->
    <!-- WITH COVER: -->
    <div class="cover-card">
      <img src="{COVER_URL}" alt="视频封面">
      <div class="overlay">
        <h1>{VIDEO_TITLE}</h1>
        <span class="author">{AUTHOR_LABEL}：{AUTHOR}</span>
      </div>
    </div>
    <!-- WITHOUT COVER (use this instead if no cover): -->
    <!--
    <div class="no-cover-header">
      <h1>{VIDEO_TITLE}</h1>
      <span class="author">{AUTHOR_LABEL}：{AUTHOR}</span>
    </div>
    -->

    <!-- Meta Row -->
    <div class="meta-row">
      <span>{PLATFORM_ID_LABEL}：{PLATFORM_ID}</span>
      <span>·</span>
      <span>{PUBLISH_DATE_LABEL}：{PUBLISH_DATE}</span>
      <span>·</span>
      <span>{DURATION_LABEL}：{DURATION}</span>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
        <span class="val">{VIEW_COUNT}</span> {VIEW_LABEL}
      </div>
      <div class="stat-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><path d="M14 9V5a3 3 0 00-3-3l-4 9v11h11.28a2 2 0 002-1.7l1.38-9a2 2 0 00-2-2.3H14z"/><path d="M7 22H4a2 2 0 01-2-2v-7a2 2 0 012-2h3"/></svg>
        <span class="val">{LIKE_COUNT}</span> {LIKE_LABEL}
      </div>
      <div class="stat-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        <span class="val">{STAT3_VALUE}</span> {STAT3_LABEL}
      </div>
      <div class="stat-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
        <span class="val">{STAT4_VALUE}</span> {STAT4_LABEL}
      </div>
      <div class="stat-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
        <span class="val">{SHARE_COUNT}</span> {SHARE_LABEL}
      </div>
      <div class="stat-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        <span class="val">{COMMENT_COUNT}</span> {COMMENT_LABEL}
      </div>
    </div>

    <!-- Tags (omit this section entirely if no tags) -->
    <div class="tags">
      {TAGS}
      <!-- Each tag: <span class="tag">#标签名</span> -->
    </div>

    <!-- Summary -->
    <div class="summary-card">
      <h2><span class="icon">📝</span>视频内容总结</h2>

      <!-- Content source badge: choose ONE based on source -->
      <!-- <span class="source-badge subtitle">字幕来源</span> -->
      <!-- <span class="source-badge asr">语音识别</span> -->
      <!-- <span class="source-badge page-info">页面信息</span> -->

      <!-- Overview -->
      <div class="overview">
        <p>{OVERVIEW_TEXT}</p>
      </div>

      <!-- Key Points -->
      {KEY_POINTS_HTML}
      <!--
      <div class="key-point">
        <h3>要点标题</h3>
        <p>要点解释内容</p>
      </div>
      -->

      <!-- Takeaway -->
      <div class="takeaway">
        <p>{TAKEAWAY_TEXT}</p>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <p>本笔记由 AI 自动生成 · 生成日期：{DATE}</p>
      <p>原始{PLATFORM_NAME}视频：<a href="{VIDEO_URL}" target="_blank">{VIDEO_URL}</a></p>
    </div>

  </div>
</body>
</html>
```

## Error Page Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>访问失败 — 无法获取视频内容</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: #f0f2f5; display: flex; justify-content: center;
      align-items: center; min-height: 100vh; padding: 1rem;
    }
    .error-card {
      background: #fff; border-radius: 16px; padding: 3rem 2.5rem;
      box-shadow: 0 8px 32px rgba(0,0,0,0.08); max-width: 520px;
      width: 100%; text-align: center;
    }
    .error-card .icon { font-size: 3rem; margin-bottom: 1rem; }
    .error-card h1 {
      color: #ef4444; font-size: 1.5rem; margin-bottom: 0.8rem; font-weight: 700;
    }
    .error-card .desc { color: #6b7280; margin-bottom: 1.2rem; font-size: 0.95rem; }
    .error-card .url-box {
      background: #f9fafb; padding: 0.8rem 1rem; border-radius: 10px;
      word-break: break-all; font-size: 0.85rem; color: #374151;
      border: 1px solid #e5e7eb; margin-bottom: 1.2rem;
    }
    .error-card .reason {
      background: #fef2f2; color: #991b1b; padding: 0.6rem 1rem;
      border-radius: 8px; font-size: 0.85rem; margin-bottom: 1.5rem;
    }
    .error-card .hint { font-size: 0.8rem; color: #9ca3af; }
  </style>
</head>
<body>
  <div class="error-card">
    <div class="icon">⚠️</div>
    <h1>视频访问失败</h1>
    <p class="desc">无法获取以下视频的内容：</p>
    <div class="url-box">{ATTEMPTED_URL}</div>
    <div class="reason">错误原因：{ERROR_REASON}</div>
    <p class="hint">请检查链接是否正确，或稍后重试。</p>
  </div>
</body>
</html>
```
