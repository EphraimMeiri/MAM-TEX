from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable

from .atoms import Template, flatten, normalize_atom, note_body_from_params, template_to_plain
from .events import Event, Note


def _hebrew_consonants(s: str) -> str:
    """Strip diacritics; keep only Hebrew letters."""
    decomposed = unicodedata.normalize("NFD", s)
    return "".join(c for c in decomposed if "א" <= c <= "ת")


def _nth_letter_index(s: str, n: int) -> int:
    """Index in s of the nth Hebrew letter (0-indexed). -1 if not found."""
    seen = 0
    for i, c in enumerate(s):
        if "א" <= c <= "ת":
            if seen == n:
                return i
            seen += 1
    return -1


def _kq_yod_vav_overlay(ketiv: str, qere: str) -> dict | None:
    """If ketiv/qere differ by exactly one consonant and that swap is י↔ו,
    return overlay info pointing into the qere string."""
    if not ketiv or not qere:
        return None
    k = _hebrew_consonants(ketiv)
    q = _hebrew_consonants(qere)
    if not k or not q or len(k) != len(q):
        return None
    diffs = [(i, kc, qc) for i, (kc, qc) in enumerate(zip(k, q)) if kc != qc]
    if len(diffs) != 1:
        return None
    i, kc, qc = diffs[0]
    if {kc, qc} != {"ו", "י"}:  # vav, yod
        return None
    idx = _nth_letter_index(qere, i)
    if idx < 0:
        return None
    return {"text": qere, "diff_index": idx, "ghost": kc}

EMET_BOOKS = {"ספר תהלים", "ספר משלי", "ספר איוב"}
KQ_NAMES = {
    "כו\"ק",
    "קו\"כ",
    "מ:כו\"ק מיוחד",
    "קו\"כ-אם",
    "מ:קו\"כ-אם-2",
    "כתיב ולא קרי",
    "קרי ולא כתיב",
}

TemplateHandler = Callable[[Template], Iterable[Event]]
TEMPLATE_HANDLERS: dict[str, TemplateHandler] = {}


def register(*names: str):
    def deco(fn: TemplateHandler) -> TemplateHandler:
        for n in names:
            TEMPLATE_HANDLERS[n] = fn
        return fn
    return deco


def book_events(sec: dict) -> Iterable[Event]:
    for book in sec["book39s"]:
        book_name = book["book24_name"]
        yield Event("book", text=book_name)
        for chapter, verses in book["chapters"].items():
            yield Event("chapter", text=chapter, meta={"book": book_name, "emet": book_name in EMET_BOOKS})
            for verse, row in verses.items():
                if verse in {"0", "תתת"}:
                    yield from pseudo_events(row)
                    continue
                d_col, cp_col, ep_col = row
                yield from section_events(d_col)
                yield from cp_events(cp_col)
                yield Event("verse", text=verse)
                yield from text_events(ep_col)
                yield Event("verse_end", meta={"emet": book_name in EMET_BOOKS})


def pseudo_events(row: list) -> Iterable[Event]:
    for atom in row[0]:
        norm = normalize_atom(atom)
        if isinstance(norm, Template) and norm.name in {"מ:שוליים", "מ:טעמי המקרא"}:
            yield Event("display_meta", text=norm.name, meta=norm.params)


_STRUCTURAL_KINDS = {
    "parashah_open", "parashah_closed", "emet_space",
    "section_label", "parashah_banner", "note",
}


def section_events(d_col: list) -> Iterable[Event]:
    for atom in d_col:
        norm = normalize_atom(atom)
        if norm == "__" or norm == "//":
            continue
        # Route through the template registry so נוסח-wrapped פפ/סס flow
        # their variant notes onto the parashah event, and conditional
        # section markers come through cleanly.
        for ev in atom_events(norm):
            if ev.kind in _STRUCTURAL_KINDS:
                yield ev


@register("מ:רווח", "מ:רווח לספר בתהלים", "מ:רווח לספר בתהלים בפסוק הראשון")
def _h_section_label(t: Template) -> Iterable[Event]:
    yield Event(
        "section_label",
        text=flatten(t.params.get("1", "")),
        meta={"template": t.name},
    )


