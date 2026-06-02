from __future__ import annotations

from collections.abc import Callable, Iterable

from .events import Event, Note


NoteFilter = Callable[[Note], bool]


def render_tex(events: Iterable[Event], notes: NoteFilter | None = None) -> str:
    out = [PREAMBLE]
    pending_notes: list[Note] = []
    in_pstart = False
    for event in events:
        if event.kind == "book":
            if in_pstart:
                out.append("\\pend\n")
                in_pstart = False
            out.append(f"\n\\section*{{{tex_escape(event.text)}}}\n")
        elif event.kind == "chapter":
            if in_pstart:
                out.append("\\pend\n")
            out.append(f"\n\\subsection*{{\\textcolor{{red}}{{פרק {tex_escape(event.text)}}}}}\n\\pstart\n")
            in_pstart = True
        elif event.kind == "verse":
            out.append(f"{{\\loc{{{tex_escape(event.text)}}}}} ")
        elif event.kind == "text":
            out.append(tex_escape(event.text))
        elif event.kind == "parashah_open":
            out.append("\\par\\smallskip\\noindent {\\locf{פ}} ")
        elif event.kind == "parashah_closed":
            out.append("\\hspace{2em}{\\locf{ס}}\\hspace{1em}")
        elif event.kind == "emet_space":
            out.append(_emet_tex_space(event.text))
        elif event.kind == "note" and event.note:
            pending_notes.append(event.note)
        elif event.kind == "verse_end":
            if notes:
                for note in pending_notes:
                    if notes(note):
                        out.append(f"\\ledsidenote{{\\scriptsize {tex_escape(note.label)}: {tex_escape(note.body)}}}")
            pending_notes.clear()
            out.append("\n")
    if in_pstart:
        out.append("\\pend\n")
    out.append(POSTAMBLE)
    return "".join(out)


def tex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def _emet_tex_space(name: str) -> str:
    if name in {"ר2", "ר3", "ר4"}:
        return "\\newline\\hspace*{1em}"
    if name == "ר1":
        return "\\hfill "
    return "\\hspace{1em}"


PREAMBLE = r"""\documentclass[12pt]{article}
\usepackage[paperwidth=5.5in,paperheight=8.5in,top=.5in,bottom=.75in]{geometry}
\usepackage{polyglossia}
\usepackage{xcolor}
\usepackage[series={A,B},noend,noeledsec,nofamiliar]{reledmac}
\setdefaultlanguage[numerals=arabic]{hebrew}
\newfontfamily\hebrewfont[Script=Hebrew,Path=/Users/ephraimmeiri/Library/Fonts/]{SBL_Hbrw.ttf}
\newfontfamily\locf[Script=Hebrew,Path=/Users/ephraimmeiri/Library/Fonts/]{SBL_Hbrw.ttf}
\newcommand{\loc}[1]{\textsuperscript{\locf{#1}}}
\setlength{\parindent}{0pt}
\begin{document}
\beginnumbering
"""

POSTAMBLE = r"""
\endnumbering
\end{document}
"""
