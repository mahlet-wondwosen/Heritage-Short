"""Shared helpers: storyboard loading and validation, hashing/caching, retries, call logging."""
from __future__ import annotations

import functools
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORYBOARD = ROOT / "storyboard.json"
SCHEMA = ROOT / "schema" / "storyboard.schema.json"
OUT = ROOT / "outputs"
RUNS_LOG = ROOT / "runs.jsonl"

MAX_ATTEMPTS = 3  # per call, then the stage's fallback or a clear error


def load_env() -> None:
    """Read KEY=VALUE lines from .env into os.environ (without overriding real variables)."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()


def offline() -> bool:
    return os.environ.get("OFFLINE", "") == "1"


def load_storyboard() -> dict:
    """Load storyboard.json and validate it against the JSON Schema. Raises on any error."""
    import jsonschema

    data = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(data)
    ids = [s["id"] for s in data["shots"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate shot ids in storyboard.json")
    known = set(ids)
    for cue in data["music"]["cues"]:
        for key in ("from_shot", "to_shot"):
            if cue[key] not in known:
                raise ValueError(f"music cue {cue['id']} points to unknown shot {cue[key]}")
    return data


def digest(*parts: object) -> str:
    """A short stable hash of any JSON-serialisable inputs."""
    blob = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def is_fresh(output: Path, key: str) -> bool:
    """True when the output exists and was made from inputs with this hash."""
    stamp = output.with_suffix(output.suffix + ".hash")
    return output.exists() and stamp.exists() and stamp.read_text().strip() == key


def mark_fresh(output: Path, key: str) -> None:
    output.with_suffix(output.suffix + ".hash").write_text(key)


def log_run(stage: str, *, shot: str | None = None, model: str = "", params: dict | None = None,
            seed: int | None = None, latency_s: float = 0.0, cost_usd: float = 0.0,
            status: str = "ok", cached: bool = False, error: str = "", note: str = "") -> None:
    """Append one line to runs.jsonl. Never put secrets in params."""
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "stage": stage, "shot": shot, "model": model, "params": params or {}, "seed": seed,
        "latency_s": round(latency_s, 3), "cost_usd": cost_usd, "status": status,
        "cached": cached, "error": error, "note": note,
    }
    with RUNS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def retry(attempts: int = MAX_ATTEMPTS, base_delay: float = 2.0):
    """Retry a function with exponential backoff. The last error is re-raised."""
    def wrap(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            last = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001 - we log and re-raise the last one
                    last = exc
                    if i < attempts - 1:
                        time.sleep(base_delay * (2 ** i))
            raise last
        return inner
    return wrap


def ffmpeg_exe() -> str:
    """The ffmpeg binary: the system one, or the one that ships with imageio-ffmpeg."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("ffmpeg not found. Run: pip install imageio-ffmpeg") from exc


def run_ffmpeg(args: list[str]) -> None:
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()[:800]}")


def selected(shots: list[dict], only: str | None) -> list[dict]:
    """All shots, or just the one named by --only."""
    if not only:
        return shots
    chosen = [s for s in shots if s["id"] == only]
    if not chosen:
        raise SystemExit(f"No shot called {only}. Shots: {', '.join(s['id'] for s in shots)}")
    return chosen
