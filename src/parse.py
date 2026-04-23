import json
import re
import xml.etree.ElementTree as ET

from .ir import AppIR, ButtonSection, ControlSection, DropDownSection, LabelIR, SectionIR

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

    # Group paragraphs into sections.
    # Two splitting triggers:
    #   1. sectPr paragraph (explicit section break in hand-crafted / older .mlx)
    #   2. heading paragraph that appears AFTER code in the current section
    #      (real MATLAB .mlx files use headings as logical section dividers
    #       rather than emitting sectPr elements)
    sections = []
    current = []
    has_code_in_current = False
    for para in body.findall(_w("p")):
        ppr = para.find(_w("pPr"))
        style = None
        if ppr is not None:
            ps = ppr.find(_w("pStyle"))
            if ps is not None:
                style = ps.get(_w("val"))
        if ppr is not None and ppr.find(_w("sectPr")) is not None:
            sections.append(current)
            current = []
            has_code_in_current = False
        elif style == "heading" and has_code_in_current:
            # Heading after code → flush and start a new section with this heading
            sections.append(current)
            current = [para]
            has_code_in_current = False
        else:
            current.append(para)
            if style == "code":
                has_code_in_current = True
    if current:
        sections.append(current)

    private_props = []
    section_irs = []

    for paras in sections:
        code_text, livecontrols, labels = _extract_section(paras)

        # Init section: no livecontrols, no plot, no labels — pure assignments
        if not code_text.strip() and not labels and not livecontrols:
            continue

        # Multi-control paragraph: distribute code among controls
        if len(livecontrols) > 1:
            _distribute_multi_control_section(
                code_text, livecontrols, labels, private_props, section_irs
            )
            continue

        livecontrol = livecontrols[0] if livecontrols else None

        if livecontrol is None and not _has_plot_call(code_text) and not labels:
            lines = [l for l in code_text.strip().splitlines() if l.strip()]
            if _is_pure_assignment(lines):
                # Assignment-only section → private props, no SectionIR
                private_props.extend(_parse_assignments(code_text))
            else:
                # Display section: has non-assignment code (disp, fprintf, etc.)
                section_irs.append(SectionIR(
                    labels=[],
                    plot_lines=[],
                    button_sections=[],
                    dropdown_sections=[],
                    code_lines=lines,
                ))
            continue

        # Determine what this section produces
        plot_lines = []
        sec_buttons = []
        sec_dropdowns = []
        sec_controls = []

        if livecontrol is None:
            if _has_plot_call(code_text):
                plot_lines = [l for l in code_text.strip().splitlines() if l.strip()]
            else:
                # Labels only (text-only section) or assignments mixed with labels
                private_props.extend(_parse_assignments(code_text))
        elif livecontrol.get("type") == "button":
            label = livecontrol["data"]["text"]
            lines = [l for l in code_text.strip().splitlines() if l.strip()]
            sec_buttons.append(ButtonSection(
                label=label, code_lines=lines,
                component_name=_to_pascal_case(label),
            ))
        elif livecontrol.get("type") == "comboBox":
            sec, prop = _parse_dropdown_section(livecontrol["data"], code_text)
            sec_dropdowns.append(sec)
            private_props.append(prop)
        else:
            ctrl_type = _resolve_control_type(livecontrol)
            if ctrl_type:
                sec, prop = _parse_control_section(livecontrol["data"], code_text, ctrl_type)
                sec_controls.append(sec)
                if prop:
                    private_props.append(prop)

        section_irs.append(SectionIR(
            labels=labels,
            plot_lines=plot_lines,
            button_sections=sec_buttons,
            dropdown_sections=sec_dropdowns,
            control_sections=sec_controls,
        ))

    return AppIR(
        class_name=class_name,
        private_props=private_props,
        sections=section_irs,
    )


def _extract_section(paras):
    """Return (code_text, livecontrols_list, labels) for a list of paragraphs."""
    code_text = ""
    livecontrols = []
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
                ctx = None
                class_name_attr = ""
                for attr in cxpr.findall(_w("attr")):
                    name = attr.get(_w("name"))
                    if name == "context":
                        ctx = json.loads(attr.get(_w("val")))
                    elif name == "className":
                        class_name_attr = attr.get(_w("val"), "")
                if ctx is not None:
                    livecontrols.append(_normalize_livecontrol(ctx, class_name_attr))

        elif style in ("heading", "text"):
            text = "".join(
                t.text
                for run in para.findall(_w("r"))
                for t in [run.find(_w("t"))]
                if t is not None and t.text
            )
            if text.strip():
                labels.append(LabelIR(style=style, text=text.strip()))

    return code_text, livecontrols, labels


