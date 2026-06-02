"""Walk MAM events and summarise פ/ס section breaks.

Each break record describes the verse that *follows* the break, the kind
(open / closed), how many verses elapsed since the previous break, any
attached variant note, and — if the break coincides with the start of a
(Torah) parashah — the parashah name.
"""
from __future__ import annotations

from collections.abc import Iterable

from .events import Event


def section_summary(
    events: Iterable[Event],
    extra_verses: set[tuple[str, str]] | None = None,
) -> list[dict]:
    rows: list[dict] = []
    cur_chapter = ""
    cur_book = ""
    cur_parashah = ""
    pending_parashah = ""
    pending_seder = ""
    pending_break: str | None = None
    pending_note = ""
    pending_target = ""
    verses_since_last = 0
    for ev in events:
        if ev.kind == "book":
            cur_book = ev.text
            cur_parashah = ""
            verses_since_last = 0
        elif ev.kind == "chapter":
            cur_chapter = ev.text
        elif ev.kind == "parashah_open":
            pending_break = "open"
            pending_note = ev.meta.get("variant_note", "") if ev.meta else ""
            pending_target = ev.meta.get("variant_target", "") if ev.meta else ""
        elif ev.kind == "parashah_closed":
            pending_break = "closed"
            pending_note = ev.meta.get("variant_note", "") if ev.meta else ""
            pending_target = ev.meta.get("variant_target", "") if ev.meta else ""
        elif ev.kind == "parashah_start":
            pending_parashah = ev.text
        elif ev.kind == "seder_start":
            pending_seder = ev.text
        elif ev.kind == "verse":
            new_parashah = (
                pending_parashah
                if pending_parashah and pending_parashah != cur_parashah
                else ""
            )
            extra = bool(
                extra_verses and (cur_chapter, ev.text) in extra_verses
            )
            has_boundary = bool(
                pending_break or new_parashah or pending_seder or extra
            )
            if has_boundary:
                rows.append({
                    "book": cur_book,
                    "chapter": cur_chapter,
                    "verse": ev.text,
                    "type": pending_break or "",
                    "verses_since_last": verses_since_last,
                    "note": pending_note,
                    "note_target": pending_target,
                    "parashah": new_parashah,
                    "seder": pending_seder,
                })
                verses_since_last = 0
                pending_break = None
                pending_note = ""
                pending_target = ""
            if pending_parashah:
                cur_parashah = pending_parashah
                pending_parashah = ""
            pending_seder = ""
            verses_since_last += 1
    return rows
