from __future__ import annotations

import math
import re
from typing import Iterable

import pandas as pd


ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")
WHITESPACE_RE = re.compile(r"[ \t\r\f\v]+")
INT_RE = re.compile(r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*(万)?")


def is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    try:
        return bool(pd.isna(value))
    except Exception:
        return False


def normalize_text(value: object, collapse_lines: bool = False) -> str:
    if is_missing(value):
        return ""
    text = str(value).replace("_x000D_", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = ZERO_WIDTH_RE.sub("", text)
    if collapse_lines:
        text = re.sub(r"\s+", " ", text)
    else:
        text = "\n".join(WHITESPACE_RE.sub(" ", line).strip() for line in text.split("\n"))
        text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_user(value: object) -> str:
    user = normalize_text(value, collapse_lines=True)
    user = re.sub(r"\s+", " ", user).strip()
    return user


def parse_int(value: object) -> int:
    if is_missing(value):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float) and not math.isnan(value):
        return int(value)
    text = normalize_text(value, collapse_lines=True)
    match = INT_RE.search(text)
    if not match:
        return 0
    number = float(match.group(1).replace(",", ""))
    if match.group(2) == "万":
        number *= 10000
    return int(round(number))


def split_liker_list(value: object) -> list[str]:
    if is_missing(value):
        return []
    text = normalize_text(value, collapse_lines=False)
    raw_parts: Iterable[str] = re.split(r"[\n;；]+", text)
    return [user for user in (clean_user(part) for part in raw_parts) if user]

