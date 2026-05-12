from __future__ import annotations

from pathlib import Path

from shared.paths import PROJECT_ROOT


SENIOR_THESIS_DIR = PROJECT_ROOT / "senior_thesis"
SENIOR_THESIS_OUTPUTS_DIR = SENIOR_THESIS_DIR / "outputs"

DEFAULT_ABM_SUMMARY = (
    PROJECT_ROOT.parent
    / "Opinion_ABM"
    / "outputs"
    / "leader_effects_main"
    / "summary"
    / "summary_results.csv"
)

EMPIRICAL_LABEL_TARGETS_CSV = SENIOR_THESIS_OUTPUTS_DIR / "empirical_label_targets.csv"
LEADER_GROUP_TARGETS_CSV = SENIOR_THESIS_OUTPUTS_DIR / "leader_group_targets.csv"
ABM_EMPIRICAL_COMPARISON_CSV = SENIOR_THESIS_OUTPUTS_DIR / "abm_empirical_comparison.csv"

LEADER_TOP_SHARES = [0.01, 0.03, 0.05, 0.10]
LEADER_IN_DEGREE_THRESHOLDS = [70, 100, 150, 250]


def ensure_outputs_dir() -> Path:
    SENIOR_THESIS_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return SENIOR_THESIS_OUTPUTS_DIR

