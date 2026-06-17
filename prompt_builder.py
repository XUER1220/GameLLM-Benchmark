from __future__ import annotations

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT_DIR / "prompts"
MAIN_TEMPLATE = PROMPTS_DIR / "main.md"
SPECS_DIR = PROMPTS_DIR / "specs"

REQUIRED_SECTIONS = (
    "任务身份",
    "输出契约",
    "坐标与时间",
    "颜色表",
    "布局与实体",
    "输入",
    "更新顺序",
    "独特规则",
    "计分与终止",
    "绘制顺序与 HUD",
    "禁止项",
    "提交前检查",
)

SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_PATTERN = re.compile(r"\[([A-Z][A-Z0-9_]*)\]")

PLACEHOLDER_SECTIONS = {
    "TASK_IDENTITY": "任务身份",
    "GAME_COORDINATES": "坐标与时间",
    "COLOR_TABLE": "颜色表",
    "LAYOUT_ENTITIES": "布局与实体",
    "INPUT_RULES": "输入",
    "UPDATE_ORDER": "更新顺序",
    "DISTINCTIVE_RULES": "独特规则",
    "SCORING_TERMINATION": "计分与终止",
    "DRAWING_HUD": "绘制顺序与 HUD",
    "GAME_FORBIDDEN_ITEMS": "禁止项",
    "GAME_PREFLIGHT_CHECK": "提交前检查",
}


class PromptBuildError(ValueError):
    """Raised when prompt source files cannot produce a complete prompt."""


def build_prompt(difficulty: str, game: str) -> str:
    """Build the full prompt sent to the model from the [] placeholder template."""
    template = _load_main_template()
    spec_path = SPECS_DIR / difficulty / f"{game}.md"
    sections = _parse_section_file(spec_path)

    _validate_spec_sections(sections, difficulty, game)
    _validate_template_placeholders(template)

    replacements = {
        placeholder: sections[section_name].strip()
        for placeholder, section_name in PLACEHOLDER_SECTIONS.items()
    }
    prompt = PLACEHOLDER_PATTERN.sub(lambda match: replacements[match.group(1)], template)
    _validate_rendered_prompt(prompt, difficulty, game)

    return prompt.rstrip() + "\n"


def generated_prompt_path(difficulty: str, game: str) -> Path:
    return PROMPTS_DIR / difficulty / game / "prompt.txt"


def _load_main_template() -> str:
    if not MAIN_TEMPLATE.exists():
        raise PromptBuildError(f"missing prompt main template: {_rel(MAIN_TEMPLATE)}")
    return MAIN_TEMPLATE.read_text(encoding="utf-8").strip()


def _parse_section_file(path: Path) -> dict[str, str]:
    if not path.exists():
        raise PromptBuildError(f"missing prompt source: {_rel(path)}")

    text = path.read_text(encoding="utf-8").strip()
    matches = list(SECTION_PATTERN.finditer(text))
    if not matches:
        raise PromptBuildError(f"{_rel(path)} must contain one or more `## section` headings")

    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        name = match.group(1).strip()
        if name in sections:
            raise PromptBuildError(f"{_rel(path)} defines section `{name}` more than once")
        if name not in REQUIRED_SECTIONS:
            raise PromptBuildError(f"{_rel(path)} defines unknown section `{name}`")

        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if not body:
            raise PromptBuildError(f"{_rel(path)} section `{name}` is empty")
        sections[name] = body

    return sections


def _validate_spec_sections(
    sections: dict[str, str],
    difficulty: str,
    game: str,
) -> None:
    required_spec_sections = tuple(PLACEHOLDER_SECTIONS.values())
    missing = [name for name in required_spec_sections if name not in sections or not sections[name]]
    if missing:
        joined = ", ".join(missing)
        raise PromptBuildError(f"{difficulty}/{game} prompt is missing section(s): {joined}")

    extra = [name for name in sections if name not in set(required_spec_sections)]
    if extra:
        joined = ", ".join(extra)
        raise PromptBuildError(f"{difficulty}/{game} prompt has unexpected section(s): {joined}")


def _validate_template_placeholders(template: str) -> None:
    placeholders = PLACEHOLDER_PATTERN.findall(template)
    seen = set(placeholders)
    expected = set(PLACEHOLDER_SECTIONS)

    unknown = sorted(seen - expected)
    if unknown:
        joined = ", ".join(f"[{name}]" for name in unknown)
        raise PromptBuildError(f"{_rel(MAIN_TEMPLATE)} contains unknown placeholder(s): {joined}")

    missing = sorted(expected - seen)
    if missing:
        joined = ", ".join(f"[{name}]" for name in missing)
        raise PromptBuildError(f"{_rel(MAIN_TEMPLATE)} is missing placeholder(s): {joined}")

    duplicates = sorted(name for name in expected if placeholders.count(name) != 1)
    if duplicates:
        joined = ", ".join(f"[{name}]" for name in duplicates)
        raise PromptBuildError(f"{_rel(MAIN_TEMPLATE)} placeholders must appear exactly once: {joined}")


def _validate_rendered_prompt(prompt: str, difficulty: str, game: str) -> None:
    leftovers = sorted(set(PLACEHOLDER_PATTERN.findall(prompt)))
    if leftovers:
        joined = ", ".join(f"[{name}]" for name in leftovers)
        raise PromptBuildError(f"{difficulty}/{game} rendered prompt has unresolved placeholder(s): {joined}")

    if "{{section:" in prompt:
        raise PromptBuildError(f"{difficulty}/{game} rendered prompt still contains old section template syntax")

    for section in REQUIRED_SECTIONS:
        count = len(re.findall(rf"^{re.escape(section)}\s*$", prompt, flags=re.MULTILINE))
        if count != 1:
            raise PromptBuildError(
                f"{difficulty}/{game} rendered prompt section `{section}` must appear exactly once, got {count}"
            )


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)
