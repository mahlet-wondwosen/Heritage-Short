"""Command line entry point:  python3 -m pipeline.cli <command> [--only s03]"""
from __future__ import annotations

import argparse

from pipeline import assemble, keyframes, music, narration, shots
from pipeline.common import load_storyboard

STAGES = ["narration", "keyframes", "shots", "music", "assemble"]


def validate() -> None:
    sb = load_storyboard()
    print(f"  storyboard.json is valid: {len(sb['shots'])} shots, formats {', '.join(sb['formats'])}")


def run_stage(name: str, only: str | None) -> None:
    print(f"[{name}]")
    {"validate": lambda: validate(),
     "narration": lambda: narration.run(only),
     "keyframes": lambda: keyframes.run(only),
     "shots": lambda: shots.run(only),
     "music": lambda: music.run(),
     "assemble": lambda: assemble.run(),
     "radio": lambda: assemble.radio_cut()}[name]()


def main() -> None:
    parser = argparse.ArgumentParser(description="Heritage Short pipeline")
    parser.add_argument("command", choices=["validate", "radio", "film", "music-brief", "costs", *STAGES])
    parser.add_argument("--only", help="regenerate just one shot, for example s03")
    args = parser.parse_args()
    if args.command == "music-brief":
        music.brief()
    elif args.command == "costs":
        from pipeline import costs
        costs.main()
    elif args.command == "film":
        for name in ["validate", *STAGES]:
            run_stage(name, args.only)
    elif args.command == "radio":
        for name in ["validate", "narration", "music", "radio"]:
            run_stage(name, args.only)
    else:
        run_stage(args.command, args.only)


if __name__ == "__main__":
    main()
