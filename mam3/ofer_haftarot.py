"""Loader for Yosef Ofer's triennial-haftarah table.

The xls is laid out with four pre-header rows; the actual columns are:

    [row#, "<book> <chapter>:<verse>", opening_words, piyyut_evidence,
     haftarah_open, geniza_fragment, T-S B 17,35, NY Adler 2103, ...]

We keep the columns most useful for cross-referencing our section table.
"""
from __future__ import annotations

import re
from pathlib import Path

BOOK_HEB_TO_EN = {
    "בראשית": "Genesis",
    "שמות": "Exodus",
    "ויקרא": "Levit",
    "במדבר": "Numbers",
    "דברים": "Deuter",
}

_REF_RE = re.compile(r"^\s*([א-ת]+)\s+([א-ת]+):([א-ת]+)\s*$")


def load_haftarot(path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    try:
        import pandas as pd
    except ImportError:
        return {}
    if not path.exists():
        return {}
    df = pd.read_excel(path, sheet_name=0, header=None, skiprows=4)
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    for _, row in df.iterrows():
        ref = row.iloc[1] if len(row) > 1 else None
        if not isinstance(ref, str):
            continue
        m = _REF_RE.match(ref)
        if not m:
            continue
        bk_he, ch, v = m.groups()
        bk = BOOK_HEB_TO_EN.get(bk_he)
        if not bk:
            continue

        def at(i: int) -> str:
            if len(row) <= i:
                return ""
            val = row.iloc[i]
            return str(val).strip() if val is not None and not _isnan(val) else ""

        out[(bk, ch, v)] = {
            "opening": at(2),
            "piyyut": at(3),
            "haftarah": at(4),
        }
    return out


def _isnan(value) -> bool:
    try:
        import math
        return isinstance(value, float) and math.isnan(value)
    except Exception:
        return False
