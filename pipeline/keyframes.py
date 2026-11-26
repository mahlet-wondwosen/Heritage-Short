"""Stage: keyframes. A reference sheet first, then one image per shot, from Cloudflare Workers AI (FLUX)."""
from __future__ import annotations

import base64
import os
import time

from pipeline.common import (OUT, digest, is_fresh, load_storyboard, log_run, mark_fresh, offline,
                             retry, selected)

DIR = OUT / "keyframes"
MODEL = os.environ.get("CF_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell")
STEPS = int(os.environ.get("CF_STEPS", "4"))


def image_path(shot_id: str):
    return DIR / f"{shot_id}.jpg"


def build_prompt(sb: dict, text: str, with_character: bool) -> str:
    """Style block + (character) + shot prompt. FLUX has no negative prompt, so avoidances are written in."""
    parts = [sb["style_block"]]
    if with_character:
        parts.append(sb["character"]["description"])
    parts.append(text)
    if sb.get("negative_block"):
        parts.append("Avoid: " + sb["negative_block"] + ".")
    return " ".join(parts)


@retry()
def generate(prompt: str) -> bytes:
    import requests

    account = os.environ["CLOUDFLARE_ACCOUNT_ID"]
    token = os.environ["CLOUDFLARE_API_TOKEN"]
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{MODEL}"
    response = requests.post(url, headers={"Authorization": f"Bearer {token}"},
                             json={"prompt": prompt, "steps": STEPS}, timeout=120)
    response.raise_for_status()
    return base64.b64decode(response.json()["result"]["image"])


def placeholder(path, label: str) -> None:
    """A plain test image so the rest of the pipeline can be checked without an API key."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (1024, 1024), (96, 70, 50))
    draw = ImageDraw.Draw(img)
    draw.ellipse((262, 262, 762, 762), fill=(150, 110, 70))
    draw.text((460, 500), label, fill=(240, 230, 210))
    img.save(path, "JPEG")


def run(only: str | None = None) -> None:
    sb = load_storyboard()
    DIR.mkdir(parents=True, exist_ok=True)
    model = "offline-placeholder" if offline() else MODEL
    jobs = [("reference", DIR / "reference_sheet.jpg", 0,
             "Character reference sheet: three views of the same figure side by side, from behind, in profile "
             "and in silhouette, plain neutral background.", True)]
    for shot in sb["shots"]:
        jobs.append((shot["id"], image_path(shot["id"]), shot["seed"], shot["image_prompt"],
                     shot.get("shows_character", False)))
    for name, out, seed, text, with_character in jobs:
        if only and name != only:
            continue
        prompt = build_prompt(sb, text, with_character)
        key = digest(prompt, model, STEPS, seed)
        if is_fresh(out, key):
            log_run("keyframes", shot=name, model=model, cached=True)
            print(f"  {name} keyframe: cached")
            continue
        started = time.time()
        try:
            if offline():
                placeholder(out, name)
            else:
                out.write_bytes(generate(prompt))
            mark_fresh(out, key)
            log_run("keyframes", shot=name, model=model, params={"steps": STEPS, "prompt": prompt}, seed=seed,
                    latency_s=time.time() - started, note="offline placeholder" if offline() else "")
            print(f"  {name} keyframe: done in {time.time() - started:.1f}s")
        except Exception as exc:  # noqa: BLE001
            log_run("keyframes", shot=name, model=model, seed=seed, status="error",
                    latency_s=time.time() - started, error=str(exc)[:300])
            raise SystemExit(f"Keyframe failed for {name}: {exc}")
