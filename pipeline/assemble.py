"""Stage: assembly. Narration track, burned-in English subtitles, ducked music, loudness, end card, both formats."""
from __future__ import annotations

import json
import time
import wave
from pathlib import Path

from pipeline import music, narration
from pipeline.common import OUT, load_storyboard, log_run, run_ffmpeg
from pipeline.shots import DIR as SHOTS_DIR
from pipeline.shots import FPS, size_for
from pipeline.timeline import plan, subtitle_cues

FINAL = OUT / "final"
WORK = OUT / "work"

FONT_LATIN = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf"]
FONT_ETHIOPIC = ["/System/Library/Fonts/Supplemental/Kefa.ttc", "/System/Library/Fonts/Kefa.ttc",
                 "C:/Windows/Fonts/nyala.ttf", "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf",
                 "/usr/share/fonts/truetype/abyssinica/AbyssinicaSIL-Regular.ttf"]


def font(candidates: list[str], size: int):
    from PIL import ImageFont

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size) if candidates is FONT_LATIN else None


def wrap_two_lines(text: str, max_chars: int = 40) -> list[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        if len(current) + len(word) + 1 > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines


def subtitle_png(text: str, w: int, h: int, out: Path) -> None:
    """A transparent full-frame image with the caption inside the safe area."""
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    portrait = h > w
    size = max(18, int((w if portrait else h) / (24 if portrait else 20)))
    f = font(FONT_LATIN, size)
    lines = wrap_two_lines(text)
    line_h = int(size * 1.3)
    box_h = line_h * len(lines) + size
    widest = max(draw.textlength(line, font=f) for line in lines)
    bottom = int(h * (0.78 if portrait else 0.92))   # vertical: clear of the platform buttons
    top = bottom - box_h
    left = int((w - widest) / 2 - size * 0.6)
    draw.rounded_rectangle((left, top, left + widest + size * 1.2, bottom), radius=int(size * 0.4),
                           fill=(30, 24, 20, 170))
    y = top + size // 2
    for line in lines:
        x = (w - draw.textlength(line, font=f)) / 2
        draw.text((x, y), line, font=f, fill=(250, 244, 232, 255))
        y += line_h
    img.save(out)


def endcard_png(sb: dict, w: int, h: int, out: Path) -> None:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (w, h), (46, 36, 30))
    draw = ImageDraw.Draw(img)
    big = font(FONT_LATIN, int(min(w, h) / 9))
    small = font(FONT_LATIN, int(min(w, h) / 18))
    rows = [(sb["title"], big, (240, 226, 200)), (sb["end_card"]["text_en"], small, (205, 180, 150))]
    native_font = font(FONT_ETHIOPIC, int(min(w, h) / 18))
    if native_font:
        rows.append((sb["end_card"]["text_native"], native_font, (205, 180, 150)))
    total = sum(int(f.size * 1.6) for _, f, _ in rows)
    y = (h - total) // 2
    for text, f, color in rows:
        draw.text(((w - draw.textlength(text, font=f)) / 2, y), text, font=f, fill=color)
        y += int(f.size * 1.6)
    img.save(out)


def write_narration_track(tl: dict, out: Path) -> None:
    """One WAV the full length of the film, each line placed at its shot (pure Python, no ffmpeg)."""
    rate, frames, cursor = narration.SAMPLE_RATE, [], 0
    for item in tl["shots"]:
        wav = narration.wav_path(item["id"])
        if not wav.exists():
            continue
        target = int(item["narr_start"] * rate)
        if target > cursor:
            frames.append(b"\x00\x00" * (target - cursor))
            cursor = target
        with wave.open(str(wav), "rb") as w:
            data = w.readframes(w.getnframes())
        frames.append(data)
        cursor += len(data) // 2
    end = int(tl["total"] * rate)
    if end > cursor:
        frames.append(b"\x00\x00" * (end - cursor))
    narration.write_wav(out, b"".join(frames))


