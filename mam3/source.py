from __future__ import annotations

import json
import subprocess
from pathlib import Path


DEFAULT_SOURCE = Path("/Users/ephraimmeiri/gitEtc/scraping and data/MAM-parsed")

BOOK_FILES = {
    "Genesis": "A1-Genesis.json",
    "Exodus": "A2-Exodus.json",
    "Levit": "A3-Levit.json",
    "Leviticus": "A3-Levit.json",
    "Numbers": "A4-Numbers.json",
    "Deuter": "A5-Deuter.json",
    "Deuteronomy": "A5-Deuter.json",
    "Joshua": "B1-Joshua.json",
    "Judges": "B2-Judges.json",
    "Samuel": "BA-Samuel.json",
    "Kings": "BC-Kings.json",
    "Isaiah": "C1-Isaiah.json",
    "Jeremiah": "C2-Jeremiah.json",
    "Ezekiel": "C3-Ezekiel.json",
    "The-12-Minor-Prophets": "CA-The-12-Minor-Prophets.json",
    "Psalms": "D1-Psalms.json",
    "Proverbs": "D2-Proverbs.json",
    "Job": "D3-Job.json",
    "Song of Songs": "E1-Song of Songs.json",
    "Ruth": "E2-Ruth.json",
    "Lamentations": "E3-Lamentations.json",
    "Ecclesiastes": "E4-Ecclesiastes.json",
    "Esther": "E5-Esther.json",
    "Daniel": "F1-Daniel.json",
    "Ezra-Nexemiah": "FA-Ezra-Nexemiah.json",
    "Ezra-Nehemiah": "FA-Ezra-Nexemiah.json",
    "Chronicles": "FC-Chronicles.json",
}


def load_book(book: str, source: Path = DEFAULT_SOURCE, ref: str | None = None, fmt: str = "plain") -> dict:
    filename = BOOK_FILES.get(book, book if book.endswith(".json") else f"{book}.json")
    relpath = f"{fmt}/{filename}"
    if ref:
        raw = subprocess.check_output(
            ["git", "-C", str(source), "show", f"{ref}:{relpath}"],
            text=True,
            encoding="utf-8",
        )
        return json.loads(raw)
    path = source / relpath
    if not path.exists():
        fallback = source / fmt / (book if book.endswith(".json") else f"{book}.json")
        path = fallback if fallback.exists() else path
    with path.open(encoding="utf-8") as f:
        return json.load(f)

