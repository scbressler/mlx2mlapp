import json
import re
import xml.etree.ElementTree as ET

from .ir import AppIR, ButtonSection, DropDownSection, LabelIR

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _w(tag):
    return f"{{{W}}}{tag}"


def _mc(tag):
    return f"{{{MC}}}{tag}"


def parse_document(xml_path: str, class_name: str) -> AppIR:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    body = root.find(_w("body"))

    # Group paragraphs into sections separated by sectPr paragraphs.
    sections = []
    current = []
    for para in body.findall(_w("p")):
        ppr = para.find(_w("pPr"))
        if ppr is not None and ppr.find(_w("sectPr")) is not None:
            sections.append(current)
            current = []
        else:
            current.append(para)
    if current:
        sections.append(current)

    private_props = []
    button_sections = []
    dropdown_sections = []
    startup_lines = []
    labels = []

    for paras in sections:
        code_text, livecontrol, section_labels = _extract_section(paras)
        labels.extend(section_labels)

        if not code_text.strip():
            continue

        if livecontrol is None:
            if _has_plot_call(code_text):
                startup_lines = [l for l in code_text.strip().splitlines() if l.strip()]
            else:
                private_props.extend(_parse_assignments(code_text))
        elif livecontrol.get("type") == "button":
            label = livecontrol["data"]["text"]
            lines = [l for l in code_text.strip().splitlines() if l.strip()]
            button_sections.append(ButtonSection(label=label, code_lines=lines))
        elif livecontrol.get("type") == "comboBox":
            sec, prop = _parse_dropdown_section(livecontrol["data"], code_text)
            dropdown_sections.append(sec)
            private_props.append(prop)

    return AppIR(
        class_name=class_name,
        private_props=private_props,
        button_sections=button_sections,
        dropdown_sections=dropdown_sections,
        startup_lines=startup_lines,
        labels=labels,
    )


def _extract_section(paras):
    """Return (code_text, livecontrol_dict_or_None, labels) for a list of paragraphs."""
    code_text = ""
    livecontrol = None
    labels = []

    for para in paras:
        ppr = para.find(_w("pPr"))
        style = None
        if ppr is not None:
            ps = ppr.find(_w("pStyle"))
            if ps is not None:
                style = ps.get(_w("val"))

        if style == "code":
            for run in para.findall(_w("r")):
                t = run.find(_w("t"))
                if t is not None and t.text:
                    code_text += t.text

            for ac in para.findall(_mc("AlternateContent")):
                choice = ac.find(_mc("Choice"))
                if choice is None:
                    continue
                cx = choice.find(_w("customXml"))
                if cx is None or cx.get(_w("element")) != "livecontrol":
                    continue
                cxpr = cx.find(_w("customXmlPr"))
                if cxpr is None:
                    continue
                for attr in cxpr.findall(_w("attr")):
                    if attr.get(_w("name")) == "context":
                        livecontrol = json.loads(attr.get(_w("val")))

        elif style in ("heading", "text"):
            text = "".join(
                t.text
                for run in para.findall(_w("r"))
                for t in [run.find(_w("t"))]
                if t is not None and t.text
            )
            if text.strip():
                labels.append(LabelIR(style=style, text=text.strip()))

    return code_text, livecontrol, labels


def _parse_dropdown_section(data: dict, code_text: str):
    """Return (DropDownSection, private_prop_tuple) from a comboBox livecontrol."""
    component_name = _to_pascal_case(data["text"])
    callback_name = f"{component_name}ValueChanged"
    items = data["itemLabels"]
    # defaultValue is a MATLAB expression like '"one"' — strip outer double-quotes.
    raw_default = data["defaultValue"].strip('"')
    default_value = raw_default

    # Find the bound variable: the LHS of an assignment whose RHS matches defaultValue.
    lines = [l for l in code_text.strip().splitlines() if l.strip()]
    bound_var = None
    remaining_lines = []
    for line in lines:
        m = re.match(r"^\s*(\w+)\s*=\s*(.+?)\s*;?\s*$", line.strip())
        if bound_var is None and m and m.group(2).strip().strip('"') == default_value:
            bound_var = m.group(1)
        else:
            remaining_lines.append(line)

    sec = DropDownSection(
        component_name=component_name,
        bound_var=bound_var,
        items=items,
        default_value=default_value,
        callback_name=callback_name,
        code_lines=remaining_lines,
    )
    prop = (bound_var, f"'{default_value}'")
    return sec, prop


def _to_pascal_case(text: str) -> str:
    """Convert a label string to PascalCase (e.g. 'Drop down' -> 'DropDown')."""
    return "".join(word.capitalize() for word in text.split())


_PLOT_FUNCTIONS = frozenset({
    "plot", "scatter", "bar", "barh", "histogram", "imagesc", "surf",
    "mesh", "contour", "fplot", "polarplot", "loglog", "semilogx",
    "semilogy", "stem", "stairs", "area", "fill", "pie",
})


def _has_plot_call(code_text: str) -> bool:
    for fn in _PLOT_FUNCTIONS:
        if re.search(rf"\b{re.escape(fn)}\s*\(", code_text):
            return True
    return False


def _parse_assignments(code_text: str) -> list:
    """Extract (name, value) pairs from simple assignment statements."""
    assignments = []
    for line in code_text.strip().splitlines():
        m = re.match(r"^\s*(\w+)\s*=\s*(.+?)\s*;?\s*$", line.strip())
        if m:
            assignments.append((m.group(1), m.group(2)))
    return assignments
