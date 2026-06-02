from __future__ import annotations

import json
import re
import subprocess
import urllib.parse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CACHE_DIR = Path("out/ws-cache")


@dataclass(frozen=True)
class WikisourcePage:
    title: str
    raw: str
    cache_path: Path


def fetch_raw(title: str, cache_dir: Path = DEFAULT_CACHE_DIR, refresh: bool = False) -> WikisourcePage:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / (safe_filename(title) + ".wiki")
    if cache_path.exists() and not refresh:
        return WikisourcePage(title, cache_path.read_text(encoding="utf-8"), cache_path)
    url = "https://he.wikisource.org/w/index.php?" + urllib.parse.urlencode({
        "title": title,
        "action": "raw",
    })
    raw = subprocess.check_output(
        ["curl", "-sS", "-L", "-A", "MAM-TEX-v3-prototype/0.1", url],
        text=True,
        encoding="utf-8",
    )
    cache_path.write_text(raw, encoding="utf-8")
    return WikisourcePage(title, raw, cache_path)


def safe_filename(title: str) -> str:
    return re.sub(r"[^A-Za-z0-9א-ת._-]+", "_", title).strip("_")


def template_names(raw: str) -> list[str]:
    names = []
    i = 0
    while i < len(raw) - 1:
        if raw[i:i + 2] != "{{":
            i += 1
            continue
        start = i + 2
        depth = 1
        i += 2
        while i < len(raw) - 1 and depth:
            if raw[i:i + 2] == "{{":
                depth += 1
                i += 2
            elif raw[i:i + 2] == "}}":
                depth -= 1
                i += 2
            else:
                i += 1
        if depth == 0:
            body = raw[start:i - 2]
            name = body.split("|", 1)[0].strip()
            if name:
                names.append(name)
    return names


def summarize_raw(raw: str) -> dict:
    names = template_names(raw)
    return {
        "bytes": len(raw.encode("utf-8")),
        "chars": len(raw),
        "lines": raw.count("\n") + 1,
        "template_count": len(names),
        "templates": dict(Counter(names).most_common()),
        "has_noinclude": "<noinclude>" in raw or "</noinclude>" in raw,
    }


def write_summary(summary: dict, path: Path) -> None:
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
