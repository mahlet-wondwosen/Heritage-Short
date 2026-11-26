"""Stage: music. Uses your chosen score if present, otherwise makes a quiet placeholder drone to test with."""
from __future__ import annotations

from pipeline.common import OUT, digest, is_fresh, load_storyboard, log_run, mark_fresh, run_ffmpeg
from pipeline.timeline import plan

DIR = OUT / "music"
SCORE_NAMES = ["score.mp3", "score.wav", "score.m4a", "score.flac"]


def find_score():
    for name in SCORE_NAMES:
        if (DIR / name).exists():
            return DIR / name
    return None


def brief() -> None:
    """Print what to paste into ACE-Step (Kaggle or Colab) to make candidates."""
    music = load_storyboard()["music"]
    print("Paste into ACE-Step:")
    print(f"  Caption: {music['caption']}")
    print(f"  Instrumental: {music['instrumental']}   BPM: {music['bpm']}   Key: {music['key']}")
    print(f"  Duration: {int(music['duration_s'])} s   Candidates: {music['candidates']}")
    print(f"Save your chosen file as {DIR / 'score.mp3'}")


def run(only: str | None = None) -> None:
    sb = load_storyboard()
    DIR.mkdir(parents=True, exist_ok=True)
    score = find_score()
    if score:
        print(f"  music: using {score.name}")
        log_run("music", model="chosen-score", note=f"using {score.name}", cached=True)
        return
    total = plan(sb)["total"] + 2
    out = DIR / "placeholder.wav"
    key = digest("drone", round(total))
    if is_fresh(out, key):
        print("  music: placeholder (cached). Add outputs/music/score.mp3 for your real score.")
        return
    d = f"{total:.2f}"
    run_ffmpeg(["-f", "lavfi", "-i", f"sine=frequency=110:sample_rate=48000:duration={d}",
                "-f", "lavfi", "-i", f"sine=frequency=164.81:sample_rate=48000:duration={d}",
                "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=48000:duration={d}",
                "-filter_complex",
                "[0]volume=0.5[a];[1]volume=0.3[b];[2]volume=0.15[c];[a][b][c]amix=inputs=3,volume=1.5,"
                f"tremolo=f=0.2:d=0.4,afade=t=in:d=2,afade=t=out:st={total - 4:.2f}:d=4",
                "-ac", "2", str(out)])
    mark_fresh(out, key)
    log_run("music", model="ffmpeg-placeholder-drone", note="temp track only, not the score")
    print("  music: placeholder drone made. Add outputs/music/score.mp3 for your real score.")
