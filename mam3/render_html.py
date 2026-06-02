from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Iterable
from html import escape

from .events import Event, Note


def _kq_inline_html(text: str, diff_index: int, ghost: str) -> str:
    """Wrap the differing letter in a .kq-swap span containing both the
    ghost (ketiv) and qere letters as siblings, so the ghost is real text
    that the browser can render with the verse font."""
    if diff_index < 0 or diff_index >= len(text):
        return escape(text)
    end = diff_index + 1
    while end < len(text) and unicodedata.combining(text[end]):
        end += 1
    before = escape(text[:diff_index])
    letter = escape(text[diff_index:end])
    after = escape(text[end:])
    return (
        before
        + '<span class="kq-swap">'
        + f'<span class="kq-ghost" aria-hidden="true">{escape(ghost)}</span>'
        + f'<span class="kq-qere">{letter}</span>'
        + "</span>"
        + after
    )


_HEB_LETTER = "א-ת־"  # letters + maqaf
_HEB_DIACRITIC = "֑-ׇֽֿׁׂׄ"
_HEB_WORD_RE = re.compile(f"[{_HEB_LETTER}{_HEB_DIACRITIC}]+")
_DIACRITIC_RE = re.compile(f"[{_HEB_DIACRITIC}]")


def _style_note_text(text: str) -> str:
    out: list[str] = []
    i = 0
    for m in _HEB_WORD_RE.finditer(text):
        if m.start() > i:
            out.append(escape(text[i:m.start()]))
        word = m.group(0)
        if _DIACRITIC_RE.search(word):
            out.append(
                f'<span class="hebw" lang="hbo">{escape(word)}</span>'
            )
        else:
            out.append(escape(word))
        i = m.end()
    if i < len(text):
        out.append(escape(text[i:]))
    return "".join(out)


NoteFilter = Callable[[Note], bool]

NOTE_MARKS = {
    "nusach": "נ",
    "ketiv_qere": "קק",
    "special_letter": "א",
    "editorial": "•",
}


