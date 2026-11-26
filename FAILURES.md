# FAILURES

### 2026-11-26  Local ACE-Step install hung on my Mac
- **What I tried:** Installed ACE-Step 1.5 locally with `uv sync` to generate the score on my own machine.
- **What broke (exact error or symptom):** `uv sync` ran for a long time with nothing downloading. The `.venv` folder stayed tiny (about 60 KB) and a macOS "Open Anyway" security prompt was waiting in the background.
- **What I tried next:** Waited, then checked the folder size with `du -sh` to confirm nothing was happening.
- **What fixed it or what I worked around it with:** Stopped it with Ctrl+C and moved to a hosted version of the model instead of a local install.
- **What I would do differently:** Start the install the day before, and approve the macOS security prompt straight away instead of leaving it hidden.

### 2026-11-26  Hugging Face ACE-Step Space would not generate
- **What I tried:** Generated the music in the ACE-Step 1.5 Hugging Face Space.
- **What broke (exact error or symptom):** First "Failed to create sample: 5Hz LM not initialized" in Simple mode, then a Seed field "Error" badge, then "Model not fully initialized. Missing components: ['model', 'vae', 'text_tokenizer', 'text_encoder']". Later the Generate Music button stayed greyed out and the status box stayed empty. Batch size also reset to 2 when I typed 3.
- **What I tried next:** Switched to Custom mode, turned Instrumental on and Thinking off, set vocal language to unknown, typed the bpm, key, time signature and duration, and clicked Generate several times.
- **What fixed it or what I worked around it with:** I used the hosted acemusic.ai version of the same model to produce the candidates instead.
- **What I would do differently:** Test the music tool first, early in the day, because it depends on a shared free GPU I do not control. Keep the placeholder drone as a ready fallback.

(Add any other real breakages from your own run here, for example a Gemini or Cloudflare limit, an Amharic word read wrongly, or a bad keyframe. Only write what happened.)

### 2026-11-26  Gemini TTS quota error on one shot
- **What I tried:** Generating the narration for all ten shots in one run.
- **What broke (exact error or symptom):** The narration for shot s07 failed with `429 RESOURCE_EXHAUSTED` (see the error line in `runs.jsonl`).
- **What I tried next:** Nothing by hand. The stage retries three times with growing waits.
- **What fixed it or what I worked around it with:** The retry succeeded about a minute later and the other shots stayed cached, so nothing had to be redone.
- **What I would do differently:** Space out the calls, or run fewer shots at once, when the free tier is busy.

### 2026-11-26  First render was over the length limit
- **What I tried:** Rendering the film with the pauses I had set around each narration line.
- **What broke (exact error or symptom):** The film ran about 95 seconds. The brief says 60 to 90. A peer on Slack pointed it out.
- **What I tried next:** I measured each shot with `timeline.plan()` and saw that narration length was setting most shots.
- **What fixed it or what I worked around it with:** I shortened the pauses and the end card and re-rendered only the assemble stage. Both films are now 89 seconds (E2 in EXPERIMENTS.md).
- **What I would do differently:** Check the total length straight after the radio cut, before I make pictures.

### 2026-11-26  Missing tools on my Mac
- **What I tried:** Re-running the assemble stage on my Mac.
- **What broke (exact error or symptom):** `ModuleNotFoundError: No module named 'jsonschema'` and `command not found: ffprobe`.
- **What I tried next:** Read the traceback to see which stage failed.
- **What fixed it or what I worked around it with:** `pip3 install -r requirements.txt` and `brew install ffmpeg`.
- **What I would do differently:** Run `pip install -r requirements.txt` and check for ffmpeg first, as the README says.