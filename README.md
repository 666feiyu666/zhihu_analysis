# Zhihu Empirical Inputs for Opinion_ABM

This repository prepares empirical Zhihu evidence for the `Opinion_ABM` thesis project without changing the ABM codebase.

## Data Source

The raw Zhihu data were crawled in December 2024 from the following Zhihu question / answer thread:

https://www.zhihu.com/question/668753879/answer/3649938067

The local Excel files are treated as archived raw data snapshots. Scripts do not re-crawl Zhihu and should not overwrite files under `original_data/`.

## Role in the Thesis

The outputs here are intended to support three uses:

1. **Motivation**: show that real Zhihu economic discussion has long-tailed attention and potential opinion leaders.
2. **Modeling basis**: justify the ABM assumption that high-visibility users can be represented as structurally advantaged opinion leaders.
3. **Future extension**: provide reproducible files that can later initialize an empirical ABM network, leader set, or opinion labels.

The current ABM remains theory-driven. The Zhihu outputs should be treated as empirical grounding and comparison material, not full parameter calibration.

## Main Entrypoints

```powershell
D:\ProgramData\Anaconda3\python.exe network\build_network.py
D:\ProgramData\Anaconda3\python.exe labeling\label_sample.py
D:\ProgramData\Anaconda3\python.exe labeling\label_sample.py --mode full
D:\ProgramData\Anaconda3\python.exe senior_thesis\empirical_targets.py
D:\ProgramData\Anaconda3\python.exe senior_thesis\compare_abm_empirical.py
```

## Interactive Review

- `network/network_analysis.ipynb`: network counts, quality checks, leaders, and plots.
- `labeling/labeling_review.ipynb`: 100 machine-labeled answers, confidence checks, and human review columns.

## Data Placement

Put raw files in `original_data/`. The scripts prefer:

- `original_data/zhihunw_new.xlsx`
- `original_data/zhihu_sen_new.xlsx`
- `original_data/cleaned_data.xlsx`

Generated files live under `network/outputs/` and `labeling/outputs/`.

## Thesis Analysis

`labeling/` produces machine labels. `senior_thesis/` turns those labels and network metrics into thesis-facing comparison targets:

- all-answer balance: `(optimistic - pessimistic) / total`;
- leader-group balances under top in-degree/PageRank and threshold rules;
- descriptive comparison against existing `Opinion_ABM` experiment outputs.

This comparison is scenario consistency analysis, not a claim that the ABM is fully calibrated to Zhihu.