def render_html(
    events: Iterable[Event],
    notes: NoteFilter | None = None,
    nav_html: str = "",
    title: str = "מקרא על פי המסורה",
) -> str:
    body: list[str] = []
    para_bits: list[str] = []
    verse_bits: list[str] = []
    pending_notes: list[Note] = []
    pending_aliyah = ""
    pending_break = ""
    open_verse = False
    in_paragraph = False
    in_chapter = False
    book_name = ""
    chapter_name = ""
    chapter_first_verse = False

    def flush_paragraph() -> None:
        nonlocal in_paragraph
        if not in_paragraph:
            return
        body.append("<div class=\"ws-margins\"><div class=\"ws-text\" lang=\"hbo\" dir=\"rtl\">\n<p>\n")
        body.extend(para_bits)
        body.append("\n</p>\n</div></div>\n")
        para_bits.clear()
        in_paragraph = False

    def close_chapter() -> None:
        nonlocal in_chapter
        flush_paragraph()
        if in_chapter:
            body.append("</section>\n")
            in_chapter = False

    def close_verse() -> None:
        nonlocal open_verse
        para_bits.append("".join(verse_bits))
        para_bits.append("\n")
        verse_bits.clear()
        pending_notes.clear()
        open_verse = False

    def emit_note(note: Note) -> None:
        keep = notes if notes is not None else (lambda _n: True)
        if not keep(note):
            return
        mark = NOTE_MARKS.get(note.kind, "‡")
        head_pieces: list[str] = []
        if note.kind != "nusach":
            head_pieces.append(f"<b>{escape(note.label)}</b>")
        if note.target:
            head_pieces.append(
                f'<span class="lemma" lang="hbo">{escape(note.target)}</span>'
            )
        body_pieces = [
            _style_note_text(chunk.strip())
            for chunk in note.body.split("|")
            if chunk.strip()
        ]
        # Estimate plain-text length to decide compact vs stacked
        plain_total = sum(len(p) for p in (
            note.label if note.kind != "nusach" else "",
            note.target,
            note.body,
        ))
        compact = (len(body_pieces) <= 1) and (plain_total < 80)
        if compact:
            inline = " · ".join(head_pieces + body_pieces)
            body_html = f'<span class="np compact">{inline}</span>'
        else:
            parts = []
            if head_pieces:
                parts.append(
                    f'<span class="np head">{" · ".join(head_pieces)}</span>'
                )
            for bp in body_pieces:
                parts.append(f'<span class="np">{bp}</span>')
            body_html = "".join(parts)
        klass = f"note {escape(note.kind)}"
        if compact:
            klass += " compact-note"
        verse_bits.append(
            f'<span class="{klass}" tabindex="0">'
            f'<sup class="note-mark">{escape(mark)}</sup>'
            f'<span class="note-body">{body_html}</span>'
            "</span>"
        )

    def open_verse_marker(verse: str) -> str:
        nonlocal pending_aliyah, chapter_first_verse
        aliyah_letter_html = ""
        aliyah_name_html = ""
        if pending_aliyah:
            aliyah_name_html = (
                f"<span class=\"visual-only\" style=\"font-size: 0.6em; color: #016200;\">"
                f"<b>{escape(pending_aliyah)}</b></span>"
            )
            pending_aliyah = ""
        left = (
            "<span class=\"visual-only\" style=\"white-space: nowrap; float: left; margin-left: -3em;\">"
            f"<span style=\"color: #800000;\">{aliyah_letter_html}</span> "
            f"{aliyah_name_html}</span>"
        )
        chapter_link = ""
        if chapter_first_verse:
            chapter_link = (
                "<span class=\"visual-only\" style=\"float: right; margin-right: -3.2em; "
                "text-align: left; width: 3em;\">"
                f"<span class=\"chapter-num\">{escape(chapter_name)}</span></span>"
            )
            chapter_first_verse = False
        right = (
            "<span class=\"visual-only\" style=\"white-space: nowrap;\">"
            "<span style=\"float: right; clear: right; margin-right: -1em; "
            "width: 0; height: 0.5em;\">"
            f"{chapter_link}"
            f"<span style=\"font-size: 0.6em;\">{escape(verse)}</span>"
            "</span></span>"
        )
        anchor = f"<span id=\"v-{escape(chapter_name)}-{escape(verse)}\"></span>"
        copy = f"<span class=\"vnum-copy\">{escape(verse)} </span>"
        return left + right + anchor + copy

    def emit_break() -> None:
        nonlocal pending_break
        if not pending_break or not in_paragraph:
            return
        label = "{פ}" if pending_break == "open" else "{ס}"
        klass = "parashah-mark " + pending_break
        gap = "　　" if pending_break == "open" else "　　　"
        marker = (
            f"<span class=\"{klass}\" "
            "style=\"white-space: nowrap; float: left; margin-left: -3em;\">"
            f"<span class=\"visual-only\" style=\"color: #800000;\">{label}</span>"
            "</span>"
        )
        para_bits.append(f"<br>{marker}{gap}<br>\n")
        pending_break = ""

    for event in events:
        kind = event.kind
        if kind == "book":
            close_chapter()
            book_name = event.text
            body.append(
                "<header class=\"page-head\">"
                f"<div class=\"eyebrow\">מקרא על פי המסורה</div>"
                f"<h1>{escape(book_name)}</h1>"
                "</header>\n"
            )
        elif kind == "chapter":
            close_chapter()
            chapter_name = event.text
            chapter_first_verse = True
            cls = "chapter"
            if event.meta.get("emet"):
                cls += " emet"
            body.append(
                f'<section class="{cls}" id="ch-'
                f"{escape(chapter_name)}\">\n"
                f"<h2>פרק {escape(chapter_name)}</h2>\n"
            )
            in_chapter = True
        elif kind == "verse":
            if not in_paragraph:
                in_paragraph = True
            emit_break()
            open_verse = True
            verse_bits.append(open_verse_marker(event.text))
        elif kind == "text":
            verse_bits.append(escape(event.text))
        elif kind == "kq_inline":
            verse_bits.append(
                _kq_inline_html(
                    event.text,
                    event.meta.get("diff_index", -1),
                    event.meta.get("ghost", ""),
                )
            )
        elif kind == "big_letter":
            verse_bits.append(f"<big><b>{escape(event.text)}</b></big>")
        elif kind == "small_letter":
            verse_bits.append(f"<small>{escape(event.text)}</small>")
        elif kind == "suspended_letter":
            verse_bits.append(
                f"<span class=\"suspended-letter\">{escape(event.text)}</span>"
            )
        elif kind == "dotted_letter":
            verse_bits.append(
                f"<span class=\"dotted-letter\">{escape(event.text)}</span>"
            )
        elif kind == "mid_pasuq_gap":
            verse_bits.append("<span class=\"mid-pasuq-gap\"> </span>")
        elif kind == "parashah_banner":
            flush_paragraph()
            body.append(
                f"<div class=\"parashah-banner\">{escape(event.text)}</div>\n"
            )
        elif kind == "pasek":
            verse_bits.append(
                " <small><small><span style=\"color:Gray;\">׀</span>"
                "</small></small> "
            )
        elif kind == "parashah_open":
            pending_break = "open"
            note_body = event.meta.get("variant_note")
            if note_body:
                emit_note(Note("nusach", "נוסח", note_body,
                               event.meta.get("variant_target", ""),
                               {"on_section": "open"}))
        elif kind == "parashah_closed":
            pending_break = "closed"
            note_body = event.meta.get("variant_note")
            if note_body:
                emit_note(Note("nusach", "נוסח", note_body,
                               event.meta.get("variant_target", ""),
                               {"on_section": "closed"}))
        elif kind == "aliyah":
            pending_aliyah = event.text
        elif kind == "parashah_start":
            # Display-only event for inline rendering; data tables read this
            # via the section walker. No-op for now.
            pass
        elif kind == "emet_space":
            verse_bits.append(_emet_html_space(event.text))
        elif kind == "note" and event.note:
            emit_note(event.note)
        elif kind == "verse_end" and open_verse:
            close_verse()
    close_chapter()
    return HTML.format(body="".join(body), nav=nav_html, title=escape(title))


