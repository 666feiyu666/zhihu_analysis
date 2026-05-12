from __future__ import annotations

from shared.paths import NETWORK_OUTPUTS_DIR


RANDOM_SEED = 20260512
MIN_SUBGRAPH_NODES = 80
MAX_SUBGRAPH_NODES = 180

ANSWER_LIKE_DETAILS_CSV = NETWORK_OUTPUTS_DIR / "answer_like_details.csv"
USER_EDGE_LIST_CSV = NETWORK_OUTPUTS_DIR / "user_user_edges.csv"
NODE_METRICS_CSV = NETWORK_OUTPUTS_DIR / "node_metrics.csv"
NETWORK_METRICS_CSV = NETWORK_OUTPUTS_DIR / "network_metrics.csv"
QUALITY_REPORT_CSV = NETWORK_OUTPUTS_DIR / "quality_report.csv"
GRAPH_GEXF = NETWORK_OUTPUTS_DIR / "zhihu_like_author_network.gexf"
FULL_NETWORK_PNG = NETWORK_OUTPUTS_DIR / "network_overview.png"
LEADER_SUBGRAPH_PNG = NETWORK_OUTPUTS_DIR / "leader_subgraph.png"

