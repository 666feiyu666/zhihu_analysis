# 知乎回答经济乐观/悲观打标

## 数据来源

原始知乎数据爬取于 2024 年 12 月，来源问题/回答页面：

https://www.zhihu.com/question/668753879/answer/3649938067

## 输入文件

推荐将原始数据放在 `original_data/zhihu_sen_new.xlsx`。脚本会优先读取该文件；若不存在，会回退到 `Sentiment/zhihu_sen_new.xlsx`、`Sentiment/cleaned_data.xlsx` 或 `SNA/zhihunw_new.xlsx`。

## 标签定义

- `optimistic`：对中国经济、房地产、政策效果、市场恢复、就业收入、未来增长等持相对乐观判断
- `pessimistic`：对中国经济、房地产、政策有效性、就业收入、债务风险、市场恢复、未来走势等持相对悲观判断

这不是通用情绪分析。脚本使用回答文本本身和经济前景相关线索做二分类，不使用旧的通用正负面词典结果。难以判断的文本也会强制二选一，并降低 `confidence`，在 `rationale` 中说明。

## 运行命令

在项目根目录运行：

```powershell
D:\ProgramData\Anaconda3\python.exe labeling\label_sample.py
```

默认只抽取并打标 100 条，供人工检查。若要对全部非空回答打标，显式运行：

```powershell
D:\ProgramData\Anaconda3\python.exe labeling\label_sample.py --mode full
```

全量打标结果仍然是机器规则结果，后续可以替换为更强的人工校验或模型打标方法。

## 抽样方式

固定随机种子为 `20260512`。样本优先覆盖高赞回答：先取赞同数最高的 30 条，再从其余回答中随机抽取 70 条普通回答。

## 输出文件

输出目录为 `labeling/outputs/`：

- `economic_label_sample_100.csv`：机器打标结果，字段为 `answer_id`, `author`, `like_count`, `created_at`, `answer_text`, `label`, `confidence`, `rationale`
- `economic_label_review_template.csv`：人工审阅模板，在机器打标字段后增加 `human_label`, `review_note`
- `economic_labels_full.csv`：全部非空回答的机器打标结果

## Notebook

打开 `labeling/labeling_review.ipynb` 可交互查看：

- 100 条机器打标结果
- 标签分布
- 低置信样本
- 每条回答的作者、赞同数、文本和标签
- 人工校验列 `human_label`、`review_note`
- 导出人工修订后的 CSV

论文侧的经验指标和 `Opinion_ABM` 对比放在 `senior_thesis/`，避免把“打标管线”和“论文分析管线”混在一起。
