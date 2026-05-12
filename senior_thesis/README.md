# Senior Thesis Empirical Comparison

This directory contains thesis-facing analysis scripts. It does not modify `Opinion_ABM`.

## Empirical Source

The Zhihu data were crawled in December 2024 from:

https://www.zhihu.com/question/668753879/answer/3649938067

## Purpose

The empirical Zhihu data are used for:

- building an all-answer optimism/pessimism balance target;
- checking how that balance differs among empirically identified opinion-leader groups;
- comparing those empirical targets with existing `Opinion_ABM` experiment outputs.

The core empirical metric is:

```text
balance_share = (optimistic_count - pessimistic_count) / total_answers
```

## Inputs

- `labeling/outputs/economic_labels_full.csv`
- `network/outputs/node_metrics.csv`
- `../Opinion_ABM/outputs/leader_effects_main/summary/summary_results.csv`

## Run

From the project root:

```powershell
D:\ProgramData\Anaconda3\python.exe labeling\label_sample.py --mode full
D:\ProgramData\Anaconda3\python.exe senior_thesis\empirical_targets.py
D:\ProgramData\Anaconda3\python.exe senior_thesis\compare_abm_empirical.py
```

## Outputs

- `senior_thesis/outputs/empirical_label_targets.csv`: all-answer empirical balance.
- `senior_thesis/outputs/leader_group_targets.csv`: balance among leader groups selected by in-degree/PageRank shares and thresholds.
- `senior_thesis/outputs/abm_empirical_comparison.csv`: ABM scenario metrics with distances to empirical all-answer and leader-group balances.