def _emet_html_space(name: str) -> str:
    indents = {"ר1": 0, "ר2": 2, "ר3": 4, "ר4": 6}
    if name in indents:
        em = indents[name]
        if em:
            return f'<br><span style="display:inline-block;width:{em}em;"></span>'
        return "<br>"
    # ר0 — within-line gap (no break)
    return '<span style="display:inline-block;width:1.5em;"></span>'


HTML = """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
:root {{ color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #fffdfa; color: #1f1b18; font-family: -apple-system, "Segoe UI", "Arial Hebrew", sans-serif; }}
.page-head {{ max-width: 60rem; margin: 0 auto; padding: 1.5rem 2rem .25rem; text-align: center; border-bottom: 1px solid #d8d0c8; }}
.eyebrow {{ color: #6f635c; font-size: .85rem; }}
.page-head h1 {{ margin: .25rem 0 .75rem; color: #8b1d1d; font-size: 1.6rem; }}
.chapter {{ max-width: 72rem; margin: 0 auto; padding: 1.5rem 5em 3rem; }}
.chapter.emet {{ max-width: 88rem; padding-left: 3em; padding-right: 3em; }}
.chapter h2 {{ color: #8b1d1d; text-align: center; font-size: 1.15rem; margin: 0 0 1rem; }}
.ws-margins {{ margin-left: 8em; margin-right: 6em; }}
.chapter.emet .ws-margins {{ margin-left: 5em; margin-right: 4em; }}
.vnum-copy {{ font-size: 0; line-height: 0; }}
.visual-only {{ user-select: none; -webkit-user-select: none; }}
.suspended-letter {{ font-size: .8em; vertical-align: .5em; }}
.dotted-letter {{ position: relative; }}
.dotted-letter::before {{
  content: "·"; position: absolute; top: -.55em; left: 50%;
  transform: translateX(-50%); font-size: .8em; line-height: 1;
}}
.mid-pasuq-gap {{ display: inline-block; width: 2em; }}
.kq-swap {{
  position: relative;
  display: inline-block;
}}
.kq-ghost {{
  position: absolute;
  inset-inline-end: 0;
  top: 0;
  color: #b9a89a;
  opacity: .55;
  pointer-events: none;
  user-select: none;
}}
.kq-qere {{
  color: #1e6fb8;
  position: relative;
}}
.parashah-banner {{
  text-align: center; color: #8b1d1d;
  font-weight: 700; margin: 1.25rem 0 .5rem;
  font-family: -apple-system, "Segoe UI", "Arial Hebrew", sans-serif;
}}
.ws-text {{
  font-family: "Taamey Frank CLM", "Keter YG", "SBL Hebrew", "Ezra SIL SR", "Ezra SIL", "Arial Unicode MS", serif;
  font-size: 23pt;
  line-height: 150%;
}}
.ws-text p {{ text-align: justify; margin: 0; }}
.chapter-num {{ color: #8b1d1d; font-weight: 700; }}
/* Note marks: tiny superscript markers next to the verse */
.note {{ position: relative; }}
.note-mark {{
  display: none;
  font-family: -apple-system, "Segoe UI", "Arial Hebrew", sans-serif;
  font-size: .42em; color: #8b1d1d; vertical-align: super;
  margin: 0 .12em; cursor: pointer; user-select: none;
}}
.note-body {{ display: none; }}
.note-body .lemma,
.note-body .hebw {{
  font-family: "Taamey Frank CLM", "Keter YG", "SBL Hebrew", "Ezra SIL SR", serif;
}}
.note-body .lemma {{ font-weight: 700; color: #1f1b18; }}
.note-body .np {{ display: block; margin: .2em 0; }}
.note-body .np.head {{
  text-align: center; margin-bottom: .35em;
  border-bottom: 1px solid #e6dfd7; padding-bottom: .2em;
}}
.note-body .np.head b {{ color: #8b1d1d; }}
.note-body .np.compact {{ display: block; margin: 0; }}
.note-body .np.compact b {{ color: #8b1d1d; }}
body.notes-tooltip .note-mark,
body.notes-shoulder .note-mark,
body.notes-footer .note-mark {{ display: inline; }}

/* Tooltip mode: popover on hover/focus */
body.notes-tooltip .note:hover .note-body,
body.notes-tooltip .note:focus-within .note-body {{
  display: block; position: absolute; z-index: 20;
  top: 1.4em; right: 0; min-width: 22em; max-width: 32em;
  padding: .55rem .75rem; font-size: 1rem; line-height: 1.4;
  font-family: -apple-system, "Segoe UI", "Arial Hebrew", sans-serif;
  color: #1f1b18; background: #fffdfa;
  border: 1px solid #d8d0c8; border-radius: 4px;
  box-shadow: 0 4px 14px rgba(0,0,0,.12);
}}

/* Shoulder mode: notes float into the left margin */
body.notes-shoulder .note-body {{
  display: block; position: relative;
  float: left; clear: left;
  width: 16em; margin-left: -18em; margin-top: .25em;
  padding: .4rem .55rem; font-size: .85rem; line-height: 1.35;
  font-family: -apple-system, "Segoe UI", "Arial Hebrew", sans-serif;
  color: #1f1b18; background: #f9f5ee;
  border: 1px solid #e6dfd7; border-radius: 3px;
  cursor: pointer;
}}
body.notes-shoulder .ws-margins {{ margin-left: 20em; }}
body.notes-shoulder .note-body::after {{
  content: "▾"; position: absolute; top: .2rem; left: .35rem;
  color: #b9a89a; font-size: .9em; pointer-events: none;
  transition: transform .12s ease-out;
}}
body.notes-shoulder .note.collapsed .note-body::after {{
  transform: rotate(-90deg);
}}
body.notes-shoulder .note.collapsed .note-body .np:not(.head):not(.compact) {{
  display: none;
}}
body.notes-shoulder .note-body {{
  max-height: 18em; overflow: auto;
}}
body.notes-shoulder .note.compact-note .note-body::after {{ display: none; }}
body.notes-shoulder .note.compact-note .note-body {{
  cursor: default; padding-left: .55rem;
}}

/* Footer popup mode: clicking a mark fills #note-pane */
.note-pane {{
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 30;
  max-height: 35vh; overflow: auto; padding: .9rem 1.5rem;
  background: #fffdfa; border-top: 1px solid #d8d0c8;
  box-shadow: 0 -4px 14px rgba(0,0,0,.08);
  font-family: -apple-system, "Segoe UI", "Arial Hebrew", sans-serif;
  font-size: 1rem; line-height: 1.45; color: #1f1b18;
  transform: translateY(100%); transition: transform .15s ease-out;
}}
#note-pane-body {{ position: relative; }}
.note-pane.open {{ transform: translateY(0); }}
.note-pane b {{ color: #8b1d1d; }}
.note-pane .close {{
  position: absolute; top: .5rem; left: .75rem;
  background: transparent; border: 0; cursor: pointer;
  color: #6f635c; font-size: 1.1rem;
}}

.note-toggle {{
  position: fixed; top: .75rem; left: .75rem; z-index: 40;
  display: flex; flex-direction: column; gap: .15rem;
  background: #fff; border: 1px solid #d8d0c8; border-radius: 4px;
  padding: .35rem .55rem; font-size: .8rem;
  font-family: -apple-system, "Segoe UI", "Arial Hebrew", sans-serif;
}}
.note-toggle legend {{
  font-weight: 700; color: #8b1d1d; padding: 0 .25em;
  font-size: .75rem;
}}
.note-toggle label {{
  display: flex; gap: .35rem; align-items: center;
  cursor: pointer; padding: .05rem 0;
}}
.note-toggle input[type="radio"] {{ margin: 0; }}
.chapter-nav {{
  display: flex; justify-content: space-between; gap: 1rem;
  max-width: 60rem; margin: .25rem auto; padding: .5rem 2rem;
  font-size: .9rem;
}}
.chapter-nav a {{
  color: #8b1d1d; text-decoration: none;
  padding: .35rem .7rem; border: 1px solid #d8d0c8; border-radius: 4px;
  background: #fff;
}}
.chapter-nav a:hover {{ background: #f4efe8; }}
.chapter-nav a.disabled {{
  color: #b9b1a8; pointer-events: none; background: transparent;
}}
.chapter-nav .up {{ flex: 0 0 auto; text-align: center; }}
.chapter-nav .prev {{ flex: 1; text-align: right; }}
.chapter-nav .next {{ flex: 1; text-align: left; }}
@media (max-width: 820px) {{
  .chapter {{ padding-inline: 1.5rem; }}
  .chapter > div {{ margin-left: 1.5em; margin-right: 1.5em; }}
  .ws-text {{ font-size: 18pt; }}
}}
</style>
</head>
<body>
<fieldset class="note-toggle" id="note-toggle">
  <legend>הערות</legend>
  <label><input type="radio" name="notes-mode" value="off"> מוסתרות</label>
  <label><input type="radio" name="notes-mode" value="tooltip"> ריחוף</label>
  <label><input type="radio" name="notes-mode" value="shoulder"> שוליים</label>
  <label><input type="radio" name="notes-mode" value="footer"> חלון תחתון</label>
</fieldset>
<aside id="note-pane" class="note-pane" aria-hidden="true">
  <button class="close" type="button" aria-label="סגור">×</button>
  <div id="note-pane-body"></div>
</aside>
{nav}
{body}
{nav}
<script>
(function() {{
  var form = document.getElementById('note-toggle');
  var pane = document.getElementById('note-pane');
  var paneBody = document.getElementById('note-pane-body');
  var paneClose = pane.querySelector('.close');
  var KEY = 'mam3:notes-mode';
  var MODES = ['off', 'tooltip', 'shoulder', 'footer'];
  function apply(mode) {{
    if (MODES.indexOf(mode) < 0) mode = 'off';
    MODES.forEach(function (m) {{
      document.body.classList.toggle('notes-' + m, m === mode && m !== 'off');
    }});
    var input = form.querySelector('input[value="' + mode + '"]');
    if (input) input.checked = true;
    if (mode !== 'footer') closePane();
    try {{ localStorage.setItem(KEY, mode); }} catch (e) {{}}
    if (mode === 'shoulder') autoCollapseShoulder();
  }}
  function autoCollapseShoulder() {{
    var notes = Array.prototype.slice.call(document.querySelectorAll('.note'));
    notes.forEach(function (n) {{ n.classList.remove('collapsed'); }});
    requestAnimationFrame(function () {{
      // A card is "in the way" if its body bottom extends past the next
      // note's inline anchor (with a small tolerance), or — for the final
      // note — past the chapter's bottom.
      var TOL = 24;
      var changed = true, safety = 400;
      while (changed && safety-- > 0) {{
        changed = false;
        for (var i = 0; i < notes.length; i++) {{
          if (notes[i].classList.contains('collapsed')) continue;
          var body = notes[i].querySelector('.note-body');
          if (!body) continue;
          var myBottom = body.getBoundingClientRect().bottom;
          var limit;
          if (i + 1 < notes.length) {{
            var nextMark = notes[i + 1].querySelector('.note-mark');
            if (!nextMark) continue;
            limit = nextMark.getBoundingClientRect().top;
          }} else {{
            var section = notes[i].closest('.chapter');
            limit = section
              ? section.getBoundingClientRect().bottom
              : document.documentElement.getBoundingClientRect().bottom;
          }}
          if (myBottom > limit + TOL) {{
            notes[i].classList.add('collapsed');
            changed = true;
            break;
          }}
        }}
      }}
    }});
  }}
  var resizeTimer = 0;
  window.addEventListener('resize', function () {{
    if (!document.body.classList.contains('notes-shoulder')) return;
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(autoCollapseShoulder, 120);
  }});
  function openPane(html) {{
    paneBody.innerHTML = html;
    pane.classList.add('open');
    pane.setAttribute('aria-hidden', 'false');
  }}
  function closePane() {{
    pane.classList.remove('open');
    pane.setAttribute('aria-hidden', 'true');
  }}
  paneClose.addEventListener('click', closePane);
  document.addEventListener('click', function (e) {{
    var note = e.target.closest && e.target.closest('.note');
    if (!note) return;
    if (document.body.classList.contains('notes-footer')) {{
      var body = note.querySelector('.note-body');
      if (body) {{
        e.preventDefault();
        openPane(body.innerHTML);
      }}
    }} else if (document.body.classList.contains('notes-shoulder')) {{
      if (note.classList.contains('compact-note')) return;
      e.preventDefault();
      note.classList.toggle('collapsed');
    }}
  }});
  form.addEventListener('change', function (e) {{
    if (e.target && e.target.name === 'notes-mode') apply(e.target.value);
  }});
  var stored = 'off';
  try {{ stored = localStorage.getItem(KEY) || 'off'; }} catch (e) {{}}
  apply(stored);
}})();
</script>
</body>
</html>
"""
