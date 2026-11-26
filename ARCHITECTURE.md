# ARCHITECTURE

## The contract

`storyboard.json` is the only thing stages share. It is validated against `schema/storyboard.schema.json` before every run (`pipeline/common.py: load_storyboard`), so a typo fails in one second, not after twenty minutes of generation. Every shot carries its prompts, seed, camera move, narration in two languages and a written reason for existing.

## Stages

```
validate -> narration -> keyframes -> shots -> music -> assemble
                \________________ timeline.py ________________/
```

| Stage | Reads | Writes | Provider |
|---|---|---|---|
| narration | `text_native`, voice style | `outputs/narration/sXX.wav` | Gemini TTS |
| keyframes | style block, character, `image_prompt`, seed | `outputs/keyframes/sXX.jpg` | Cloudflare Workers AI (FLUX) |
| shots | keyframe or `outputs/clips/sXX.mp4`, `camera`, timing | `outputs/shots/sXX_<format>.mp4` | Wan 2.2 (supplied) or FFmpeg Ken Burns |
| music | `music` block | `outputs/music/score.*` | ACE-Step (made on Kaggle/Colab), or placeholder |
| assemble | all of the above | `outputs/final/` | FFmpeg and Pillow |

`timeline.py` decides how long each shot lasts: the longer of the storyboard duration and the narration length plus a small margin. Narration therefore sets the pace, and the same timeline is used for shots, subtitles and the audio track.

## Caching

Each generated file has a sidecar `<file>.hash`. The hash covers every input that affects it (prompt text, model, steps, seed, style block, camera, duration, size, and the bytes of the keyframe or clip). A stage skips a file whose hash still matches, and logs a `cached: true` line. Editing one shot's prompt changes only that shot's hash, so only that shot is regenerated. To force a fresh image from an unchanged prompt, delete the image file.

## Failure handling

- Network calls (`narration.synthesize`, `keyframes.generate`) retry 3 times with exponential backoff (`common.retry`).
- After the last attempt the stage logs `status: error` to `runs.jsonl` and stops with a clear message naming the shot. Finished shots stay cached, so a re-run resumes where it stopped.
- Moving shots fall back to a Ken Burns move on the keyframe, so a missing or failed video clip never blocks the film.
- Music falls back to a placeholder drone (clearly labelled as a temp track) if no chosen score exists.
- Secrets come from `.env` or environment variables only, and `.env` is git-ignored.

## Logging

Every model call appends one line to `runs.jsonl`: time, stage, shot, model, parameters, seed, latency, cost, status, cached, error. `python3 -m pipeline.cli costs` turns the log into the table used in `COSTS.md`.

## Known limits

- FLUX.1 schnell on Workers AI takes no reference image, so character consistency comes from a fixed character description, a fixed style block, painted style and never showing a face. This is tested in `EXPERIMENTS.md`.
- The Cloudflare image call is not sent a seed by default; the seed is logged for reproducibility records and used in the cache key.
- Loudness uses single-pass `loudnorm`; a two-pass run would be more exact.
