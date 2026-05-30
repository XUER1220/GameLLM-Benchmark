from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT_DIR / "prompts"
EVALUATION_RULES_DIR = ROOT_DIR / "evaluation"
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_SCORES_DIR = ROOT_DIR / "data" / "scores"
DEFAULT_WEIGHTS = ROOT_DIR / "config" / "weights.yaml"