def write_srt(cues: list[dict], out: Path) -> None:
    def stamp(t: float) -> str:
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

    blocks = [f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n" for i, c in enumerate(cues, 1)]
    out.write_text("\n".join(blocks), encoding="utf-8")


def audio_chain(total: float, music_input: int, narr_input: int) -> str:
    """Music ducked under the narration, mixed, then normalised to about -14 LUFS with a -1 dB true peak."""
    return (f"[{narr_input}:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={total:.2f},"
            f"asplit=2[nsc][nmix];"
            f"[{music_input}:a]aresample=48000,aformat=channel_layouts=stereo,aloop=loop=-1:size=2000000000,"
            f"atrim=0:{total:.2f},afade=t=in:d=1.5,afade=t=out:st={max(total - 3, 0):.2f}:d=3,volume=0.55[m];"
            f"[m][nsc]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[duck];"
            f"[duck][nmix]amix=inputs=2:duration=longest:dropout_transition=0,volume=2,"
            f"loudnorm=I=-14:TP=-1:LRA=11[aout]")


def chosen_music() -> Path:
    path = music.find_score()
    if path:
        return path
    placeholder = music.DIR / "placeholder.wav"
    if not placeholder.exists():
        music.run()
    return placeholder


def render_format(sb: dict, tl: dict, cues: list[dict], fmt: str, narr_wav: Path) -> Path:
    tag, w, h = size_for(fmt)
    WORK.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)
    endcard = WORK / f"endcard_{tag}.png"
    endcard_png(sb, w, h, endcard)
    endclip = WORK / f"endcard_{tag}.mp4"
    run_ffmpeg(["-loop", "1", "-framerate", str(FPS), "-i", str(endcard), "-t", str(tl["end_card_length"]),
                "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-r", str(FPS), "-pix_fmt", "yuv420p", str(endclip)])
    listing = WORK / f"concat_{tag}.txt"
    lines = []
    for item in tl["shots"]:
        clip = SHOTS_DIR / f"{item['id']}_{tag}.mp4"
        if not clip.exists():
            raise SystemExit(f"Missing {clip.name}. Run the shots stage first.")
        lines.append(f"file '{clip.resolve()}'")
    lines.append(f"file '{endclip.resolve()}'")
    listing.write_text("\n".join(lines))
    joined = WORK / f"joined_{tag}.mp4"
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(joined)])

    inputs = ["-i", str(joined), "-i", str(narr_wav), "-i", str(chosen_music())]
    filters, last = [], "0:v"
    for i, cue in enumerate(cues):
        png = WORK / f"sub_{tag}_{i:02d}.png"
        subtitle_png(cue["text"], w, h, png)
        inputs += ["-i", str(png)]
        filters.append(f"[{last}][{3 + i}:v]overlay=0:0:enable='between(t,{cue['start']},{cue['end']})'[v{i}]")
        last = f"v{i}"
    filter_complex = ";".join(filters + [audio_chain(tl["total"], 2, 1)])
    out = FINAL / f"buna_{tag}.mp4"
    run_ffmpeg([*inputs, "-filter_complex", filter_complex, "-map", f"[{last}]", "-map", "[aout]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
                "-t", f"{tl['total']:.2f}", str(out)])
    return out


def run(only: str | None = None) -> None:
    sb = load_storyboard()
    tl = plan(sb)
    cues = subtitle_cues(sb, tl)
    WORK.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)
    (OUT / "timeline.json").write_text(json.dumps({"timeline": tl, "subtitles": cues}, indent=2))
    write_srt(cues, FINAL / "subtitles.en.srt")
    narr_wav = WORK / "narration_full.wav"
    write_narration_track(tl, narr_wav)
    for fmt in sb["formats"]:
        started = time.time()
        out = render_format(sb, tl, cues, fmt, narr_wav)
        log_run("assemble", model="ffmpeg", latency_s=time.time() - started,
                params={"format": fmt, "total_s": tl["total"], "loudnorm": "I=-14 TP=-1", "ducking": "sidechaincompress"})
        print(f"  {out.name}: {tl['total']:.0f}s")


def radio_cut() -> None:
    """Narration over the placeholder score on a black screen: the first thing to show your audience."""
    sb = load_storyboard()
    tl = plan(sb)
    WORK.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)
    narr_wav = WORK / "narration_full.wav"
    write_narration_track(tl, narr_wav)
    out = FINAL / "radio_cut.mp4"
    started = time.time()
    run_ffmpeg(["-f", "lavfi", "-i", f"color=c=black:s=640x360:r=5:d={tl['total']:.2f}",
                "-i", str(narr_wav), "-i", str(chosen_music()),
                "-filter_complex", audio_chain(tl["total"], 2, 1), "-map", "0:v", "-map", "[aout]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{tl['total']:.2f}", str(out)])
    log_run("radio_cut", model="ffmpeg", latency_s=time.time() - started, params={"total_s": tl["total"]})
    print(f"  {out}  ({tl['total']:.0f}s)")
