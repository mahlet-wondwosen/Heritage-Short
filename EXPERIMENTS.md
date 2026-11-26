# EXPERIMENTS

Each entry: hypothesis, the one thing I changed, the evidence, the result and what I decided. I only list experiments I actually ran.

### E1: Which ACE-Step candidate sits best under the narration
- **Hypothesis:** A slow, sparse krar-and-drone track will leave room for the Amharic narration, and one of the candidates will fit that brief better than the others.
- **Change (one thing):** Only the random seed. The caption, 68 bpm, A minor, 4/4, instrumental and 60 second length were the same for every candidate.
- **Evidence:** I made the candidates on the hosted ACE-Step 1.5 tool, saved them as candidate1 to candidate3, and played each one quietly under the radio cut, listening for whether the narration stayed clear.
- **Result:** Candidate 2 was the slowest and calmest. It stayed out of the voice's way and matched the unhurried mood of the ceremony. The others felt busier or faster under speech.
- **Decision:** I chose candidate 2 and saved it as `outputs/music/score.mp3`.

### E2: Can I get under the 90 second limit by trimming gaps instead of cutting story
- **Hypothesis:** Narration sets each shot's length, so the 95 s cut is long mostly because of the pauses I added around each line and the 3 second end card. Shortening those should bring the film under 90 s without touching the story or the narration.
- **Change:** Shorter lead-in before each narration line, shorter tail after it, a shorter end card, and a shorter first shot. I changed these together because the goal was to fit the limit, not to measure each one alone. This is a weakness of the experiment and I note it here on purpose.
- **Evidence:** `timeline.plan()` reported a total of 95.1 s before the change. After re-running `assemble`, `ffprobe` showed 89.0 s for both `buna_9x16.mp4` and `buna_16x9.mp4`. The narration files were not regenerated (cache hits in `runs.jsonl`), so the voice and the words are identical.
- **Result:** 95.1 s down to 89.0 s, inside the 60 to 90 s limit, with no story cut and no new model calls.
- **Decision:** Keep it. The README and DESIGN.md now state 89 s. A peer on Slack was the one who noticed the first cut was too long.