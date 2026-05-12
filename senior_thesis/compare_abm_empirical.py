from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from senior_thesis import config
from senior_thesis.empirical_targets import run as build_empirical_targets


def _load_or_build_empirical() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not config.EMPIRICAL_LABEL_TARGETS_CSV.exists() or not config.LEADER_GROUP_TARGETS_CSV.exists():
        outputs = build_empirical_targets()
        return outputs["overall"], outputs["leader_targets"]
    overall = pd.read_csv(config.EMPIRICAL_LABEL_TARGETS_CSV, keep_default_na=False)
    leader_targets = pd.read_csv(config.LEADER_GROUP_TARGETS_CSV, keep_default_na=False)
    return overall, leader_targets


def _normalized_content_balance(row: pd.Series) -> float:
    support = float(row.get("support_posts_mean", 0.0))
    oppose = float(row.get("oppose_posts_mean", 0.0))
    total = support + oppose
    return (support - oppose) / total if total else 0.0


def _leader_rule_for_share(share: float) -> str:
    pct = int(round(float(share) * 100))
    return f"top_{pct}pct_by_in_degree"


def build_comparison(abm_summary_path: str | Path = config.DEFAULT_ABM_SUMMARY) -> pd.DataFrame:
    abm_path = Path(abm_summary_path)
    if not abm_path.exists():
        raise FileNotFoundError(f"Cannot find ABM summary: {abm_path}")

    overall, leader_targets = _load_or_build_empirical()
    empirical_all_balance = float(overall.iloc[0]["balance_share"])
    leader_targets = leader_targets.set_index("leader_rule", drop=False)

    abm = pd.read_csv(abm_path, keep_default_na=False)
    rows = []
    for _, row in abm.iterrows():
        leader_rule = _leader_rule_for_share(float(row["leader_share"]))
        leader_balance = (
            float(leader_targets.at[leader_rule, "leader_balance_share"])
            if leader_rule in leader_targets.index
            else float("nan")
        )
        content_balance_norm = _normalized_content_balance(row)
        final_mean_opinion = float(row.get("final_mean_opinion_mean", 0.0))
        rows.append(
            {
                "N": int(row["N"]),
                "topology": row["topology"],
                "leader_share": float(row["leader_share"]),
                "leader_mode": row["leader_mode"],
                "T_rounds": int(row["T_rounds"]),
                "empirical_all_balance_share": empirical_all_balance,
                "empirical_leader_rule": leader_rule,
                "empirical_leader_balance_share": leader_balance,
                "abm_final_mean_opinion": final_mean_opinion,
                "abm_content_balance_norm": content_balance_norm,
                "distance_final_opinion_to_all": abs(final_mean_opinion - empirical_all_balance),
                "distance_content_balance_to_all": abs(content_balance_norm - empirical_all_balance),
                "distance_final_opinion_to_leaders": abs(final_mean_opinion - leader_balance),
                "distance_content_balance_to_leaders": abs(content_balance_norm - leader_balance),
                "all_direction_match": (final_mean_opinion >= 0) == (empirical_all_balance >= 0),
                "leader_direction_match": (final_mean_opinion >= 0) == (leader_balance >= 0),
                "final_mean_abs_opinion_mean": float(row.get("final_mean_abs_opinion_mean", 0.0)),
                "extremist_ratio_mean": float(row.get("extremist_ratio_mean", 0.0)),
                "homophily_ratio_mean": float(row.get("homophily_ratio_mean", 0.0)),
            }
        )

    comparison = pd.DataFrame(rows)
    return comparison.sort_values(
        ["distance_final_opinion_to_all", "distance_content_balance_to_all", "N", "topology"]
    ).reset_index(drop=True)


def run() -> pd.DataFrame:
    config.ensure_outputs_dir()
    comparison = build_comparison()
    comparison.to_csv(config.ABM_EMPIRICAL_COMPARISON_CSV, index=False, encoding="utf-8-sig")
    return comparison


def main() -> None:
    comparison = run()
    print(comparison.head(10).to_string(index=False))
    print(f"comparison_rows: {len(comparison)}")
    print(f"output: {config.ABM_EMPIRICAL_COMPARISON_CSV}")


if __name__ == "__main__":
    main()

