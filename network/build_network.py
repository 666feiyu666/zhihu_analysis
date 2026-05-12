from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from network import config
from network.metrics import build_graph, compute_network_metrics, compute_node_metrics
from network.visualize import write_network_plots
from shared.data_loader import load_network_answers
from shared.paths import ensure_output_dirs
from shared.text_utils import split_liker_list


def build_answer_like_details(answers: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    detail_rows = []
    quality = Counter()
    quality["raw_answer_rows"] = len(answers)

    for row in answers.itertuples(index=False):
        if not row.author:
            quality["answers_missing_author"] += 1
            continue
        raw_likers = split_liker_list(row.raw_liker_list)
        if not raw_likers:
            quality["answers_without_liker_list"] += 1
            continue
        counts = Counter(raw_likers)
        duplicate_count = sum(count - 1 for count in counts.values() if count > 1)
        quality["duplicate_likers_within_answer"] += duplicate_count
        unique_likers = sorted(counts)
        for liker in unique_likers:
            if not liker:
                quality["invalid_empty_liker_records"] += 1
                continue
            if liker == row.author:
                quality["self_like_records_removed"] += 1
                continue
            detail_rows.append(
                {
                    "answer_id": row.answer_id,
                    "author": row.author,
                    "liker": liker,
                    "created_at": row.created_at,
                    "like_count": row.like_count,
                }
            )

    details = pd.DataFrame(detail_rows, columns=["answer_id", "author", "liker", "created_at", "like_count"])
    quality["answer_level_like_records"] = len(details)
    quality["answers_with_parsed_likes"] = details["answer_id"].nunique() if not details.empty else 0
    quality["unique_answer_authors"] = details["author"].nunique() if not details.empty else 0
    quality["unique_likers"] = details["liker"].nunique() if not details.empty else 0
    quality["removed_duplicate_or_invalid_records"] = (
        quality["duplicate_likers_within_answer"]
        + quality["invalid_empty_liker_records"]
        + quality["self_like_records_removed"]
    )
    quality_df = pd.DataFrame([{"metric": key, "value": value} for key, value in sorted(quality.items())])
    return details, quality_df


def aggregate_edges(answer_like_details: pd.DataFrame) -> pd.DataFrame:
    if answer_like_details.empty:
        return pd.DataFrame(columns=["liker", "author", "interaction_count"])
    return (
        answer_like_details.groupby(["liker", "author"], as_index=False)
        .size()
        .rename(columns={"size": "interaction_count"})
        .sort_values(["interaction_count", "author", "liker"], ascending=[False, True, True])
    )


def run(input_path: str | Path | None = None) -> dict[str, object]:
    ensure_output_dirs()
    answers = load_network_answers(input_path)
    answer_like_details, quality = build_answer_like_details(answers)
    edges = aggregate_edges(answer_like_details)
    graph = build_graph(edges)
    authors = set(answer_like_details["author"]) if not answer_like_details.empty else set()
    likers = set(answer_like_details["liker"]) if not answer_like_details.empty else set()
    node_metrics = compute_node_metrics(graph, authors, likers)
    network_metrics = compute_network_metrics(graph)

    answer_like_details.to_csv(config.ANSWER_LIKE_DETAILS_CSV, index=False, encoding="utf-8-sig")
    edges.to_csv(config.USER_EDGE_LIST_CSV, index=False, encoding="utf-8-sig")
    node_metrics.to_csv(config.NODE_METRICS_CSV, index=False, encoding="utf-8-sig")
    network_metrics.to_csv(config.NETWORK_METRICS_CSV, index=False, encoding="utf-8-sig")
    quality.to_csv(config.QUALITY_REPORT_CSV, index=False, encoding="utf-8-sig")
    nx.write_gexf(graph, config.GRAPH_GEXF)
    write_network_plots(graph, node_metrics, config.FULL_NETWORK_PNG, config.LEADER_SUBGRAPH_PNG)

    return {
        "answers": answers,
        "answer_like_details": answer_like_details,
        "edges": edges,
        "node_metrics": node_metrics,
        "network_metrics": network_metrics,
        "quality": quality,
        "graph": graph,
    }


def main() -> None:
    result = run()
    metrics = {
        "raw_answer_rows": len(result["answers"]),
        "answer_level_like_records": len(result["answer_like_details"]),
        "user_user_edges": len(result["edges"]),
        "nodes": result["graph"].number_of_nodes(),
    }
    for key, value in metrics.items():
        print(f"{key}: {value}")
    print(f"outputs: {config.NETWORK_OUTPUTS_DIR}")


if __name__ == "__main__":
    main()

