"""Build a static directory of MAM chapters with prev/next nav.

Usage:
    python build_site.py [--out out/site] [--books Genesis Exodus ...]

Open out/site/index.html directly in a browser; no server needed.
"""
from __future__ import annotations

import argparse
from html import escape
from itertools import groupby
from pathlib import Path

from mam3.ofer_haftarot import load_haftarot
from mam3.pipeline import book_events
from mam3.render_html import render_html
from mam3.sections import section_summary
from mam3.source import DEFAULT_SOURCE, load_book

OFER_PATH = Path(__file__).resolve().parent.parent / "Haftarot 3 years _ Ofer.xls"


BOOK_ORDER = [
    "Genesis", "Exodus", "Levit", "Numbers", "Deuter",
    "Joshua", "Judges", "Samuel", "Kings",
    "Isaiah", "Jeremiah", "Ezekiel", "The-12-Minor-Prophets",
    "Psalms", "Proverbs", "Job",
    "Song of Songs", "Ruth", "Lamentations", "Ecclesiastes", "Esther",
    "Daniel", "Ezra-Neḥemiah", "Chronicles",
]


# Books whose `book39s` are distinct books traditionally *counted* as a single
# book of the 24, but shown as separate books inside a named group (each gets
# its own pages and chapter numbering). Contrast with books like Samuel that are
# ONE book with named subdivisions — those are handled via `split`/`parts`.
GROUPED_BOOKS = {"The-12-Minor-Prophets"}


def slug(name: str) -> str:
    return name.replace(" ", "-").replace('"', "")


def chapter_section(sec: dict, book_idx: int, chapter: str) -> dict:
    book = sec["book39s"][book_idx]
    chap_dict = {chapter: book["chapters"][chapter]}
    return {**sec, "book39s": [{**book, "chapters": chap_dict}]}


def part_prefix(part: dict) -> str:
    """Filename-safe prefix identifying a sub-book (e.g. שמ"א -> שמא)."""
    return slug(part["sub_name"]) if part["sub_name"] else ""


def chapter_file(entry: dict, part: dict, ch: str) -> str:
    """Chapter filename. Split books namespace chapters by part so the two
    halves (each numbered from א) don't collide on disk."""
    if entry["split"]:
        return f'{part_prefix(part)}-{ch}.html'
    return f'{ch}.html'


def chapter_label(entry: dict, part: dict, ch: str) -> str:
    """Human label for nav: 'שמ"א א' for split books, 'ספר בראשית א' otherwise."""
    if entry["split"]:
        return f'{part["sub_name"]} {ch}'
    return f'{entry["display_name"]} {ch}'


def _chapters_of(b: dict) -> list[str]:
    return [c for c in b["chapters"].keys() if c not in {"0", "תתת"}]


def collect(books: list[str], source: Path) -> list[dict]:
    """Build the catalog of book units to render.

    Three shapes of `book39s`:
      * single book (Genesis): one unit, one part.
      * one book with named subdivisions (Samuel, Kings, Chronicles,
        Ezra-Neḥemiah): one unit, `split=True`, the halves become `parts`
        that namespace the chapter numbering within a shared directory.
      * a group of separate books (The-12-Minor-Prophets, see GROUPED_BOOKS):
        one standalone unit per sub-book — each its own directory and pages —
        tagged with a shared `group` for index display.
    """
    catalog = []
    for book_key in books:
        try:
            sec = load_book(book_key, source)
        except FileNotFoundError:
            print(f"skip {book_key}: not found")
            continue
        book39s = sec["book39s"]
        if book_key in GROUPED_BOOKS:
            group_name = book39s[0]["book24_name"]
            for bi, b in enumerate(book39s):
                sub = b.get("sub_book_name")
                catalog.append({
                    "book_key": slug(sub),
                    "display_name": sub,
                    "group": group_name,
                    "split": False,
                    "parts": [{"book_idx": bi, "sub_name": sub,
                               "chapters": _chapters_of(b)}],
                    "sec": sec,
                })
            continue
        parts = [
            {"book_idx": bi, "sub_name": b.get("sub_book_name"),
             "chapters": _chapters_of(b)}
            for bi, b in enumerate(book39s)
        ]
        catalog.append({
            "book_key": book_key,
            "display_name": book39s[0]["book24_name"],
            "group": None,
            "split": len(parts) > 1,
            "parts": parts,
            "sec": sec,
        })
    return catalog


