from __future__ import annotations

import networkx as nx
import pandas as pd


def build_graph(edges: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in edges.itertuples(index=False):
        graph.add_edge(row.liker, row.author, interaction_count=int(row.interaction_count))
    return graph


def compute_node_metrics(graph: nx.DiGraph, authors: set[str], likers: set[str]) -> pd.DataFrame:
    pagerank = nx.pagerank(graph, weight="interaction_count") if graph.number_of_nodes() else {}
    rows = []
    for user in graph.nodes():
        rows.append(
            {
                "user": user,
                "in_degree": int(graph.in_degree(user)),
                "out_degree": int(graph.out_degree(user)),
                "pagerank": float(pagerank.get(user, 0.0)),
                "is_answer_author": user in authors,
                "is_liker": user in likers,
            }
        )
    return pd.DataFrame(rows).sort_values(["in_degree", "pagerank", "user"], ascending=[False, False, True])


def compute_network_metrics(graph: nx.DiGraph) -> pd.DataFrame:
    weak_components = list(nx.weakly_connected_components(graph)) if graph.number_of_nodes() else []
    largest_wcc_size = max((len(component) for component in weak_components), default=0)
    return pd.DataFrame(
        [
            {
                "scope": "directed_full_graph",
                "node_count": graph.number_of_nodes(),
                "edge_count": graph.number_of_edges(),
                "density": nx.density(graph) if graph.number_of_nodes() > 1 else 0.0,
                "weakly_connected_component_count": len(weak_components),
                "largest_weakly_connected_component_size": largest_wcc_size,
            }
        ]
    )

