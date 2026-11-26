"""Stage: narration. One WAV file per shot from Gemini TTS (or a silent placeholder if OFFLINE=1)."""
from __future__ import annotations

import os
import time
import wave

from pipeline.common import (OUT, digest, is_fresh, load_storyboard, log_run, mark_fresh, offline,
                             retry, selected)

DIR = OUT / "narration"
SAMPLE_RATE = 24000  # Gemini TTS returns 24 kHz, 16-bit, mono PCM
TTS_MODEL = os.environ.get("TTS_MODEL", "gemini-2.5-flash-preview-tts")
TTS_VOICE = os.environ.get("TTS_VOICE", "Kore")


def wav_path(shot_id: str):
    return DIR / f"{shot_id}.wav"


def duration_s(path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def write_wav(path, pcm: bytes) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)


@retry()
def synthesize(text: str, style: str) -> bytes:
    """Call Gemini TTS and return raw PCM bytes."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=TTS_MODEL,
        contents=f"{style}: {text}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=TTS_VOICE)
                )
            ),
        ),
    )
    return response.candidates[0].content.parts[0].inline_data.data


def run(only: str | None = None) -> None:
    sb = load_storyboard()
    DIR.mkdir(parents=True, exist_ok=True)
    style = sb["language"]["tts_voice_style"]
    for shot in selected(sb["shots"], only):
        text = shot["narration"]["text_native"]
        model = "offline-placeholder" if offline() else TTS_MODEL
        key = digest(text, style, model, TTS_VOICE)
        out = wav_path(shot["id"])
        if is_fresh(out, key):
            log_run("narration", shot=shot["id"], model=model, cached=True)
            print(f"  {shot['id']} narration: cached")
            continue
        started = time.time()
        try:
            if offline():
                # silent placeholder, about 0.45 s per word, so timing can be tested without a key
                pcm = b"\x00\x00" * int(SAMPLE_RATE * 0.45 * max(1, len(text.split())))
            else:
                pcm = synthesize(text, style)
            write_wav(out, pcm)
            mark_fresh(out, key)
            log_run("narration", shot=shot["id"], model=model, params={"voice": TTS_VOICE, "style": style},
                    latency_s=time.time() - started, note="offline placeholder (silent)" if offline() else "")
            print(f"  {shot['id']} narration: {duration_s(out):.1f}s")
        except Exception as exc:  # noqa: BLE001
            log_run("narration", shot=shot["id"], model=model, status="error",
                    latency_s=time.time() - started, error=str(exc)[:300])
            raise SystemExit(f"Narration failed for {shot['id']}: {exc}")