def write_indexes(catalog: list[dict], out_dir: Path) -> None:
    parts = [
        '<!doctype html><html lang="he" dir="rtl"><head>',
        '<meta charset="utf-8"><title>מקרא על פי המסורה</title>',
        "<style>",
        "body{font-family:-apple-system,'Segoe UI','Arial Hebrew',sans-serif;",
        "background:#fffdfa;color:#1f1b18;max-width:60rem;margin:2rem auto;padding:0 2rem;}",
        "h1{color:#8b1d1d;text-align:center;}",
        ".book{margin:1rem 0;padding:.5rem 1rem;border:1px solid #d8d0c8;border-radius:4px;background:#fff;}",
        ".book h2{margin:.25rem 0;color:#8b1d1d;font-size:1.1rem;}",
        ".chapters a{display:inline-block;margin:.15rem;padding:.2rem .55rem;",
        "border:1px solid #d8d0c8;border-radius:3px;color:#8b1d1d;text-decoration:none;background:#fffdfa;}",
        ".chapters a:hover{background:#f4efe8;}",
        ".part{display:flex;align-items:baseline;gap:.5rem;margin:.25rem 0;}",
        ".part-label{color:#8b1d1d;font-weight:700;min-width:3rem;flex:none;}",
        ".group{margin:1rem 0;padding:.25rem 1rem .5rem;border:1px solid #d8d0c8;",
        "border-radius:4px;background:#faf6f0;}",
        ".group-head{color:#8b1d1d;text-align:center;font-size:1.2rem;margin:.5rem 0;}",
        ".group .book{margin:.5rem 0;}",
        ".group .book h3{margin:.25rem 0;color:#8b1d1d;font-size:1rem;}",
        "</style></head><body>",
        "<h1>מקרא על פי המסורה</h1>",
    ]
    for group_name, group_units in groupby(catalog, key=lambda e: e["group"]):
        units = list(group_units)
        if group_name:
            parts.append(f'<div class="group"><h2 class="group-head">'
                         f'{escape(group_name)}</h2>')
        head = "h3" if group_name else "h2"
        for entry in units:
            bk = slug(entry["book_key"])
            parts.append(f'<div class="book"><{head}><a href="{bk}/index.html">'
                         f'{escape(entry["display_name"])}</a></{head}>')
            for part in entry["parts"]:
                parts.append('<div class="part">')
                if entry["split"]:
                    parts.append(f'<span class="part-label">{escape(part["sub_name"])}</span>')
                parts.append('<div class="chapters">')
                for ch in part["chapters"]:
                    fn = escape(chapter_file(entry, part, ch))
                    parts.append(f'<a href="{bk}/{fn}">{escape(ch)}</a>')
                parts.append("</div></div>")
            parts.append("</div>")
        if group_name:
            parts.append("</div>")
    parts.append("</body></html>")
    (out_dir / "index.html").write_text("".join(parts), encoding="utf-8")

    for entry in catalog:
        bk = slug(entry["book_key"])
        bdir = out_dir / bk
        bdir.mkdir(parents=True, exist_ok=True)
        rows = ["".join([
            '<!doctype html><html lang="he" dir="rtl"><head>',
            f'<meta charset="utf-8"><title>{escape(entry["display_name"])}</title>',
            "<style>",
            "body{font-family:-apple-system,'Segoe UI','Arial Hebrew',sans-serif;",
            "background:#fffdfa;color:#1f1b18;max-width:60rem;margin:2rem auto;padding:0 2rem;}",
            "h1{color:#8b1d1d;text-align:center;}",
            ".chapters a{display:inline-block;margin:.15rem;padding:.3rem .7rem;",
            "border:1px solid #d8d0c8;border-radius:3px;color:#8b1d1d;text-decoration:none;background:#fff;}",
            ".chapters a:hover{background:#f4efe8;}",
            ".part-head{color:#8b1d1d;text-align:center;font-size:1rem;margin:1rem 0 .25rem;}",
            ".back{display:block;text-align:center;margin:1rem 0;color:#8b1d1d;}",
            ".sections-link{display:block;text-align:center;margin:1rem 0;color:#8b1d1d;}",
            "</style></head><body>",
            '<a class="back" href="../index.html">→ תוכן הענינים</a>',
            f'<h1>{escape(entry["display_name"])}</h1>',
        ])]
        for part in entry["parts"]:
            if entry["split"]:
                rows.append(f'<h2 class="part-head">{escape(part["sub_name"])}</h2>')
            rows.append('<div class="chapters" style="text-align:center;">')
            for ch in part["chapters"]:
                fn = escape(chapter_file(entry, part, ch))
                rows.append(f'<a href="{fn}">{escape(ch)}</a>')
            rows.append('</div>')
        rows.append('<a class="sections-link" href="sections.html">סיכום פרשיות פתוחות וסתומות ←</a>')
        rows.append("</body></html>")
        (bdir / "index.html").write_text("".join(rows), encoding="utf-8")
        write_sections_page(entry, bdir)


