from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import visualize_results as single_run


ROOT_DIR = single_run.ROOT_DIR
SCORES_DIR = single_run.SCORES_DIR
FIGURES_DIR = single_run.FIGURES_DIR
REPEATED_PREFIX = "repeated_"


def _score_run_dirs() -> list[Path]:
    if not SCORES_DIR.exists():
        return []
    return sorted(
        [
            path
            for path in SCORES_DIR.iterdir()
            if path.is_dir()
            and not path.name.startswith(REPEATED_PREFIX)
            and (path / "summary.json").exists()
        ],
        key=lambda path: path.stat().st_mtime,
    )


def _resolve_summary(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = SCORES_DIR / path
    if path.is_dir():
        path = path / "summary.json"
    return path


def _summary_from_manifest_entry(entry: dict[str, Any]) -> Path | None:
    summary = str(entry.get("summary_path", "")).strip()
    if not summary:
        return None
    path = Path(summary)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path


def collect_summary_paths(args: argparse.Namespace) -> tuple[list[Path], str]:
    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            manifest_path = ROOT_DIR / manifest_path
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths = [
            path
            for item in data.get("runs", [])
            for path in [_summary_from_manifest_entry(item)]
            if path is not None
        ]
        return paths, manifest_path.parent.name

    if args.summaries:
        paths = []
        for value in args.summaries:
            path = Path(value)
            if not path.is_absolute():
                path = ROOT_DIR / path
            paths.append(path)
        return paths, "repeated_custom"

    if args.runs:
        return [_resolve_summary(value) for value in args.runs], "repeated_custom"

    latest = args.latest or 5
    runs = _score_run_dirs()
    if len(runs) < latest:
        raise FileNotFoundError(f"Only found {len(runs)} score runs under {SCORES_DIR}; need {latest}.")
    selected = runs[-latest:]
    return [path / "summary.json" for path in selected], f"repeated_latest_{latest}"


def load_repeated_results(summary_paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for repeat, summary_path in enumerate(summary_paths, start=1):
        results = single_run.load_results(summary_path)
        run_id = summary_path.parent.name
        for item in results:
            tagged = dict(item)
            tagged["repeat"] = repeat
            tagged["run_id"] = run_id
            tagged["source_summary"] = str(summary_path)
            tagged.setdefault("timestamp", run_id)
            records.append(tagged)
    return records


def plot_run_mean_trend(df: pd.DataFrame, out_dir: Path) -> None:
    if df["repeat"].nunique() < 2:
        return

    trend = (
        df.groupby(["repeat", "run_id", "model_short"], as_index=False)["total_score"]
        .mean()
        .sort_values(["repeat", "model_short"])
    )
    plt.figure(figsize=(9, 5))
    ax = sns.lineplot(
        data=trend,
        x="repeat",
        y="total_score",
        hue="model_short",
        marker="o",
        linewidth=2.2,
        errorbar=None,
        palette="Set2",
    )
    ax.set_title("Mean Score Across Repeats")
    ax.set_xlabel("Repeat")
    ax.set_ylabel("Mean Total Score")
    ax.set_ylim(0, 1)
    ax.legend(title="")
    single_run.save_figure(out_dir / "07_repeat_mean_score_trend.png")


def plot_model_score_distribution(df: pd.DataFrame, out_dir: Path) -> None:
    plt.figure(figsize=(9, 5))
    ax = sns.boxplot(
        data=df,
        x="model_short",
        y="total_score",
        hue="model_short",
        palette="Set2",
        legend=False,
    )
    sns.stripplot(
        data=df,
        x="model_short",
        y="total_score",
        color="0.25",
        alpha=0.35,
        size=3,
        jitter=0.22,
        ax=ax,
    )
    ax.set_title("Score Distribution Across Repeats")
    ax.set_xlabel("")
    ax.set_ylabel("Total Score")
    ax.set_ylim(0, 1)
    single_run.save_figure(out_dir / "08_repeat_score_distribution.png")


def plot_run_variability_heatmap(df: pd.DataFrame, out_dir: Path) -> None:
    if df["repeat"].nunique() < 2:
        return

    variability = df.pivot_table(
        index="game",
        columns="model_short",
        values="total_score",
        aggfunc="std",
    ).fillna(0.0)
    if variability.empty:
        return

    plt.figure(figsize=(9, max(4.5, len(variability) * 0.45)))
    ax = sns.heatmap(variability, annot=True, fmt=".3f", cmap="rocket_r", linewidths=0.5)
    ax.set_title("Run-to-Run Score Std. Dev.")
    ax.set_xlabel("")
    ax.set_ylabel("")
    single_run.save_figure(out_dir / "09_repeat_score_std_heatmap.png")


def export_combined_json(records: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "combined_summary.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate figures from multiple GameLLM-Benchmark score runs.")
    parser.add_argument("--latest", type=int, help="Use the latest N score runs. Defaults to 5.")
    parser.add_argument("--runs", nargs="+", help="Run directory names under data/scores.")
    parser.add_argument("--summaries", nargs="+", help="Direct paths to summary.json files.")
    parser.add_argument("--manifest", help="Manifest produced by scripts/run_repeated.py.")
    parser.add_argument("--out", help="Output directory. Defaults to analysis/figures/<batch-name>.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary_paths, batch_name = collect_summary_paths(args)
    if not summary_paths:
        raise FileNotFoundError("No summary.json files were selected.")

    missing = [path for path in summary_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing summary files: " + ", ".join(str(path) for path in missing))

    records = load_repeated_results(summary_paths)
    if not records:
        raise ValueError("Selected summaries did not contain result records.")

    out_dir = Path(args.out) if args.out else FIGURES_DIR / batch_name
    if not out_dir.is_absolute():
        out_dir = ROOT_DIR / out_dir

    single_run.setup_style()
    df, indicators = single_run.build_frames(records)
    if df.empty:
        raise ValueError("No rows could be built from selected summaries.")

    single_run.export_tables(df, indicators, out_dir)
    export_combined_json(records, out_dir)
    single_run.plot_overall_ranking(df, out_dir)
    single_run.plot_model_game_heatmap(df, out_dir)
    single_run.plot_dimension_profile(df, out_dir)
    single_run.plot_weighted_contributions(df, out_dir)
    single_run.plot_difficulty_trend(df, out_dir)
    single_run.plot_indicator_heatmaps(indicators, out_dir)
    plot_run_mean_trend(df, out_dir)
    plot_model_score_distribution(df, out_dir)
    plot_run_variability_heatmap(df, out_dir)

    print(f"Runs: {len(summary_paths)}")
    print(f"Records: {len(df)}")
    print(f"Models: {df['model_short'].nunique()}")
    print(f"Games: {df['game'].nunique()}")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
