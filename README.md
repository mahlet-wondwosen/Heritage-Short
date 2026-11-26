# Buna: The Sound of Patience

A 76 second short film about a grandmother's coffee ceremony, narrated in Amharic with English subtitles, made by a pipeline in code. One file, `storyboard.json`, is the contract between every stage. Change one shot in it and only that shot is regenerated.

## Run it (from a clean clone)

```bash
git clone <this repository>
cd <folder>
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your own keys
make film                     # or: python3 -m pipeline.cli film
```

Output: `outputs/final/buna_9x16.mp4` (vertical), `outputs/final/buna_16x9.mp4` (horizontal) and `outputs/final/subtitles.en.srt`.

No keys yet? `OFFLINE=1 DRAFT=1 make film` runs the whole pipeline with placeholder images and silent narration, so you can check that the plumbing works. Placeholders are marked in `runs.jsonl` and are never a finished film.

## Keys you need (all free tiers, no card)

| Variable | From |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio (narration) |
| `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` | Cloudflare dashboard, Workers AI (keyframes) |

Keys live in `.env`, which is ignored by git.

## Stages

| Command | What it does | Output |
|---|---|---|
| `validate` | Checks `storyboard.json` against `schema/storyboard.schema.json` | none |
| `narration` | Gemini TTS, one WAV per shot | `outputs/narration/` |
| `keyframes` | Reference sheet, then one FLUX image per shot (Cloudflare Workers AI) | `outputs/keyframes/` |
| `shots` | Moves each keyframe: a supplied Wan 2.2 clip from `outputs/clips/sXX.mp4` if present, else a Ken Burns move | `outputs/shots/` |
| `music` | Uses `outputs/music/score.mp3` (your ACE-Step choice), or a placeholder drone | `outputs/music/` |
| `assemble` | Cuts to the narration, English subtitles, music ducked under the voice, -14 LUFS, end card, both formats | `outputs/final/` |
| `radio` | Narration over placeholder music on a black screen, for the first user test | `outputs/final/radio_cut.mp4` |
| `costs` | Latency and call counts per stage from `runs.jsonl`, as a markdown table | printed |

Regenerate a single shot: edit it in `storyboard.json`, then `python3 -m pipeline.cli film --only s03`.

## What it costs

All stages run on free tiers. Measured latency and a list-price equivalent are in `COSTS.md`.

## Files

`ARCHITECTURE.md` (stages, contracts, caching, failures), `DESIGN.md` (audience and user tests), `EXPERIMENTS.md`, `FAILURES.md`, `COSTS.md`, `ETHICS.md`, `runs.jsonl` (one line per model call).