# Map from MATLAB livecontrol className attribute → canonical type string.
# Real .mlx files omit "type" from the context JSON; we infer it from className.
_CLASSNAME_TO_TYPE = {
    "SpinnerControlNode":     "spinner",
    "SliderControlNode":      "slider",
    "RangeSliderControlNode": "rangeslider",
    "CheckBoxControlNode":    "checkbox",
    "StateButtonControlNode": "statebutton",
    "EditFieldControlNode":   "editfield",
    "ColorPickerControlNode": "colorPicker",
    "DatePickerControlNode":  "datePicker",
    "FileBrowserControlNode": "filebrowser",
    "ComboBoxControlNode":    "comboBox",
}


def _normalize_livecontrol(ctx: dict, class_name_attr: str) -> dict:
    """Normalize a real .mlx context dict to the canonical format expected by the parser.

    Real MATLAB .mlx files use different JSON field names than the hand-crafted
    golden test fixtures:
      - No top-level "type" key (inferred from className attribute instead)
      - data.text  instead of data.label  (component display name)
      - data.minimum / data.maximum  instead of data.min / data.max
    """
    # Work on a shallow copy so we don't mutate the caller's dict
    ctx = dict(ctx)

    # Infer missing "type" from className
    if "type" not in ctx and class_name_attr in _CLASSNAME_TO_TYPE:
        ctx["type"] = _CLASSNAME_TO_TYPE[class_name_attr]

    if "data" in ctx:
        data = dict(ctx["data"])
        # Real .mlx uses minimum/maximum; parser expects min/max
        if "minimum" in data and "min" not in data:
            data["min"] = data.pop("minimum")
        if "maximum" in data and "max" not in data:
            data["max"] = data.pop("maximum")
        ctx["data"] = data

    return ctx


def _distribute_multi_control_section(
    code_text: str, livecontrols: list, labels: list,
    private_props: list, section_irs: list,
) -> None:
    """Handle a paragraph containing multiple livecontrols.

    Non-button controls (slider, comboBox, etc.) are processed first in DOM order;
    each consumes its bound-var assignment from the shared code pool and gets
    empty code_lines (value-update-only callback).  The button (if any) receives
    whatever code lines remain after all bound-var assignments have been consumed.
    """
    lines = [l for l in code_text.strip().splitlines() if l.strip()]

    sec_buttons = []
    sec_dropdowns = []
    sec_controls = []

    # First pass: non-button controls
    for lc in livecontrols:
        t = lc.get("type", "")
        if t == "button":
            continue
        elif t == "comboBox":
            sec, prop = _parse_dropdown_section(lc["data"], "\n".join(lines))
            lines = [l for l in sec.code_lines if l.strip()]
            sec.code_lines = []
            sec_dropdowns.append(sec)
            private_props.append(prop)
        else:
            ctrl_type = _resolve_control_type(lc)
            if ctrl_type:
                sec, prop = _parse_control_section(lc["data"], "\n".join(lines), ctrl_type)
                lines = [l for l in sec.code_lines if l.strip()]
                sec.code_lines = []
                sec_controls.append(sec)
                if prop:
                    private_props.append(prop)

    # Second pass: button gets remaining lines
    for lc in livecontrols:
        if lc.get("type") == "button":
            label = lc["data"]["text"]
            sec_buttons.append(ButtonSection(
                label=label,
                code_lines=lines,
                component_name=_to_pascal_case(label),
            ))
            lines = []

    section_irs.append(SectionIR(
        labels=labels,
        plot_lines=[],
        button_sections=sec_buttons,
        dropdown_sections=sec_dropdowns,
        control_sections=sec_controls,
    ))


def _parse_dropdown_section(data: dict, code_text: str):
    """Return (DropDownSection, private_prop_tuple) from a comboBox livecontrol."""
    component_name = _to_pascal_case(data["text"]) or "DropDown"
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
    """Convert a label string to a valid PascalCase MATLAB identifier.

    Splits on whitespace and non-alphanumeric characters, capitalises each
    token, and joins them.  E.g.:
        'Drop down'               → 'DropDown'
        'Square Wave Frequency (Hz)' → 'SquareWaveFrequencyHz'
        'Plot it'                 → 'PlotIt'
    """
    tokens = re.split(r'[^A-Za-z0-9]+', text)
    return "".join(t.capitalize() for t in tokens if t)


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


