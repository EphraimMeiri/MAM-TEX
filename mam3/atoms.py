from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Template:
    name: str
    params: dict[str, Any]


def normalize_atom(atom: Any) -> str | Template | list[Any]:
    if isinstance(atom, Template):
        return Template(atom.name, {
            str(k): normalize_atom(v)
            for k, v in atom.params.items()
        })
    if isinstance(atom, str):
        return atom
    if isinstance(atom, list):
        return [normalize_atom(item) for item in atom]
    if not isinstance(atom, dict):
        return str(atom)
    if "stmpl" in atom:
        return parse_stmpl(atom["stmpl"])
    if "tmpl_name" in atom:
        return Template(atom["tmpl_name"], {
            str(k): normalize_atom(v)
            for k, v in atom.get("tmpl_params", {}).items()
        })
    if "tmpl" in atom:
        return parse_tmpl(atom["tmpl"])
    if "custom_tag" in atom:
        return Template("custom_tag", {"1": atom["custom_tag"]})
    if "unparseable" in atom:
        return Template("unparseable", {"1": atom["unparseable"]})
    return str(atom)


def parse_stmpl(value: str) -> Template:
    parts = value.split("|")
    params: dict[str, Any] = {}
    for index, raw in enumerate(parts[1:], start=1):
        if "=" in raw:
            key, val = raw.split("=", 1)
            if key:
                params[key] = val
                continue
        params[str(index)] = raw
    return Template(parts[0], params)


def parse_tmpl(value: list[Any]) -> Template:
    name = flatten(value[0])
    params: dict[str, Any] = {}
    for index, raw in enumerate(value[1:], start=1):
        if raw and isinstance(raw[0], str) and "=" in raw[0]:
            key, val = raw[0].split("=", 1)
            if key:
                rest = raw[1:]
                params[key] = normalize_atom([val, *rest]) if rest else val
                continue
        params[str(index)] = normalize_atom(raw)
    return Template(name, params)


def flatten(value: Any) -> str:
    value = normalize_atom(value)
    if isinstance(value, str):
        return value
    if isinstance(value, Template):
        return template_to_plain(value)
    if isinstance(value, list):
        return "".join(flatten(item) for item in value)
    return str(value)


def template_to_plain(tmpl: Template) -> str:
    name = tmpl.name
    p = tmpl.params
    if name == "נוסח":
        return flatten(p.get("1", ""))
    if name in {"כו\"ק", "קו\"כ", "מ:כו\"ק מיוחד", "כתיב ולא קרי"}:
        return f"({flatten(p.get('1', ''))})"
    if name == "קרי ולא כתיב":
        return "()"
    if name in {"קו\"כ-אם", "מ:קו\"כ-אם-2"}:
        return flatten(p.get("1", ""))
    if name == "מ:אות-ג":
        return flatten(p.get("1", ""))
    if name == "מ:אות-ק":
        return flatten(p.get("1", ""))
    if name == "מ:אות תלויה":
        return flatten(p.get("1", ""))
    if name == "מ:אות-מיוחדת-במילה":
        return flatten(p.get("1", p.get("2", "")))
    if name == "מ:עלייה":
        return flatten(p.get("א", ""))
    if name in {"מ:קמץ", "מ:דחי"}:
        return flatten(p.get("1", ""))
    if name in {"מ:לגרמיה", "מ:לגרמיה-2", "מ:פסק"}:
        return " | "
    if name in {"ירח בן יומו", "גלגל"}:
        return "֪"
    if name == "מ:גרשיים ותלישא גדולה":
        return "֞֠"
    if name == "מ:טעם ומתג באות אחת":
        return "͏ֽ"
    if name == "אתנח הפוך":
        return "֢"
    if name == "מ:נו\"ן הפוכה":
        return "׆"
    if name == "מ:מקף אפור":
        return " "
    if name == "שני טעמים באות אחת":
        return flatten(p.get("1", "")) + flatten(p.get("2", ""))
    if name in {"ר0", "ר1", "ר2", "ר3", "ר4"}:
        return ""
    if name in {"ש"}:
        return " | "
    return flatten(p.get("1", ""))


def note_body_from_params(tmpl: Template, start: int = 2) -> str:
    chunks = []
    for key in sorted(tmpl.params, key=_param_sort):
        if key.isdigit() and int(key) < start:
            continue
        chunks.append(flatten(tmpl.params[key]))
    return " | ".join(chunk for chunk in chunks if chunk)


def _param_sort(key: str) -> tuple[int, str]:
    return (int(key), "") if key.isdigit() else (1000, key)
