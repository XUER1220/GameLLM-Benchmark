from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
SCORES_DIR = ROOT_DIR / "data" / "scores"
REPEATED_PREFIX = "repeated_"


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def _existing_score_runs() -> dict[str, Path]:
    if not SCORES_DIR.exists():
        return {}

    runs: dict[str, Path] = {}
    for path in SCORES_DIR.iterdir():
        if not path.is_dir() or path.name.startswith(REPEATED_PREFIX):
            continue
        if (path / "summary.json").exists():
            runs[path.name] = path
    return runs


def _detect_new_run(before: dict[str, Path], after: dict[str, Path]) -> Path | None:
    created = [path for name, path in after.items() if name not in before]
    if not created:
        return None
    return max(created, key=lambda path: path.stat().st_mtime)


def run_once(index: int, python_exe: str) -> dict[str, Any]:
    before = _existing_score_runs()
    command = [python_exe, str(ROOT_DIR / "run_pipeline.py")]

    print(f"\n=== Repeat {index}: running {' '.join(command)} ===", flush=True)
    completed = subprocess.run(command, cwd=ROOT_DIR)

    after = _existing_score_runs()
    run_dir = _detect_new_run(before, after)
    summary_path = run_dir / "summary.json" if run_dir else None

    result: dict[str, Any] = {
        "repeat": index,
        "returncode": completed.returncode,
        "scores_dir": _relative(run_dir) if run_dir else "",
        "summary_path": _relative(summary_path) if summary_path else "",
    }
    if run_dir:
        result["run_id"] = run_dir.name
        print(f"Repeat {index} scores: {run_dir}", flush=True)
    else:
        result["run_id"] = ""
        print(f"Repeat {index} did not create a new summary.json", flush=True)
    return result


def write_manifest(manifest_dir: Path, manifest: dict[str, Any]) -> Path:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run run_pipeline.py repeatedly and record score directories.")
    parser.add_argument("--times", type=int, default=5, help="Number of complete pipeline runs. Defaults to 5.")
    parser.add_argument("--python", default=sys.executable, help="Python executable used to run run_pipeline.py.")
    parser.add_argument("--sleep-seconds", type=float, default=1.0, help="Delay between repeats.")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop after the first non-zero pipeline exit.")
    parser.add_argument("--plot", action="store_true", help="Generate repeated-result figures after all runs finish.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.times < 1:
        raise ValueError("--times must be at least 1")

    batch_id = datetime.now().strftime(f"{REPEATED_PREFIX}%Y%m%d_%H%M%S")
    manifest_dir = SCORES_DIR / batch_id
    runs: list[dict[str, Any]] = []

    for index in range(1, args.times + 1):
        result = run_once(index, args.python)
        runs.append(result)
        if args.stop_on_fail and result["returncode"] != 0:
            break
        if index < args.times and args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    manifest = {
        "batch_id": batch_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "times_requested": args.times,
        "runs": runs,
    }
    manifest_path = write_manifest(manifest_dir, manifest)

    print(f"\nManifest: {manifest_path}")
    print(f"Successful summaries: {sum(1 for item in runs if item.get('summary_path'))}/{len(runs)}")

    if args.plot:
        command = [
            args.python,
            str(ROOT_DIR / "scripts" / "visualize_repeated_results.py"),
            "--manifest",
            str(manifest_path),
        ]
        print(f"\n=== Plotting repeated results: {' '.join(command)} ===", flush=True)
        completed = subprocess.run(command, cwd=ROOT_DIR)
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
