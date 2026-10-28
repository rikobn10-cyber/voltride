# VoltRide demo-video generator

Records the real app (Playwright + Chromium), overlays subtitle/intro/outro cards, and encodes a 1080x1920 H.264 MP4 with ffmpeg.
Not used by the site and not run by CI. Needs `playwright` and `ffmpeg`.

    python3 -m http.server 8130 &            # serve the repo
    node tools/video/make_video.js tools/video/scenarios/cost.json cost.mp4

A scenario JSON defines: `assert` (JS expressions that must be true, so subtitles never state stale numbers), `scroll` keyframes,
timed `actions` (JS run in the page), `subs` ([from, to, text]), and `intro`/`outro` cards. Copy `scenarios/cost.json` to start a new video.
Honesty: subtitles must only state numbers the app really shows; mark estimates as estimates.
