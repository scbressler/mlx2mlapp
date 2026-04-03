"""
parser.py — Parse a MATLAB LiveScript (.mlx) file into an IR.

The .mlx format is a ZIP archive whose matlab/document.xml uses
WordprocessingML (OOXML) with MathWorks-specific extensions:

  <w:pStyle w:val="heading">  — section heading
  <w:pStyle w:val="text">     — narrative text
  <w:pStyle w:val="code">     — MATLAB code (CDATA)
  <w:sectPr/>                 — section boundary (runnable section break)
  <w:customXml w:element="livecontrol"> — embedded interactive control

Each livecontrol carries a JSON `context` attribute describing the
control type (slider / comboBox / editField), its label, default value,
range, items, and the precise line/column offset within the code block
where the literal value sits.
"""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass, field
from typing import Any

from lxml import etree

# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------
W  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"

def _w(tag: str) -> str:
    return f"{{{W}}}{tag}"

def _mc(tag: str) -> str:
    return f"{{{MC}}}{tag}"


# ---------------------------------------------------------------------------
# IR dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Control:
    """One interactive LiveScript control linked to a variable."""
    type: str           # 'slider' | 'comboBox' | 'editField'
    variable: str       # MATLAB variable name (inferred from code)
    label: str          # display label from control JSON
    default: Any        # default value
    # slider-specific
    min: float | None = None
    max: float | None = None
    step: float | None = None
    # comboBox-specific
    items: list[str] | None = None
    item_labels: list[str] | None = None
    # position within the code block (0-based line offset, 0-based col)
    line_offset: int = 0
    col_start: int = 0
    col_end: int = 0


@dataclass
class Section:
    """One runnable LiveScript section."""
    heading: str | None        # section heading text (if any)
    text_blocks: list[str] = field(default_factory=list)
    code: str = ""             # raw MATLAB code (may be empty)
    controls: list[Control] = field(default_factory=list)


@dataclass
class LiveScript:
    """Top-level IR produced by the parser."""
    sections: list[Section] = field(default_factory=list)

    @property
    def all_controls(self) -> list[Control]:
        return [c for s in self.sections for c in s.controls]

    @property
    def all_code_lines(self) -> list[str]:
        lines = []
        for s in self.sections:
            if s.code:
                lines.extend(s.code.splitlines())
        return lines


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse(mlx_path: str) -> LiveScript:
    """Parse *mlx_path* and return a :class:`LiveScript` IR."""
    with zipfile.ZipFile(mlx_path) as zf:
        xml_bytes = zf.read("matlab/document.xml")
    return _parse_xml(xml_bytes)


def _parse_xml(xml_bytes: bytes) -> LiveScript:
    root = etree.fromstring(xml_bytes)
    body = root.find(_w("body"))
    if body is None:
        raise ValueError("No <w:body> found in document.xml")

    ls = LiveScript()
    current_section = Section(heading=None)

    for para in body:
        if para.tag != _w("p"):
            continue

        pPr = para.find(_w("pPr"))
        style = _get_style(pPr)
        is_section_break = _has_section_break(pPr)

        if is_section_break:
            # Commit current section and start a new one
            if _section_has_content(current_section):
                ls.sections.append(current_section)
            current_section = Section(heading=None)
            continue

        if style == "heading":
            text = _collect_text(para)
            if text:
                current_section.heading = text

        elif style == "text":
            text = _collect_text(para)
            if text:
                current_section.text_blocks.append(text)

        elif style == "code":
            code_text = _collect_cdata(para)
            controls = _collect_controls(para, code_text)
            if code_text:
                # Append to any existing code in this section
                if current_section.code:
                    current_section.code += "\n" + code_text
                else:
                    current_section.code = code_text
            current_section.controls.extend(controls)

    # Don't forget the last section
    if _section_has_content(current_section):
        ls.sections.append(current_section)

    return ls


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_style(pPr: etree._Element | None) -> str | None:
    if pPr is None:
        return None
    pStyle = pPr.find(_w("pStyle"))
    if pStyle is None:
        return None
    return pStyle.get(_w("val"))


