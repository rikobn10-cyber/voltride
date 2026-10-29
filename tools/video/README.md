# VoltRide demo-video generator

Records the real app (Playwright + Chromium), overlays subtitle/intro/outro cards, and encodes a 1080x1920 H.264 MP4 with ffmpeg.
Not used by the site and not run by CI. Needs `playwright` and `ffmpeg`.

    python3 -m http.server 8130 &            # serve the repo
    node tools/video/make_video.js tools/video/scenarios/cost.json cost.mp4

A scenario JSON defines: `assert` (JS expressions that must be true, so subtitles never state stale numbers), `scroll` keyframes,
timed `actions` (JS run in the page), `subs` ([from, to, text]), and `intro`/`outro` cards. Copy `scenarios/cost.json` to start a new video.
Honesty: subtitles must only state numbers the app really shows; mark estimates as estimates.

## Optional voice-over (TTS)

Add a `voice` block to a scenario to speak the subtitles:

    "voice": {"cmd": ["espeak-ng", "-v", "ar", "-s", "170", "-w", "{out}", "{text}"], "maxSpeedup": 1.35}

`cmd` is an argv array (no shell): `{text}` is the spoken text and `{out}` is the .wav the engine must write. Any engine that can write a wav
from the command line works (a neural voice can be plugged in the same way). The spoken text of a subtitle is its optional 4th element
(use it for Modern Standard Arabic, diacritics or numbers written as words); otherwise the subtitle text without emoji is spoken.
Each line starts with its subtitle; if it is longer than its slot it is sped up (up to `maxSpeedup`), and a warning names any line that still
overflows. The generator also warns if the final audio track is silent. espeak-ng is robotic and does not speak Moroccan Darija:
treat it as a plumbing test, not as a brand voice.
