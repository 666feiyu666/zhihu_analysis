from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from labeling import config as labeling_config
from network import config as network_config
from senior_thesis import config


def _is_true(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def load_full_labels(path: str | Path = labeling_config.FULL_LABELS_CSV) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find full labels: {path}. Run: python labeling/label_sample.py --mode full"
        )
    labels = pd.read_csv(path, keep_default_na=False)
    invalid = sorted(set(labels["label"]) - {"optimistic", "pessimistic"})
    if invalid:
        raise ValueError(f"Unexpected labels in {path}: {invalid}")
    return labels


def load_author_metrics(path: str | Path = network_config.NODE_METRICS_CSV) -> pd.DataFrame:
    nodes = pd.read_csv(path, keep_default_na=False)
    authors = nodes[_is_true(nodes["is_answer_author"])].copy()
    authors["in_degree"] = pd.to_numeric(authors["in_degree"])
    authors["pagerank"] = pd.to_numeric(authors["pagerank"])
    return authors


def label_balance(labels: pd.DataFrame) -> dict:
    counts = labels["label"].value_counts()
    total = int(counts.sum())
    optimistic = int(counts.get("optimistic", 0))
    pessimistic = int(counts.get("pessimistic", 0))
    balance = optimistic - pessimistic
    return {
        "answer_count": total,
        "optimistic_count": optimistic,
        "pessimistic_count": pessimistic,
        "optimistic_share": optimistic / total if total else 0.0,
        "pessimistic_share": pessimistic / total if total else 0.0,
        "balance": balance,
        "balance_share": balance / total if total else 0.0,
        "mean_confidence": float(labels["confidence"].mean()) if total and "confidence" in labels else float("nan"),
    }


def select_top_authors(authors: pd.DataFrame, metric: str, share: float) -> pd.DataFrame:
    leader_count = max(1, int(round(len(authors) * share)))
    return authors.sort_values([metric, "user"], ascending=[False, True]).head(leader_count).copy()


def build_overall_targets(labels: pd.DataFrame) -> pd.DataFrame:
    row = {
        "target_scope": "all_answers",
        "leader_rule": "none",
        "leader_count": 0,
        "leader_answer_count": 0,
        **label_balance(labels),
    }
    return pd.DataFrame([row])


def build_leader_targets(labels: pd.DataFrame, authors: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    total_answers = len(labels)

    leader_groups: list[tuple[str, pd.DataFrame]] = []
    for metric in ["in_degree", "pagerank"]:
        for share in config.LEADER_TOP_SHARES:
            leader_groups.append((f"top_{int(share * 100)}pct_by_{metric}", select_top_authors(authors, metric, share)))

    for threshold in config.LEADER_IN_DEGREE_THRESHOLDS:
        selected = authors[authors["in_degree"] >= threshold].copy()
        leader_groups.append((f"in_degree_ge_{threshold}", selected))

    for rule_name, selected_authors in leader_groups:
        leader_users = set(selected_authors["user"])
        leader_labels = labels[labels["author"].isin(leader_users)].copy()
        non_leader_labels = labels[~labels["author"].isin(leader_users)].copy()
        leader_stats = label_balance(leader_labels)
        non_leader_stats = label_balance(non_leader_labels)
        rows.append(
            {
                "leader_rule": rule_name,
                "leader_count": len(leader_users),
                "leader_answer_count": len(leader_labels),
                "leader_answer_coverage": len(leader_labels) / total_answers if total_answers else 0.0,
                "leader_optimistic_count": leader_stats["optimistic_count"],
                "leader_pessimistic_count": leader_stats["pessimistic_count"],
                "leader_optimistic_share": leader_stats["optimistic_share"],
                "leader_pessimistic_share": leader_stats["pessimistic_share"],
                "leader_balance": leader_stats["balance"],
                "leader_balance_share": leader_stats["balance_share"],
                "non_leader_answer_count": len(non_leader_labels),
                "non_leader_balance_share": non_leader_stats["balance_share"],
                "leader_vs_non_leader_balance_gap": leader_stats["balance_share"] - non_leader_stats["balance_share"],
                "mean_leader_in_degree": float(selected_authors["in_degree"].mean()) if len(selected_authors) else 0.0,
                "min_leader_in_degree": int(selected_authors["in_degree"].min()) if len(selected_authors) else 0,
                "mean_leader_pagerank": float(selected_authors["pagerank"].mean()) if len(selected_authors) else 0.0,
            }
        )

    return pd.DataFrame(rows).sort_values(["leader_rule"]).reset_index(drop=True)


def run() -> dict[str, pd.DataFrame]:
    config.ensure_outputs_dir()
    labels = load_full_labels()
    authors = load_author_metrics()
    overall = build_overall_targets(labels)
    leader_targets = build_leader_targets(labels, authors)
    overall.to_csv(config.EMPIRICAL_LABEL_TARGETS_CSV, index=False, encoding="utf-8-sig")
    leader_targets.to_csv(config.LEADER_GROUP_TARGETS_CSV, index=False, encoding="utf-8-sig")
    return {"overall": overall, "leader_targets": leader_targets}


def main() -> None:
    outputs = run()
    print(outputs["overall"].to_string(index=False))
    print(f"leader_rules: {len(outputs['leader_targets'])}")
    print(f"outputs: {config.SENIOR_THESIS_OUTPUTS_DIR}")


if __name__ == "__main__":
    main()