def _has_section_break(pPr: etree._Element | None) -> bool:
    if pPr is None:
        return False
    return pPr.find(_w("sectPr")) is not None


def _collect_text(para: etree._Element) -> str:
    """Collect all <w:t> text within a paragraph (non-CDATA)."""
    parts = []
    for r in para.iter(_w("r")):
        for t in r.findall(_w("t")):
            if t.text:
                parts.append(t.text)
    return "".join(parts).strip()


def _collect_cdata(para: etree._Element) -> str:
    """Collect the CDATA content from <w:t> inside a code paragraph."""
    parts = []
    for r in para.iter(_w("r")):
        for t in r.findall(_w("t")):
            if t.text:
                parts.append(t.text)
    return "".join(parts)


def _collect_controls(para: etree._Element, code_text: str) -> list[Control]:
    """Extract all livecontrol elements from AlternateContent blocks in a paragraph."""
    controls: list[Control] = []
    code_lines = code_text.splitlines() if code_text else []

    for ac in para.iter(_mc("AlternateContent")):
        choice = ac.find(_mc("Choice"))
        if choice is None:
            continue
        cx = choice.find(_w("customXml"))
        if cx is None or cx.get(_w("element")) != "livecontrol":
            continue

        cxPr = cx.find(_w("customXmlPr"))
        if cxPr is None:
            continue

        attrs = {a.get(_w("name")): a.get(_w("val"))
                 for a in cxPr.findall(_w("attr"))}

        context_str = attrs.get("context", "{}")
        try:
            ctx = json.loads(context_str)
        except json.JSONDecodeError:
            continue

        ctrl_type = ctx.get("type", "editField")
        data      = ctx.get("data", {})

        line_offset = int(attrs.get("startOffsetLine", 0))
        col_start   = int(attrs.get("startColumn", 0))
        col_end     = int(attrs.get("endColumn", col_start))

        variable = _infer_variable(code_lines, line_offset, col_start, col_end)
        label    = data.get("text", variable)
        default  = data.get("value", data.get("defaultValue"))

        ctrl = Control(
            type=ctrl_type,
            variable=variable,
            label=label,
            default=default,
            line_offset=line_offset,
            col_start=col_start,
            col_end=col_end,
        )

        if ctrl_type == "slider":
            ctrl.min  = data.get("minimum")
            ctrl.max  = data.get("maximum")
            ctrl.step = data.get("step")

        elif ctrl_type == "comboBox":
            raw_items        = data.get("items", [])
            ctrl.item_labels = data.get("itemLabels",
                                        [i.get("label", "") for i in raw_items])
            ctrl.items   = [_strip_matlab_string(i.get("value", "")) for i in raw_items]
            ctrl.default = _strip_matlab_string(str(default)) if default else ""

        controls.append(ctrl)

    return controls


def _infer_variable(code_lines: list[str], line_offset: int, col_start: int, col_end: int) -> str:
    """
    Given the line/col of the RHS value in a code block, find the LHS variable name.
    Looks for patterns like:  varname = <value>;
    Falls back to 'var<N>' if the pattern is not matched.
    """
    if line_offset >= len(code_lines):
        return f"var{line_offset}"
    line = code_lines[line_offset]
    # Match   identifier = ...  at the start of the line (ignoring leading whitespace)
    m = re.match(r"\s*([A-Za-z_]\w*)\s*=", line)
    if m:
        return m.group(1)
    return f"var{line_offset}"


def _strip_matlab_string(s: str) -> str:
    """Remove MATLAB double-quoted string delimiters: '\"hello\"' -> 'hello'."""
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s


def _section_has_content(s: Section) -> bool:
    return bool(s.heading or s.text_blocks or s.code or s.controls)
