# DESIGN

## Audience and intent (written before generating anything)

**Who watches:** my family and followers in Ethiopia and the diaspora. They watch on a phone, usually vertical, in a few quiet minutes. They know the coffee ceremony, so the film does not explain it. Some are far from home.

**What they should feel at the end:** warmth and a little homesickness, and the sense that patience and welcome, not the coffee itself, are what the ceremony gives.

**The story:** a grandchild remembers a morning coffee ceremony at their grandmother's house. The narrator is the grandchild, speaking in Amharic, with English subtitles.

**Why this story:** I can tell it from memory, it is made of objects and places rather than faces, and it has a natural beginning, middle and end (grass, roasting, grinding, waiting, pouring, three rounds).

## Design choices and their reasons

- **Painted, not photorealistic.** A gouache style hides the weak spots of generated faces and hands, and keeps the film from borrowing a real person's likeness.
- **The grandmother is never shown facing the camera.** She appears from behind, in profile or in silhouette. This keeps her identity consistent across shots without training anything, because the image model I used takes no reference image.
- **Mostly objects.** Seven of ten shots show no person at all, which lowers the risk of identity drift.
- **Narration sets the timing.** Each shot lasts as long as its narration plus a short gap, so pictures, subtitles and audio share one timeline.
- **Ten shots, 89 seconds in the final render.** My first render was 95 seconds, over the 60 to 90 second limit, so I trimmed the gaps (see E2 in EXPERIMENTS.md).
- **Every shot has a stated reason** in `storyboard.json`.

## Consent

No real person's face or voice appears. The narration is a stock TTS voice, not a cloned one. See ETHICS.md.

## User test 1: radio cut (narration over placeholder music)

- **Who and when:** 26 November 2026. My mother Tshehay, my father Wondwosen and my brother Teddy. All three know the coffee ceremony well, so they are the audience I made it for.
- **What they said:** all three said they liked it.
- **What I changed:** nothing in the storyboard. The radio cut showed me the narration timing was workable, so I moved on to the pictures.

## User test 2: near-final cut

- **Who and when:** 26 November 2026. The same three people, on their phones.
- **What they said:** they liked the final version, including the music.
- **What changed:** nothing in the storyboard.

## User test 3: peers on Slack

- **Who and when:** 26 November 2026. Colleagues in the cohort Slack channel.
- **What they said:** one pointed out that my cut ran about 95 seconds, over the 60 to 90 second brief. Another told me to remove or fill in the bracketed placeholders in my report.
- **What changed:** I shortened the gaps around the narration and the end card, re-rendered both formats at 89 seconds, and removed the placeholders from the report.