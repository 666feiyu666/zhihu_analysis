from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from labeling import config
from shared.data_loader import load_labeling_answers
from shared.paths import ensure_output_dirs
from shared.text_utils import normalize_text


OPTIMISTIC_TERMS = [
    "看好", "乐观", "复苏", "恢复", "回暖", "反弹", "企稳", "止跌回稳", "改善", "利好",
    "信心恢复", "预期改善", "增长", "回升", "向好", "托底", "有效", "机会", "软着陆",
    "走出", "希望", "稳住", "修复", "底部", "牛市",
]
PESSIMISTIC_TERMS = [
    "悲观", "不看好", "下行", "衰退", "萧条", "通缩", "风险", "债务", "坏账", "断供",
    "烂尾", "失业", "收入下降", "消费降级", "负增长", "泡沫", "崩", "踩踏", "螺旋下降",
    "库存", "过剩", "无效", "没用", "难以", "无法", "不可能", "回不去", "扛无可扛",
    "大概率还得", "横盘", "下降", "放缓",
]
NEGATORS = ["不", "没", "没有", "难以", "无法", "不能", "并非", "不是", "未必"]
MITIGATORS = ["避免", "防止", "解决", "托底", "救市", "支撑", "稳定"]


def select_sample(answers: pd.DataFrame) -> pd.DataFrame:
    answers = answers.sort_values(["like_count", "answer_id"], ascending=[False, True]).reset_index(drop=True)
    high = answers.head(config.HIGH_LIKE_SAMPLE_SIZE)
    remaining = answers[~answers["answer_id"].isin(high["answer_id"])]
    ordinary_n = min(config.SAMPLE_SIZE - len(high), len(remaining))
    ordinary = remaining.sample(n=ordinary_n, random_state=config.RANDOM_SEED) if ordinary_n else remaining.head(0)
    sample = pd.concat([high, ordinary], ignore_index=True)
    return sample.sort_values(["like_count", "answer_id"], ascending=[False, True]).head(config.SAMPLE_SIZE)


def select_answers(answers: pd.DataFrame, mode: str) -> pd.DataFrame:
    if mode == "review":
        return select_sample(answers)
    if mode == "full":
        return answers.sort_values(["answer_id"], ascending=True).copy()
    raise ValueError(f"Unsupported labeling mode: {mode}")


def _term_hits(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term in text]


def _negated_optimism_score(text: str, optimistic_hits: list[str]) -> int:
    score = 0
    for term in optimistic_hits:
        for match in re.finditer(re.escape(term), text):
            window = text[max(0, match.start() - 8) : match.start()]
            if any(negator in window for negator in NEGATORS):
                score += 2
    return score


def _mitigated_pessimism_score(text: str, pessimistic_hits: list[str]) -> int:
    score = 0
    for term in pessimistic_hits:
        for match in re.finditer(re.escape(term), text):
            window = text[max(0, match.start() - 8) : match.start()]
            if any(mitigator in window for mitigator in MITIGATORS):
                score += 1
    return score


def label_text(answer_text: str) -> tuple[str, float, str]:
    text = normalize_text(answer_text, collapse_lines=True)
    optimistic_hits = _term_hits(text, OPTIMISTIC_TERMS)
    pessimistic_hits = _term_hits(text, PESSIMISTIC_TERMS)
    optimistic_score = len(optimistic_hits)
    pessimistic_score = len(pessimistic_hits)
    pessimistic_score += _negated_optimism_score(text, optimistic_hits)
    optimistic_score += _mitigated_pessimism_score(text, pessimistic_hits)

    if optimistic_score > pessimistic_score:
        label = "optimistic"
        margin = optimistic_score - pessimistic_score
    else:
        label = "pessimistic"
        margin = pessimistic_score - optimistic_score

    total = max(optimistic_score + pessimistic_score, 1)
    confidence = min(0.92, max(0.52, 0.52 + margin / (total + 3)))
    if not optimistic_hits and not pessimistic_hits:
        confidence = 0.52
        rationale = "未命中明显经济前景词，只能依据整体语境作低置信二选一。"
    else:
        opt = "、".join(optimistic_hits[:5]) or "无"
        pes = "、".join(pessimistic_hits[:5]) or "无"
        rationale = f"经济乐观线索：{opt}；经济悲观线索：{pes}；按经济前景判断为{label}。"
    return label, round(float(confidence), 2), rationale


def run(input_path: str | Path | None = None, mode: str = "review") -> pd.DataFrame:
    ensure_output_dirs()
    answers = load_labeling_answers(input_path)
    sample = select_answers(answers, mode=mode)
    labels = sample["answer_text"].apply(label_text)
    sample = sample.copy()
    sample["label"] = [item[0] for item in labels]
    sample["confidence"] = [item[1] for item in labels]
    sample["rationale"] = [item[2] for item in labels]
    output_columns = [
        "answer_id",
        "author",
        "like_count",
        "created_at",
        "answer_text",
        "label",
        "confidence",
        "rationale",
    ]
    output_path = config.FULL_LABELS_CSV if mode == "full" else config.LABELED_SAMPLE_CSV
    sample[output_columns].to_csv(output_path, index=False, encoding="utf-8-sig")
    if mode == "review":
        review = sample[output_columns].copy()
        review["human_label"] = ""
        review["review_note"] = ""
        review.to_csv(config.REVIEW_TEMPLATE_CSV, index=False, encoding="utf-8-sig")
    return sample[output_columns]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Label Zhihu answers as economically optimistic or pessimistic.")
    parser.add_argument(
        "--mode",
        default="review",
        choices=["review", "full"],
        help="review labels the reproducible 100-row review sample; full labels every non-empty answer.",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optional input Excel path. Defaults to original_data/zhihu_sen_new.xlsx with legacy fallbacks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    labeled = run(input_path=args.input, mode=args.mode)
    print(f"labeled_rows: {len(labeled)}")
    print(labeled["label"].value_counts().to_string())
    if args.mode == "full":
        print(f"output: {config.FULL_LABELS_CSV}")
    else:
        print(f"output: {config.LABELED_SAMPLE_CSV}")
    print(f"outputs: {config.LABELING_OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
