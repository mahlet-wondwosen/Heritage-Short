"""Stage: moving shots. Uses a supplied Wan clip (outputs/clips/sXX.mp4) if present, else a Ken Burns move."""
from __future__ import annotations

import hashlib
import os
import time

from pipeline.common import (OUT, digest, is_fresh, load_storyboard, log_run, mark_fresh, run_ffmpeg,
                             selected)
from pipeline.keyframes import image_path
from pipeline.timeline import plan

DIR = OUT / "shots"
CLIPS = OUT / "clips"
FPS = 24
FORMATS = {"9:16": ("9x16", 1080, 1920), "16:9": ("16x9", 1920, 1080)}


def size_for(fmt: str) -> tuple[str, int, int]:
    tag, w, h = FORMATS[fmt]
    if os.environ.get("DRAFT", "") == "1":  # half size for quick checks
        return tag, w // 2, h // 2
    return tag, w, h


def file_hash(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else "none"


def motion_expressions(camera: str, frames: int) -> tuple[str, str, str]:
    """zoompan expressions (zoom, x, y) for a camera move. No commas, so they need no escaping."""
    centre_x, centre_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    p = f"on/{frames}"
    if camera in ("push_in", "orbit"):
        return f"1+0.18*{p}", centre_x, centre_y
    if camera == "pull_out":
        return f"1.18-0.18*{p}", centre_x, centre_y
    if camera == "pan_right":
        return "1.2", f"(iw-iw/zoom)*{p}", centre_y
    if camera == "pan_left":
        return "1.2", f"(iw-iw/zoom)*(1-{p})", centre_y
    if camera == "tilt_up":
        return "1.2", centre_x, f"(ih-ih/zoom)*(1-{p})"
    if camera == "tilt_down":
        return "1.2", centre_x, f"(ih-ih/zoom)*{p}"
    return "1.04", centre_x, centre_y  # static: a barely visible drift


def ken_burns(image, out, camera: str, seconds: float, w: int, h: int) -> None:
    frames = int(round(seconds * FPS))
    z, x, y = motion_expressions(camera, frames)
    big_w, big_h = int(w * 1.25) // 2 * 2, int(h * 1.25) // 2 * 2
    # centre-crop the square keyframe to the target shape, enlarge it for smooth motion, then move over it
    if h > w:
        crop = "crop=floor(ih*{}/{}/2)*2:ih".format(w, h)
    else:
        crop = "crop=iw:floor(iw*{}/{}/2)*2".format(h, w)
    vf = (f"{crop},scale={big_w}:{big_h}:flags=lanczos,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={FPS},format=yuv420p")
    run_ffmpeg(["-i", str(image), "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "18", "-r", str(FPS), "-pix_fmt", "yuv420p", str(out)])


def from_clip(clip, out, seconds: float, w: int, h: int) -> None:
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS},"
          f"tpad=stop_mode=clone:stop_duration={seconds:.2f},format=yuv420p")
    run_ffmpeg(["-i", str(clip), "-vf", vf, "-t", f"{seconds:.3f}", "-an", "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(out)])


def run(only: str | None = None) -> None:
    sb = load_storyboard()
    DIR.mkdir(parents=True, exist_ok=True)
    tl = plan(sb)
    lengths = {item["id"]: item["length"] for item in tl["shots"]}
    for shot in selected(sb["shots"], only):
        sid, seconds = shot["id"], lengths[shot["id"]]
        image = image_path(sid)
        clip = CLIPS / f"{sid}.mp4"
        if not image.exists() and not clip.exists():
            raise SystemExit(f"No keyframe for {sid}. Run the keyframes stage first.")
        source = "wan-clip" if clip.exists() else "ken-burns"
        for fmt in sb["formats"]:
            tag, w, h = size_for(fmt)
            out = DIR / f"{sid}_{tag}.mp4"
            key = digest(source, file_hash(image), file_hash(clip), shot["camera"], round(seconds, 2), w, h)
            if is_fresh(out, key):
                log_run("shots", shot=sid, model=source, cached=True, params={"format": fmt})
                print(f"  {sid} {tag}: cached")
                continue
            started = time.time()
            try:
                if clip.exists():
                    from_clip(clip, out, seconds, w, h)
                else:
                    ken_burns(image, out, shot["camera"], seconds, w, h)
                mark_fresh(out, key)
                log_run("shots", shot=sid, model=source, seed=shot["seed"], latency_s=time.time() - started,
                        params={"format": fmt, "camera": shot["camera"], "seconds": round(seconds, 2)})
                print(f"  {sid} {tag}: {source} {seconds:.1f}s")
            except Exception as exc:  # noqa: BLE001
                log_run("shots", shot=sid, model=source, status="error", error=str(exc)[:300])
                raise SystemExit(f"Shot {sid} failed: {exc}")
