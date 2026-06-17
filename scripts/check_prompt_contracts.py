from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from prompt_builder import REQUIRED_SECTIONS, PromptBuildError, build_prompt, generated_prompt_path

PROMPTS_DIR = ROOT_DIR / "prompts"
GAMES_CONFIG = ROOT_DIR / "config" / "games.yaml"

REQUIRED_SNIPPETS = (
    "800x600",
    "60 FPS",
    "random.seed(42)",
    "`R`",
    "`ESC`",
    "最终只输出代码",
)

FORBIDDEN_VAGUE_TERMS = (
    "附近",
    "大约",
    "合理范围",
    "建议",
    "适当",
    "少量",
    "低频",
)

EXPECTED_MAP_SHAPES = {
    ("medium", "pacman"): ((21, 19),),
    ("hard", "roguelike_dungeon"): ((15, 21), (15, 21)),
}


def load_enabled_games() -> list[tuple[str, str]]:
    config = yaml.safe_load(GAMES_CONFIG.read_text(encoding="utf-8"))
    return [
        (difficulty, game)
        for difficulty, games in config["games"].items()
        for game in games
    ]


def extract_map_blocks(text: str) -> list[list[str]]:
    blocks = re.findall(r"```\r?\n(.*?)```", text, flags=re.DOTALL)
    return [
        [line for line in block.splitlines() if line]
        for block in blocks
    ]


def validate_prompt(difficulty: str, game: str) -> list[str]:
    prompt_path = generated_prompt_path(difficulty, game)
    if not prompt_path.exists():
        return [f"missing prompt: {prompt_path.relative_to(ROOT_DIR)}"]

    try:
        text = build_prompt(difficulty, game)
    except PromptBuildError as exc:
        return [f"{prompt_path.relative_to(ROOT_DIR)}: failed to build prompt: {exc}"]
    errors: list[str] = []

    generated_text = prompt_path.read_text(encoding="utf-8")
    if generated_text != text:
        errors.append(f"{prompt_path.relative_to(ROOT_DIR)} is not up to date; run `python scripts/build_prompts.py`")

    for section in REQUIRED_SECTIONS:
        if text.count(section) != 1:
            errors.append(f"{prompt_path.relative_to(ROOT_DIR)}: section `{section}` must appear exactly once")

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            errors.append(f"{prompt_path.relative_to(ROOT_DIR)}: missing `{snippet}`")

    for term in FORBIDDEN_VAGUE_TERMS:
        if term in text:
            errors.append(f"{prompt_path.relative_to(ROOT_DIR)}: forbidden vague term `{term}`")

    expected_shapes = EXPECTED_MAP_SHAPES.get((difficulty, game), ())
    if expected_shapes:
        blocks = extract_map_blocks(text)
        if len(blocks) != len(expected_shapes):
            errors.append(
                f"{prompt_path.relative_to(ROOT_DIR)}: expected {len(expected_shapes)} fixed map block(s), got {len(blocks)}"
            )
        for index, ((rows, columns), block) in enumerate(zip(expected_shapes, blocks), start=1):
            if len(block) != rows:
                errors.append(
                    f"{prompt_path.relative_to(ROOT_DIR)}: map {index} expected {rows} rows, got {len(block)}"
                )
            bad_rows = [
                row_index
                for row_index, row in enumerate(block, start=1)
                if len(row) != columns
            ]
            if bad_rows:
                errors.append(
                    f"{prompt_path.relative_to(ROOT_DIR)}: map {index} rows {bad_rows} are not {columns} columns wide"
                )

    return errors


def main() -> None:
    games = load_enabled_games()
    errors = [
        error
        for difficulty, game in games
        for error in validate_prompt(difficulty, game)
    ]

    prompt_paths = list(PROMPTS_DIR.glob("*/*/prompt.txt"))
    if len(prompt_paths) != len(games):
        errors.append(
            f"enabled game count is {len(games)}, but prompt file count is {len(prompt_paths)}"
        )

    if errors:
        print("Prompt contract check failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Prompt contract check passed: {len(games)} enabled prompts")


if __name__ == "__main__":
    main()
