from __future__ import annotations

from pathlib import Path

import pandas as pd

from shared.paths import find_data_file
from shared.text_utils import clean_user, normalize_text, parse_int


def _first_existing_column(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    if required:
        raise KeyError(f"None of these columns exist: {candidates}. Actual columns: {list(df.columns)}")
    return None


def _answer_id_from_index(index: int) -> str:
    return f"ans_{index + 2:05d}"


def load_network_answers(path: str | Path | None = None) -> pd.DataFrame:
    """Load raw answer rows for network construction."""
    data_path = Path(path) if path else find_data_file(
        "zhihunw_new.xlsx",
        ["SNA/zhihunw_new.xlsx", "Sentiment/zhihu_sen_new.xlsx"],
    )
    df = pd.read_excel(data_path)
    text_col = _first_existing_column(df, ["文本", "回答文本"])
    author_col = _first_existing_column(df, ["用户", "作者"])
    created_col = _first_existing_column(df, ["发布时间", "时间", "时间.1"])
    comment_col = _first_existing_column(df, ["评论数目", "评论数"], required=False)
    like_col = _first_existing_column(df, ["赞同数目", "赞同数", "css1lr85n"])
    liker_col = _first_existing_column(df, ["赞同列表", "点赞用户列表"])

    records = []
    for idx, row in df.iterrows():
        records.append(
            {
                "answer_id": _answer_id_from_index(idx),
                "source_row": idx + 2,
                "answer_text": normalize_text(row[text_col]),
                "author": clean_user(row[author_col]),
                "created_at": normalize_text(row[created_col], collapse_lines=True),
                "comment_count": parse_int(row[comment_col]) if comment_col else 0,
                "like_count": parse_int(row[like_col]),
                "raw_liker_list": row[liker_col],
                "source_file": str(data_path),
            }
        )
    return pd.DataFrame(records)


def load_labeling_answers(path: str | Path | None = None) -> pd.DataFrame:
    """Load answer rows for economic optimism/pessimism labeling."""
    data_path = Path(path) if path else find_data_file(
        "zhihu_sen_new.xlsx",
        ["Sentiment/zhihu_sen_new.xlsx", "Sentiment/cleaned_data.xlsx", "SNA/zhihunw_new.xlsx"],
    )
    df = pd.read_excel(data_path)
    text_col = _first_existing_column(df, ["文本", "回答文本"])
    author_col = _first_existing_column(df, ["用户", "作者"])
    created_col = _first_existing_column(df, ["时间", "发布时间", "时间.1"])
    like_col = _first_existing_column(df, ["赞同数", "赞同数目", "css1lr85n"])

    records = []
    for idx, row in df.iterrows():
        text = normalize_text(row[text_col])
        records.append(
            {
                "answer_id": _answer_id_from_index(idx),
                "source_row": idx + 2,
                "author": clean_user(row[author_col]),
                "like_count": parse_int(row[like_col]),
                "created_at": normalize_text(row[created_col], collapse_lines=True),
                "answer_text": text,
                "source_file": str(data_path),
            }
        )
    out = pd.DataFrame(records)
    return out[out["answer_text"].str.len() > 0].reset_index(drop=True)

