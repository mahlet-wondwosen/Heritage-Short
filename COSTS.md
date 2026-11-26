# COSTS

Everything ran on free tiers, so the cash I paid was **$0**. The numbers below come from `runs.jsonl`.

## Measured latency per stage

Produced by `python3 -m pipeline.cli costs`:

```
(paste the table printed by the command)
```

Cache hits are calls that were skipped because the input hash had not changed. They cost nothing and are counted separately.

## GPU minutes

| Job | Model | Clips | GPU minutes | Notes |
|---|---|---|---|---|
| Moving shots | none (FFmpeg Ken Burns) | 0 | 0 | I did not use a GPU for video. Wan 2.2 was not run. |
| Music | ACE-Step 1.5, hosted | 3 candidates | not measured | I used a free hosted tool, so no GPU time was billed to me. |

## Free-tier limits I actually met

- **Gemini TTS:** I hit the quota once. `runs.jsonl` has a `429 RESOURCE_EXHAUSTED` error for the narration of shot s07, and the retry logic succeeded about a minute later. The free tier covers this model for input and output on the standard tier.
- **Cloudflare Workers AI:** the free allowance is 10,000 Neurons a day. `runs.jsonl` shows no image call failing, so I did not hit it.
- **Kaggle:** not used.

## List-price equivalent

Published prices, checked on 26 November 2026:

- FLUX.1 schnell on Cloudflare Workers AI: $0.0000528 per 512x512 tile and $0.0001056 per step.
- Gemini 2.5 Flash Preview TTS: $0.50 per 1M input tokens and $10.00 per 1M output (audio) tokens.

The arithmetic is printed by `python3 -m pipeline.pricing`:

```
(paste the three lines printed by the command)
```

Assumptions: images are 1024x1024 (4 tiles); text is about 4 characters per token; Gemini audio is about 32 tokens per second. ACE-Step on the hosted tool was free. FFmpeg is free.

## Frontier comparison

I had no access to a frontier lane (Omni Flash, Nano Banana, Lyria 3.5), so I made no comparison.