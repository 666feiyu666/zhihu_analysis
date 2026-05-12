from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def _draw_graph(graph: nx.DiGraph, path: Path, title: str) -> None:
    if graph.number_of_nodes() == 0:
        return
    plt.figure(figsize=(12, 9))
    pos = nx.spring_layout(graph, seed=20260512, k=None)
    indegree = dict(graph.in_degree())
    sizes = [35 + min(indegree.get(node, 0), 60) * 12 for node in graph.nodes()]
    nx.draw_networkx_edges(graph, pos, alpha=0.12, width=0.6, arrows=False)
    nx.draw_networkx_nodes(graph, pos, node_size=sizes, node_color="#3b82f6", alpha=0.78, linewidths=0)
    top_labels = sorted(indegree, key=indegree.get, reverse=True)[:20]
    nx.draw_networkx_labels(
        graph,
        pos,
        labels={node: node for node in top_labels},
        font_size=8,
        font_family="SimHei",
    )
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=200)
    plt.close()


def select_leader_subgraph(graph: nx.DiGraph, node_metrics: pd.DataFrame, max_nodes: int = 180) -> nx.DiGraph:
    if graph.number_of_nodes() <= max_nodes:
        return graph.copy()
    leaders = node_metrics.sort_values(["in_degree", "pagerank"], ascending=[False, False]).head(30)["user"].tolist()
    selected = set(leaders)
    for leader in leaders:
        incoming = sorted(graph.predecessors(leader), key=lambda node: graph[node][leader].get("interaction_count", 1), reverse=True)
        selected.update(incoming[:5])
    if len(selected) < max_nodes:
        extra = node_metrics.head(max_nodes - len(selected))["user"].tolist()
        selected.update(extra)
    return graph.subgraph(list(selected)[:max_nodes]).copy()


def write_network_plots(graph: nx.DiGraph, node_metrics: pd.DataFrame, full_path: Path, subgraph_path: Path) -> None:
    overview = graph
    if graph.number_of_nodes() > 350:
        overview = select_leader_subgraph(graph, node_metrics, max_nodes=220)
    _draw_graph(overview, full_path, "Zhihu like-user to answer-author network")
    _draw_graph(select_leader_subgraph(graph, node_metrics), subgraph_path, "High in-degree / PageRank subgraph")

