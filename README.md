# Zhihu Empirical Analysis

Prepares network, labeling, and OLIM-comparison evidence from a December 2024
[Zhihu discussion](https://www.zhihu.com/question/668753879/answer/3649938067).

The outputs provide empirical motivation and scenario-consistency comparisons;
they are not full parameter calibration or causal evidence of opinion-leader effects. See [opinion-model](https://github.com/666feiyu666/Opinion_ABM)

## Run

```powershell
uv sync --locked
uv run --locked python network\build_network.py
uv run --locked python labeling\label_sample.py --mode full
uv run --locked python senior_thesis\empirical_targets.py
uv run --locked python senior_thesis\compare_abm_empirical.py
```

Treat `original_data/` as immutable. Generated files stay under each module's
`outputs/` directory. Use `network/network_analysis.ipynb` and
`labeling/labeling_review.ipynb` for interactive review.