def _is_pure_assignment(lines: list) -> bool:
    """Return True if all non-empty lines are simple variable assignments."""
    if not lines:
        return True
    for line in lines:
        if not re.match(r"^\s*\w+\s*=\s*.+?;?\s*$", line.strip()):
            return False
    return True


def _parse_assignments(code_text: str) -> list:
    """Extract (name, value) pairs from simple assignment statements."""
    assignments = []
    for line in code_text.strip().splitlines():
        m = re.match(r"^\s*(\w+)\s*=\s*(.+?)\s*;?\s*$", line.strip())
        if m:
            assignments.append((m.group(1), m.group(2)))
    return assignments


# ---------------------------------------------------------------------------
# New control type support
# ---------------------------------------------------------------------------

# Map from livecontrol "type" string → internal control_type token.
# editfield is handled separately (requires valueType check).
_CONTROL_TYPE_MAP = {
    "slider":      "slider",
    "spinner":     "spinner",
    "rangeslider": "rangeslider",
    "checkbox":    "checkbox",
    "statebutton": "statebutton",
    "colorPicker": "colorpicker",
    "datePicker":  "datepicker",
    "filebrowser": "filebrowser",
}


def _resolve_control_type(livecontrol: dict) -> str:
    """Return internal control_type string, or None if unrecognised."""
    t = livecontrol.get("type", "")
    if t == "editfield":
        vt = livecontrol.get("data", {}).get("valueType", "")
        return "editfield_numeric" if vt == "Double" else "editfield_text"
    return _CONTROL_TYPE_MAP.get(t)


def _json_default_to_matlab(val, control_type: str) -> str:
    """Convert a JSON defaultValue to a MATLAB expression for the properties block."""
    if val is None:
        return "NaT"  # DatePicker has no defaultValue
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        # Emit as integer when possible (0 not 0.0)
        return str(int(val)) if val == int(val) else str(val)
    # String value from JSON
    stripped = str(val).strip('"')
    if control_type in ("editfield_text", "filebrowser"):
        # Convert MATLAB double-quoted string default to char vector
        return f"'{stripped}'"
    # rangeslider "[0 100]", colorpicker "[1 1 1]" — keep as array literal
    return stripped


def _normalize_for_match(val):
    """Normalise a JSON defaultValue for comparison with code RHS strings."""
    if val is None:
        return None
    if isinstance(val, bool):
        return "false" if not val else "true"
    if isinstance(val, (int, float)):
        return str(int(val)) if val == int(val) else str(val)
    # Strip outer double-quotes (handles MATLAB string literals in JSON)
    return str(val).strip('"')


def _parse_control_section(data: dict, code_text: str, control_type: str):
    """Return (ControlSection, prop_tuple_or_None) for a generic livecontrol."""
    label = data.get("label", data.get("text", "Control"))
    component_name = _to_pascal_case(label)
    callback_name = f"{component_name}ValueChanged"

    default_value_raw = data.get("defaultValue", None)
    matlab_default = _json_default_to_matlab(default_value_raw, control_type)
    target = _normalize_for_match(default_value_raw)

    # Find bound variable: first assignment whose RHS matches the default value.
    lines = [l for l in code_text.strip().splitlines() if l.strip()]
    bound_var = None
    remaining_lines = []
    for line in lines:
        m = re.match(r"^\s*(\w+)\s*=\s*(.+?)\s*;?\s*$", line.strip())
        if bound_var is None and m and target is not None:
            rhs = m.group(2).strip().strip('"')
            if rhs == target or rhs.lower() == target.lower():
                bound_var = m.group(1)
                continue
        remaining_lines.append(line)

    # Numeric range (slider, spinner, rangeslider)
    limits = ""
    if "min" in data and "max" in data:
        limits = f"[{data['min']} {data['max']}]"

    step = data.get("step", None)
    display_format = data.get("displayFormat", "")
    browser_type = data.get("browserType", "")

    sec = ControlSection(
        control_type=control_type,
        component_name=component_name,
        bound_var=bound_var or "",
        default_value=matlab_default,
        callback_name=callback_name,
        code_lines=remaining_lines,
        limits=limits,
        step=step,
        display_format=display_format,
        browser_type=browser_type,
    )
    prop = (bound_var, matlab_default) if bound_var else None
    return sec, prop
