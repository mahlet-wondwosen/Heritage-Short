"""Timing: how long each shot lasts. Narration sets the length, the storyboard sets the minimum."""
from __future__ import annotations

import re

from pipeline import narration

NARRATION_DELAY_S = 0.2   # narration starts a moment after the cut
TAIL_S = 0.2              # breathing room after the last word


def plan(sb: dict) -> dict:
    """Start time, length and narration timing for every shot, plus the total length."""
    items, t = [], 0.0
    for shot in sb["shots"]:
        wav = narration.wav_path(shot["id"])
        narr = narration.duration_s(wav) if wav.exists() else 0.0
        length = shot["duration_s"]
        if narr:
            length = max(length, NARRATION_DELAY_S + narr + TAIL_S)
        items.append({"id": shot["id"], "start": round(t, 3), "length": round(length, 3),
                      "narr_start": round(t + NARRATION_DELAY_S, 3), "narr_dur": round(narr, 3)})
        t += length
    end = sb["end_card"]["duration_s"]
    return {"shots": items, "end_card_start": round(t, 3), "end_card_length": end, "total": round(t + end, 3)}


def split_subtitle(text: str, max_chars: int = 40) -> list[str]:
    """Break narration text into chunks that fit two lines of about 40 characters."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?:;])\s+", text.strip()) if s.strip()]
    chunks: list[str] = []
    for sentence in sentences:
        if len(sentence) <= max_chars * 2:
            chunks.append(sentence)
            continue
        words, current = sentence.split(), ""
        for word in words:
            if len(current) + len(word) + 1 > max_chars * 2:
                chunks.append(current.strip())
                current = word
            else:
                current = f"{current} {word}"
        if current.strip():
            chunks.append(current.strip())
    return chunks


def subtitle_cues(sb: dict, tl: dict) -> list[dict]:
    """Timed English subtitle cues, spread over each shot's narration in proportion to text length."""
    cues = []
    for shot, item in zip(sb["shots"], tl["shots"]):
        chunks = split_subtitle(shot["narration"]["text_en"])
        span = max(item["narr_dur"], 1.0) + 0.3
        total_chars = sum(len(c) for c in chunks) or 1
        cursor = item["narr_start"]
        for chunk in chunks:
            share = span * len(chunk) / total_chars
            cues.append({"shot": shot["id"], "start": round(cursor, 3), "end": round(cursor + share, 3), "text": chunk})
            cursor += share
    return cues
