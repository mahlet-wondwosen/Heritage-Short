"""Summarise runs.jsonl into a markdown table for COSTS.md: calls, cache hits and latency per stage."""
from __future__ import annotations

import json
from collections import defaultdict

from pipeline.common import RUNS_LOG


def main() -> None:
    if not RUNS_LOG.exists():
        raise SystemExit("runs.jsonl not found yet. Run some stages first.")
    stats = defaultdict(lambda: {"calls": 0, "cached": 0, "errors": 0, "seconds": 0.0})
    for line in RUNS_LOG.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        s = stats[(r["stage"], r["model"])]
        if r["cached"]:
            s["cached"] += 1
            continue
        s["calls"] += 1
        s["errors"] += r["status"] != "ok"
        s["seconds"] += r["latency_s"]
    print("| Stage | Model | Calls | Cache hits | Errors | Total seconds | Mean seconds |")
    print("|---|---|---|---|---|---|---|")
    for (stage, model), s in sorted(stats.items()):
        mean = s["seconds"] / s["calls"] if s["calls"] else 0
        print(f"| {stage} | {model} | {s['calls']} | {s['cached']} | {s['errors']} | {s['seconds']:.1f} | {mean:.1f} |")


if __name__ == "__main__":
    main()
