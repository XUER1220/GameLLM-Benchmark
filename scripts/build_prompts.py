from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

import yaml

ROOT_DIR_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_DIR_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR_FOR_IMPORTS))

from prompt_builder import ROOT_DIR, build_prompt, generated_prompt_path


GAMES_CONFIG = ROOT_DIR / "config" / "games.yaml"


def load_enabled_games() -> list[tuple[str, str]]:
    config = yaml.safe_load(GAMES_CONFIG.read_text(encoding="utf-8"))
    return [
        (difficulty, game)
        for difficulty, games in config["games"].items()
        for game in games
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build generated prompt.txt files from prompt sources.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="only check that generated prompt.txt files are up to date",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    errors: list[str] = []

    for difficulty, game in load_enabled_games():
        built = build_prompt(difficulty, game)
        path = generated_prompt_path(difficulty, game)
        existing = path.read_text(encoding="utf-8") if path.exists() else None

        if args.check:
            if existing != built:
                errors.append(f"{path.relative_to(ROOT_DIR)} is not up to date")
                if existing is not None:
                    diff = difflib.unified_diff(
                        existing.splitlines(),
                        built.splitlines(),
                        fromfile=f"{path.relative_to(ROOT_DIR)}",
                        tofile="generated",
                        lineterm="",
                    )
                    errors.extend(f"  {line}" for line in list(diff)[:80])
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(built, encoding="utf-8")
        print(f"built {path.relative_to(ROOT_DIR)}")

    if errors:
        print("Prompt build check failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    if args.check:
        print("Prompt build check passed")


if __name__ == "__main__":
    main()