_OFER_CACHE: dict[tuple[str, str, str], dict[str, str]] | None = None


def _ofer() -> dict[tuple[str, str, str], dict[str, str]]:
    global _OFER_CACHE
    if _OFER_CACHE is None:
        _OFER_CACHE = load_haftarot(OFER_PATH)
    return _OFER_CACHE


def write_sections_page(entry: dict, bdir: Path) -> None:
    ofer = _ofer()
    extras = {
        (ch, v) for (bk, ch, v) in ofer if bk == entry["book_key"]
    }
    # One block of section rows per sub-book; for unsplit books there is just one.
    part_blocks: list[tuple[dict, list[dict]]] = []
    for part in entry["parts"]:
        book_only = {**entry["sec"], "book39s": [entry["sec"]["book39s"][part["book_idx"]]]}
        rows = section_summary(book_events(book_only), extra_verses=extras)
        for r in rows:
            key = (entry["book_key"], r["chapter"], r["verse"])
            r["ofer"] = ofer.get(key, {})
        part_blocks.append((part, rows))
    total = sum(len(rows) for _, rows in part_blocks)
    parts = [
        '<!doctype html><html lang="he" dir="rtl"><head>',
        '<meta charset="utf-8">',
        f'<title>פרשיות — {escape(entry["display_name"])}</title>',
        "<style>",
        "body{font-family:-apple-system,'Segoe UI','Arial Hebrew',sans-serif;",
        "background:#fffdfa;color:#1f1b18;max-width:64rem;margin:2rem auto;padding:0 2rem;}",
        "h1{color:#8b1d1d;text-align:center;font-size:1.4rem;}",
        ".back{display:inline-block;color:#8b1d1d;text-decoration:none;}",
        "table{width:100%;border-collapse:collapse;margin-top:1rem;font-size:.95rem;}",
        "th,td{border:1px solid #d8d0c8;padding:.4rem .6rem;text-align:right;vertical-align:top;}",
        "th{background:#f4efe8;color:#8b1d1d;}",
        "td.type{text-align:center;font-weight:700;color:#8b1d1d;}",
        "td.count{text-align:center;color:#6f635c;}",
        ".lemma{font-family:'Taamey Frank CLM','SBL Hebrew',serif;font-weight:700;}",
        ".note{color:#6f635c;font-size:.88rem;}",
        ".parashah{font-weight:700;color:#016200;}",
        ".seder{font-weight:700;color:#1e6fb8;}",
        ".haftarah{color:#5b3f00;}",
        "tr:nth-child(even) td{background:#fbf7ef;}",
        ".verse a{color:#8b1d1d;text-decoration:none;}",
        "td.part-row{background:#f4efe8;color:#8b1d1d;font-weight:700;text-align:center;}",
        "</style></head><body>",
        '<a class="back" href="index.html">→ אינדקס פרקים</a>',
        f'<h1>פרשיות פתוחות וסתומות — {escape(entry["display_name"])}</h1>',
        f"<p>סך הכל: {total} פרשיות.</p>",
        "<table>",
        "<thead><tr>",
        "<th>פסוק</th><th>סוג</th><th>פסוקים</th>",
        "<th>פרשה</th><th>סדר</th>",
        "<th>תחילת הסדר (עופר)</th><th>הפטרה (עופר)</th>",
        "<th>הערה</th>",
        "</tr></thead><tbody>",
    ]
    for part, rows in part_blocks:
        if entry["split"]:
            parts.append(
                f'<tr><td class="part-row" colspan="8">{escape(part["sub_name"])}</td></tr>'
            )
        for r in rows:
            ch_href = escape(chapter_file(entry, part, r["chapter"]))
            verse_link = f'{ch_href}#v-{escape(r["chapter"])}-{escape(r["verse"])}'
            verse_label = f'{escape(r["chapter"])}:{escape(r["verse"])}'
            if r["type"] == "open":
                type_label = "{פ}"
            elif r["type"] == "closed":
                type_label = "{ס}"
            else:
                type_label = ""
            note_html = ""
            if r["note"]:
                tgt = (f'<span class="lemma" lang="hbo">{escape(r["note_target"])}</span> · '
                       if r["note_target"] else "")
                note_html = f'{tgt}<span class="note">{escape(r["note"])}</span>'
            parashah_html = (
                f'<span class="parashah">{escape(r["parashah"])}</span>'
                if r["parashah"] else ""
            )
            seder_html = (
                f'<span class="seder">{escape(r["seder"])}</span>'
                if r.get("seder") else ""
            )
            ofer = r.get("ofer") or {}
            opening = escape(ofer.get("opening", ""))
            haftarah = ofer.get("haftarah", "")
            if haftarah and ofer.get("piyyut"):
                haftarah_html = f'<span class="haftarah">{escape(haftarah)}</span> <small>(פיוט)</small>'
            elif haftarah:
                haftarah_html = f'<span class="haftarah">{escape(haftarah)}</span>'
            else:
                haftarah_html = ""
            parts.append(
                "<tr>"
                f'<td class="verse"><a href="{verse_link}">{verse_label}</a></td>'
                f'<td class="type">{type_label}</td>'
                f'<td class="count">{r["verses_since_last"]}</td>'
                f"<td>{parashah_html}</td>"
                f'<td class="count">{seder_html}</td>'
                f"<td>{opening}</td>"
                f"<td>{haftarah_html}</td>"
                f"<td>{note_html}</td>"
                "</tr>"
            )
    parts.append("</tbody></table></body></html>")
    (bdir / "sections.html").write_text("".join(parts), encoding="utf-8")