def cp_events(cp_col: list) -> Iterable[Event]:
    for atom in cp_col:
        norm = normalize_atom(atom)
        if isinstance(norm, Template) and norm.name == "מ:פסוק":
            seder = flatten(norm.params.get("סדר", ""))
            if seder:
                yield Event("seder_start", text=seder)
            aliyah = norm.params.get("עלייה")
            # Parashah-start signal in MAM-parsed: "עלייה ראשונה=כן" with the
            # parashah name in "עלייה". (The on-wiki form uses ב1=ראשון/ב0=name
            # via the מ:עלייה sub-template.)
            if flatten(norm.params.get("עלייה ראשונה", "")) == "כן" and aliyah:
                parashah = flatten(aliyah)
                if parashah and not parashah.startswith("["):
                    yield Event("parashah_start", text=parashah)
            else:
                aliyah_norm = normalize_atom(aliyah) if aliyah else None
                if (
                    isinstance(aliyah_norm, Template)
                    and aliyah_norm.name == "מ:עלייה"
                    and flatten(aliyah_norm.params.get("ב1", "")) == "ראשון"
                ):
                    parashah = flatten(aliyah_norm.params.get("ב0", ""))
                    if parashah:
                        yield Event("parashah_start", text=parashah)
            if aliyah:
                label = aliyah_label(aliyah)
                if label:
                    yield Event("aliyah", text=label)


def text_events(atoms: list) -> Iterable[Event]:
    for atom in atoms:
        norm = normalize_atom(atom)
        yield from atom_events(norm)


def atom_events(atom) -> Iterable[Event]:
    if isinstance(atom, str):
        if atom:
            yield Event("text", text=atom)
        return
    if isinstance(atom, list):
        for item in atom:
            yield from atom_events(item)
        return
    if not isinstance(atom, Template):
        yield Event("text", text=str(atom))
        return
    handler = TEMPLATE_HANDLERS.get(atom.name)
    if handler is not None:
        yield from handler(atom)
        return
    rendered = template_to_plain(atom)
    if rendered:
        yield Event("text", text=rendered)


# --- Template handlers -----------------------------------------------------


@register("נוסח")
def _h_nusach(t: Template) -> Iterable[Event]:
    body = note_body_from_params(t)
    target = flatten(t.params.get("1", ""))
    inner = list(atom_events(t.params.get("1", "")))
    # If the inner content already produced its own note (K/Q, special_letter,
    # editorial), suppress it: the outer variant note describes the same span
    # and would otherwise double-mark the verse.
    inner = [e for e in inner if e.kind != "note"]
    # If the variant wraps a parashah break, attach the body onto the section
    # event instead of emitting a separate dangling note.
    if body and inner and inner[-1].kind in {"parashah_open", "parashah_closed"}:
        last = inner[-1]
        inner[-1] = Event(
            last.kind, last.text,
            meta={**last.meta, "variant_note": body, "variant_target": target},
        )
        body = ""
    yield from inner
    if body:
        yield Event("note", note=Note("nusach", "נוסח", body, target, {"template": t.name}))


@register(*KQ_NAMES, "מ:כו\"ק כתיב מילה חדה וקרי תרתין מילין",
          "מ:קו\"כ כתיב מילה חדה וקרי תרתין מילין",
          "מ:כו\"ק כתיב מילה חדה וקרי תרתין מילין בין שני מקפים",
          "מ:כו\"ק בין שני מקפים",
          "מ:כו\"ק של שתי מילים בהערה אחת",
          "מ:כו\"ק כתיב תרתין מילין וקרי מילה חדה",
          "מ:קו\"כ קרי שונה מהכתיב בשתי מילים",
          "מ:כו\"ק קרי שונה מהכתיב בשתי מילים")
def _h_kq(t: Template) -> Iterable[Event]:
    p = t.params
    p1 = flatten(p.get("1", ""))
    p2 = flatten(p.get("2", ""))
    if t.name == "כו\"ק":
        ketiv, qere = p1, p2
    elif t.name in {"קו\"כ", "מ:כו\"ק מיוחד"}:
        ketiv, qere = p2, p1
    else:
        ketiv = qere = ""
    overlay = _kq_yod_vav_overlay(ketiv, qere)
    if overlay:
        yield Event("kq_inline", text=overlay["text"],
                    meta={"diff_index": overlay["diff_index"], "ghost": overlay["ghost"]})
    else:
        yield Event("text", text=template_to_plain(t))
    target, body = _kq_lemma_and_body(t)
    yield Event("note", note=Note("ketiv_qere", "קרי/כתיב", body, target, {"template": t.name}))


