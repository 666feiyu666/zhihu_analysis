# 知乎点赞用户-回答用户网络

## 数据来源

原始知乎数据爬取于 2024 年 12 月，来源问题/回答页面：

https://www.zhihu.com/question/668753879/answer/3649938067

## 输入文件

推荐将原始数据放在 `original_data/zhihunw_new.xlsx`。脚本会优先读取该文件；若不存在，会回退到旧位置 `SNA/zhihunw_new.xlsx`。

原始字段映射：

- `文本`：回答文本
- `用户`：回答用户
- `发布时间`：回答发布时间
- `评论数目`：评论数
- `赞同数目`：赞同数
- `赞同列表`：点赞用户列表，使用 `_x000D_`、换行或空白分隔

## 运行命令

在项目根目录运行：

```powershell
D:\ProgramData\Anaconda3\python.exe network\build_network.py
```

## 输出文件

输出目录为 `network/outputs/`：

- `answer_like_details.csv`：回答级点赞明细，字段为 `answer_id`, `author`, `liker`, `created_at`, `like_count`
- `user_user_edges.csv`：聚合后的有向边，字段为 `liker`, `author`, `interaction_count`
- `node_metrics.csv`：节点指标，字段包含 `user`, `in_degree`, `out_degree`, `pagerank`, `is_answer_author`, `is_liker`
- `network_metrics.csv`：全图指标，基于有向全图计算密度，基于弱连通分量计算连通性
- `quality_report.csv`：空值、重复点赞、自赞移除等质量检查
- `zhihu_like_author_network.gexf`：可导入 Gephi 的网络文件
- `network_overview.png`、`leader_subgraph.png`：网络可视化

## 边与指标含义

网络为有向图：`liker -> author`。边表示点赞用户认可或接触到了回答用户的回答，可作为 follower-followee / influence-exposure 网络的近似。

默认边是二值用户对；若同一点赞用户在不同回答中点赞了同一回答用户，`interaction_count` 表示跨回答累计互动次数。同一回答内部重复出现的同一点赞用户会去重，并写入 `quality_report.csv`。

Opinion leaders 建议优先按 `in_degree`、`pagerank` 或 `interaction_count` 解释，不使用旧逻辑中的 `out_degree > 10`。

## Notebook

打开 `network/network_analysis.ipynb` 可交互查看：

- 原始回答数量、解析出的点赞记录数、用户数、边数
- 节点指标前几行
- 按 `in_degree` 和 `pagerank` 排序的 Top opinion leaders
- 网络图和主要子图
- 数据质量检查结果