def build_chapters(catalog: list[dict], out_dir: Path) -> None:
    flat: list[tuple[dict, dict, str]] = []
    for entry in catalog:
        for part in entry["parts"]:
            for ch in part["chapters"]:
                flat.append((entry, part, ch))

    for i, (entry, part, ch) in enumerate(flat):
        sec = chapter_section(entry["sec"], part["book_idx"], ch)
        events = list(book_events(sec))

        prev_html = '<a class="prev disabled">·</a>'
        next_html = '<a class="next disabled">·</a>'
        if i > 0:
            pe, pp, pch = flat[i - 1]
            href = f'../{slug(pe["book_key"])}/{escape(chapter_file(pe, pp, pch))}'
            prev_html = (f'<a class="prev" href="{href}">'
                         f'→ {escape(chapter_label(pe, pp, pch))}</a>')
        if i < len(flat) - 1:
            ne, np_, nch = flat[i + 1]
            href = f'../{slug(ne["book_key"])}/{escape(chapter_file(ne, np_, nch))}'
            next_html = (f'<a class="next" href="{href}">'
                         f'{escape(chapter_label(ne, np_, nch))} ←</a>')
        book_index = f'../{slug(entry["book_key"])}/index.html'
        nav_html = (
            '<nav class="chapter-nav">'
            f'{prev_html}'
            f'<a class="up" href="{book_index}">{escape(entry["display_name"])}</a>'
            f'<a class="up" href="../index.html">תוכן הענינים</a>'
            f'{next_html}'
            "</nav>"
        )

        part_label = f'{part["sub_name"]} ' if entry["split"] else f'{entry["display_name"]} '
        title = f'{part_label}פרק {ch}'
        page = render_html(events, notes=lambda n: True, nav_html=nav_html, title=title)
        path = out_dir / slug(entry["book_key"]) / chapter_file(entry, part, ch)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("out/site"))
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--books", nargs="*", default=BOOK_ORDER,
                        help="Subset of book keys (default: all)")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    catalog = collect(args.books, args.source)
    if not catalog:
        raise SystemExit("no books found")
    write_indexes(catalog, args.out)
    build_chapters(catalog, args.out)
    n = sum(len(p["chapters"]) for e in catalog for p in e["parts"])
    print(f"wrote {n} chapters across {len(catalog)} books to {args.out}")


if __name__ == "__main__":
    main()