def _kq_lemma_and_body(t: Template) -> tuple[str, str]:
    """Return (lemma_for_header, body_text) for a K/Q template.

    The header carries both forms in '(ketiv) qere' order whenever both are
    available; the body is reserved for additional commentary parameters.
    """
    p = t.params
    p1 = flatten(p.get("1", ""))
    p2 = flatten(p.get("2", ""))
    if t.name == "כתיב ולא קרי":
        return f"({p1})", ""
    if t.name == "קרי ולא כתיב":
        return p1, "(קרי ולא כתיב)"
    if t.name in {"כו\"ק", "קו\"כ", "מ:כו\"ק מיוחד"}:
        ketiv, qere = (p1, p2) if t.name == "כו\"ק" else (p2, p1)
        if ketiv and qere:
            target = f"({ketiv}) {qere}"
        else:
            target = ketiv or qere
        body = note_body_from_params(t, start=3)
        return target, body
    target = p1 or p2
    return target, note_body_from_params(t, start=3)


@register("מ:אות-ג")
def _h_big_letter(t: Template) -> Iterable[Event]:
    text = flatten(t.params.get("1", ""))
    yield Event("big_letter", text=text, meta={"template": t.name})
    yield Event("note", note=Note("special_letter", "אות גדולה", t.name, text, {"template": t.name}))


@register("מ:אות-ק")
def _h_small_letter(t: Template) -> Iterable[Event]:
    text = flatten(t.params.get("1", ""))
    yield Event("small_letter", text=text, meta={"template": t.name})
    yield Event("note", note=Note("special_letter", "אות קטנה", t.name, text, {"template": t.name}))


@register("מ:אות תלויה")
def _h_suspended_letter(t: Template) -> Iterable[Event]:
    text = flatten(t.params.get("1", ""))
    yield Event("suspended_letter", text=text, meta={"template": t.name})
    yield Event("note", note=Note("special_letter", "אות תלויה", t.name, text, {"template": t.name}))


@register("מ:אות מנוקדת")
def _h_dotted_letter(t: Template) -> Iterable[Event]:
    text = flatten(t.params.get("1", ""))
    yield Event("dotted_letter", text=text, meta={"template": t.name})
    yield Event("note", note=Note("special_letter", "אות מנוקדת", t.name, text, {"template": t.name}))


@register("מ:אות-מיוחדת-במילה")
def _h_special_word_letter(t: Template) -> Iterable[Event]:
    text = flatten(t.params.get("1", t.params.get("2", "")))
    yield Event("text", text=text)
    yield Event("note", note=Note("special_letter", "אות מיוחדת", t.name, text, {"template": t.name}))


@register("מ:פסק", "מ:לגרמיה", "מ:לגרמיה-2")
def _h_pasek(t: Template) -> Iterable[Event]:
    yield Event("pasek", text=t.name)


@register("ר0", "ר1", "ר2", "ר3", "ר4")
def _h_emet(t: Template) -> Iterable[Event]:
    yield Event("emet_space", text=t.name)


@register("פפ", "פפפ")
def _h_parashah_open(t: Template) -> Iterable[Event]:
    yield Event("parashah_open")


@register("סס", "ססס", "סס2")
def _h_parashah_closed(t: Template) -> Iterable[Event]:
    yield Event("parashah_closed")


@register("פסקא באמצע פסוק")
def _h_pisqa_mid(t: Template) -> Iterable[Event]:
    yield Event("mid_pasuq_gap")
    yield from atom_events(t.params.get("1", ""))


@register("מ:ירושלם")
def _h_yerushalem(t: Template) -> Iterable[Event]:
    p1 = flatten(t.params.get("1", ""))
    p2 = flatten(t.params.get("2", ""))
    yield Event("text", text=p1 + p2 + "͏ִם")  # ירושל + (CGJ + chiriq + mem) approximating wiki overlay


@register("מ:קמץ")
def _h_kamatz(t: Template) -> Iterable[Event]:
    yield Event("text", text=flatten(t.params.get("1", "")))


@register("פרשה-מרכז")
def _h_parashah_banner(t: Template) -> Iterable[Event]:
    label = flatten(t.params.get("1", ""))
    yield Event("parashah_banner", text=label, meta={"template": t.name})


@register("מ:הערה")
def _h_inline_note(t: Template) -> Iterable[Event]:
    body = note_body_from_params(t, start=1)
    if body:
        yield Event("note", note=Note("editorial", "הערה", body, "", {"template": t.name}))


@register("מ:אין פרשה בתחילת פרק", "מ:אין פרשה בתחילת פרק בספרי אמ\"ת")
def _h_suppress(t: Template) -> Iterable[Event]:
    return
    yield  # pragma: no cover  (make this a generator)


def aliyah_label(value) -> str:
    value = normalize_atom(value)
    if isinstance(value, Template) and value.name == "מ:עלייה":
        label = flatten(value.params.get("א", ""))
        return label if label.startswith("[") else ""
    label = flatten(value)
    return label if label.startswith("[") else ""
