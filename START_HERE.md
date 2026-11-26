# START HERE (step by step, for a Mac)

You do not need to understand the code. You run commands in Terminal and look at the results.
Typing rule: copy each command exactly, paste it into Terminal, press Enter, wait for it to finish.

## Part 1: put the files in place (10 minutes)

1. Download `heritage-short.zip` from the chat. Double-click it in Finder. A folder `heritage-short` appears.
2. Drag that folder into your **Documents** folder.
3. Open **Terminal** (Cmd+Space, type Terminal, Enter).
4. Type `cd ` (c, d, space), then drag the `heritage-short` folder from Finder into the Terminal window, and press Enter. Terminal is now "inside" the folder. Check with: `ls` (you should see README.md, storyboard.json, pipeline).
5. Make a private Python space and install what is needed (once):
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   If `python3` is not found, macOS will offer to install developer tools. Accept, wait, and repeat step 5.
   Every time you open a NEW Terminal window later, run steps 4 and `source .venv/bin/activate` again first.
6. Test that everything works, with no keys (this uses fake pictures and silent narration):
   ```
   OFFLINE=1 DRAFT=1 python3 -m pipeline.cli film
   open outputs/final
   ```
   You should see `buna_9x16.mp4` and `buna_16x9.mp4`. Play one: a brown circle with English subtitles. That proves the machine works.
7. Delete the fake outputs before the real run:
   ```
   rm -rf outputs runs.jsonl
   mkdir outputs
   ```

## Part 2: get your free keys (20 to 30 minutes)

1. **Gemini key:** go to https://aistudio.google.com, sign in, click "Get API key", create one, copy it.
2. **Cloudflare:** sign up at https://dash.cloudflare.com. Copy your **Account ID** (shown on the dashboard home or the Workers & Pages page). Then open My Profile, API Tokens, Create Token, choose the **Workers AI** template, create it and copy the token (shown once).
3. **Kaggle** (for the optional video clips and for the music): sign up at https://www.kaggle.com and verify your phone in Settings. Start this early, it can be slow.
4. In Terminal, create your key file:
   ```
   cp .env.example .env
   open -e .env
   ```
   Paste each key after the `=` sign (no spaces, no quotes), save, close. Never share this file or paste keys in chat or screenshots.

## Part 3: fix the narration, then make the radio cut (45 minutes)

1. Open `storyboard.json` (right-click, Open With, TextEdit). Each shot has `text_native` (Amharic) and `text_en`. **Check and correct every Amharic line** (ask a family member), and the meaning of the three coffee rounds. Keep the quotes and commas as they are. Save.
2. Check it is still valid: `python3 -m pipeline.cli validate`
3. Make narration: `python3 -m pipeline.cli narration`. Listen: `open outputs/narration` and play a few files. If Amharic sounds wrong, note it in FAILURES.md. If a model name is rejected, open https://ai.google.dev/gemini-api/docs/speech-generation, find the current text-to-speech model name, put it in `.env` as `TTS_MODEL=...`, and run again.
4. Make the radio cut: `python3 -m pipeline.cli radio`, then `open outputs/final/radio_cut.mp4`.
5. **User test 1:** send radio_cut.mp4 to at least 3 people like your audience (family, or Slack colleagues). Ask: what did you feel, what confused you, what would you cut? Write their answers in DESIGN.md under "User test 1". Change the storyboard if they say something useful.

## Part 4: pictures (30 to 60 minutes)

1. `python3 -m pipeline.cli keyframes` (first the reference sheet, then 10 images).
2. `open outputs/keyframes` and look at each image. Check hands, faces and whether the grandmother looks the same. If one is bad, delete that file (for example `rm outputs/keyframes/s04.jpg`), optionally improve its `image_prompt`, and run `python3 -m pipeline.cli keyframes --only s04`. Write what you saw in EXPERIMENTS.md or FAILURES.md.
3. Make the moving shots: `python3 -m pipeline.cli shots`. This gives every shot a slow camera move. You can already finish a complete film this way.

## Part 5: music (45 minutes, in parallel with Part 4)

1. Run `python3 -m pipeline.cli music-brief` to print the caption, tempo and key.
2. On Kaggle or Colab, follow the ACE-Step 1.5 guide (https://github.com/ACE-Step/ACE-Step-1.5), paste that brief, and make 3 candidates.
3. Listen to each under the radio cut at low volume. Pick one and write why in EXPERIMENTS.md.
4. Save your choice as `outputs/music/score.mp3` in the project folder.
5. If you cannot get a GPU, keep the placeholder drone and record that honestly in FAILURES.md.

## Part 6: optional upgrade, real video clips

If Kaggle works, animate your keyframes with Wan 2.2 TI2V-5B (draft at 480p), name each clip `s01.mp4`, `s02.mp4` and so on, and put them in `outputs/clips/`. Then run `python3 -m pipeline.cli shots` and `python3 -m pipeline.cli assemble`. Shots with no clip keep the camera-move version.

## Part 7: the final film (about 20 minutes)

1. `python3 -m pipeline.cli film` (no OFFLINE, no DRAFT). Watch both files in `outputs/final` on your phone with sound on.
2. **User test 2:** show the near-final cut to 3 people, write the results in DESIGN.md, and fix what you can.
3. Fill in `COSTS.md` (run `python3 -m pipeline.cli costs` and paste), `ETHICS.md`, `EXPERIMENTS.md` (about 10 entries) and `FAILURES.md` with what really happened.

## Part 8: publish and submit (before 23:59 tonight, aim for 21:30)

1. Create a **public** GitHub repository. In Terminal inside the folder:
   ```
   git init
   git add .
   git commit -m "Heritage Short pipeline"
   git branch -M main
   git remote add origin https://github.com/YOUR-NAME/YOUR-REPO.git
   git push -u origin main
   ```
   Before pushing, check `.env` is NOT in `git status` (it is ignored). Never commit keys.
2. Upload both MP4 files somewhere that opens without a login (YouTube unlisted or TikTok public, Google Drive "anyone with the link").
3. Post the film publicly, with the platform's **AI label on**. Write the post yourself: the story, why it matters to you, one thing you learned.
4. Record the walkthrough (max 5 minutes, screen recording): show the structure, explain one hard decision, edit one line in `storyboard.json`, rerun `python3 -m pipeline.cli film`, and show that only that shot changes (the output says "cached" for the rest).
5. Write the report (PDF or Word): audience and what they said, hardest problem, one suggested practice that helped and one that did not (with evidence), anything extra you tried, what you would do next.
6. Submit Assignment 1 (repo link and report) and Assignment 2 (vertical MP4, then attach horizontal MP4, walkthrough and post). Then do the AI interview.
