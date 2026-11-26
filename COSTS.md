# COSTS

## Measured latency (from runs.jsonl)

Run `python3 -m pipeline.cli costs` and paste the table it prints here.

(paste the table)

## GPU minutes (Kaggle or Colab)

| Job | Model | Resolution | Clips | GPU minutes | Notes |
|---|---|---|---|---|---|
| Moving shots | none | n/a | 0 | 0 | I used Ken Burns motion on the keyframes with FFmpeg on my laptop, so no GPU was rented |
| Music | ACE-Step 1.5 (hosted) | n/a | 2 to 3 candidates | not measured | Free hosted tool, no GPU time billed to me |

## Free-tier limits I actually found (check each at the time)

- Gemini API TTS: (write the limit you saw in your Google AI Studio quota page, or "did not reach a limit")
- Cloudflare Workers AI daily allowance: (write what your dashboard showed, or "did not reach a limit")
- Kaggle weekly GPU hours: not used

## List-price equivalent

For each hosted call, look up the published price today and write the arithmetic, for example:

- Gemini TTS: (number of narration calls from runs.jsonl) x (price per call or per character) = (result)
- FLUX schnell on Cloudflare: (number of images from runs.jsonl) x (price per image) = (result)
- ACE-Step: free hosted tool, 0

Total actual cash spent: 0 (everything ran on free tiers).