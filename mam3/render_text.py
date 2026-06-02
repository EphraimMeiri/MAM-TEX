from __future__ import annotations

from collections.abc import Callable, Iterable

from .events import Event, Note


NoteFilter = Callable[[Note], bool]


def render_text(events: Iterable[Event], notes: NoteFilter | None = None) -> str:
    out: list[str] = []
    pending_notes: list[Note] = []
    for event in events:
        if event.kind == "book":
            out.append(f"\n\n{event.text}\n")
        elif event.kind == "chapter":
            out.append(f"\n\nפרק {event.text}\n")
        elif event.kind == "verse":
            out.append(f"{event.text} ")
        elif event.kind == "text":
            out.append(event.text)
        elif event.kind == "parashah_open":
            out.append("\n\n{פ} ")
        elif event.kind == "parashah_closed":
            out.append(" {ס} ")
        elif event.kind == "emet_space":
            out.append(_emet_text_space(event.text))
        elif event.kind == "verse_end":
            if notes:
                rendered = [note for note in pending_notes if notes(note)]
                if rendered:
                    out.append(" [" + " || ".join(f"{n.label}: {n.body}" for n in rendered) + "]")
            pending_notes.clear()
            out.append("\n")
        elif event.kind == "note" and event.note:
            pending_notes.append(event.note)
    return "".join(out).strip() + "\n"


def _emet_text_space(name: str) -> str:
    if name in {"ר2", "ר3", "ר4"}:
        return "\n    "
    if name == "ר1":
        return "    "
    return " "
