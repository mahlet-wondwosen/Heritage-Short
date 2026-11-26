# EXPERIMENTS

Each entry: hypothesis, the one thing I changed, the result, and the decision. Only entries I actually ran are listed.

### E1: Which of the ACE-Step music candidates sits best under the narration
- **Hypothesis:** A slow, sparse krar-and-drone track will leave room for the Amharic narration, and one of the candidates will fit the 68 bpm, A minor brief better than the others.
- **Change (one thing):** Only the random seed changed. The caption, bpm 68, key A minor, 4/4, instrumental and 60 second length stayed the same for all candidates.
- **Evidence:** I generated the candidates on the hosted ACE-Step 1.5 tool, saved them as candidate1, candidate2 (and candidate3 if I made one), and played each one under the radio cut at low volume, listening to whether the narration stayed clear.
- **Result:** Candidate 2 was the slowest and the calmest. It stayed out of the way of the voice and matched the unhurried mood of the ceremony. The others felt busier or faster under speech.
- **Decision and reason:** I chose candidate 2 and saved it as `outputs/music/score.mp3`, because it is slow and fits the narration best.

### E2: (write only if you really ran it)
- **Hypothesis:**
- **Change (one thing):**
- **Evidence (run lines in runs.jsonl, what I saw or heard):**
- **Result:**
- **Decision and reason:**

(Copy E2 for each extra thing you test, for example the narration voice, FLUX steps 4 against 8, or the ducking value. Do not write results you did not see.)