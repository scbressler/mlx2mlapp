"""Parser for plain-text Live Script (.m) format.

Parses the %[text] / %[control:type:uuid] annotated format produced by
MATLAB R2025a+ when saving a Live Script as plain-text (.m).

Produces the same AppIR as parse_document() so the shared codegen works
unchanged for both input formats.
"""
import json
import re

from .ir import AppIR, ButtonSection, LabelIR, SectionIR
from .parse import (
    _has_plot_call,
    _is_pure_assignment,
    _parse_assignments,
    _parse_control_section,
    _parse_dropdown_section,
    _resolve_control_type,
    _to_pascal_case,
)

# ---------------------------------------------------------------------------
# Regex patterns for body line classification
# ---------------------------------------------------------------------------

# %[text] optional-text
_TEXT_LINE_RE = re.compile(r'^%\[text\](.*)')

# Standalone control line: optional whitespace, then %[control:type:uuid], rest ignored
_STANDALONE_CTRL_RE = re.compile(r'^\s*%\[control:(\w+):(\w+)\]')

# Inline control annotation at end of a code line: code  %[control:type:uuid]...
_INLINE_CTRL_RE = re.compile(r'^(.*?)\s*%\[control:(\w+):(\w+)\]')

# Trailing output annotation: code  %[output:uuid]...
_INLINE_OUTPUT_RE = re.compile(r'^(.*?)\s*%\[output:[\w]+\]')

# ---------------------------------------------------------------------------
# Regex patterns for appendix block parsing
# ---------------------------------------------------------------------------

# %[control:type:uuid]  (standalone — no trailing JSON on same line)
_APPENDIX_CTRL_RE = re.compile(r'^%\[control:(\w+):(\w+)\]\s*$')

# %   data: {json}
_APPENDIX_DATA_RE = re.compile(r'^%\s+data:\s+(.+)$')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_plaintext(m_path: str, class_name: str) -> AppIR:
    """Parse a plain-text Live Script (.m) file and return an AppIR."""
    with open(m_path, encoding='utf-8') as f:
        content = f.read()

    if '%[appendix]' in content:
        body_text, appendix_text = content.split('%[appendix]', 1)
    else:
        body_text, appendix_text = content, ''

    control_data = _parse_appendix(appendix_text)
    segments = _split_body_into_segments(body_text)
    return _build_ir(segments, control_data, class_name)


# ---------------------------------------------------------------------------
# Appendix parsing
# ---------------------------------------------------------------------------

def _parse_appendix(text: str) -> dict:
    """Parse appendix blocks. Returns {uuid: {'type': str, 'data': dict}}."""
    result = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        m = _APPENDIX_CTRL_RE.match(line)
        if m:
            ctrl_type = m.group(1)
            uuid = m.group(2)
            # Search forward for the data line, skipping separators and blanks
            j = i + 1
            while j < len(lines):
                candidate = lines[j].rstrip()
                if candidate in ('%---', ''):
                    j += 1
                    continue
                dm = _APPENDIX_DATA_RE.match(candidate)
                if dm:
                    try:
                        data = json.loads(dm.group(1))
                        result[uuid] = {'type': ctrl_type, 'data': data}
                    except json.JSONDecodeError:
                        pass
                    i = j
                break
        i += 1
    return result


# ---------------------------------------------------------------------------
# Body segmentation
# ---------------------------------------------------------------------------

def _split_body_into_segments(body_text: str) -> list:
    """Split body into (label_text_or_None, [raw_code_lines]) segments.

    Each %[text] line starts a new segment. The text after %[text] becomes
    the segment's label (markdown heading markers stripped).
    """
    segments = []
    current_label = None
    current_code = []

    for raw_line in body_text.splitlines():
        m = _TEXT_LINE_RE.match(raw_line)
        if m:
            # Flush current segment before starting a new one
            segments.append((current_label, current_code))
            label_text = m.group(1).strip()
            # Strip markdown heading markers (##, #, etc.)
            label_text = re.sub(r'^#+\s*', '', label_text).strip()
            current_label = label_text or None
            current_code = []
        else:
            current_code.append(raw_line)

    # Flush the last segment (only if non-empty)
    if current_code:
        segments.append((current_label, current_code))

    return segments


# ---------------------------------------------------------------------------
# Control extraction from a segment's raw code lines
# ---------------------------------------------------------------------------

def _extract_control_from_lines(code_lines: list, control_data: dict):
    """Strip annotations from raw code lines and identify any control.

    Returns (livecontrol_or_None, clean_code_lines).
    livecontrol has the same shape used by parse_document:
        {'type': str, 'data': dict}
    The 'data' dict is normalized so 'text' == 'label' when only 'label'
    exists (for buttons whose appendix uses "label" not "text").
    """
    ctrl_uuid = None
    ctrl_type_str = None
    clean = []

    for line in code_lines:
        if not line.strip():
            continue

        # ── Standalone control annotation (entire line is the annotation) ──
        if _STANDALONE_CTRL_RE.match(line):
            m = _STANDALONE_CTRL_RE.match(line)
            ctrl_type_str = m.group(1)
            ctrl_uuid = m.group(2)
            continue  # Don't add to clean lines

        # ── Inline control annotation appended to a code line ──
        m = _INLINE_CTRL_RE.match(line)
        if m:
            code_part = m.group(1).strip()
            ctrl_type_str = m.group(2)
            ctrl_uuid = m.group(3)
            if code_part:
                # Also strip any trailing output annotation from the code part
                mo = _INLINE_OUTPUT_RE.match(code_part)
                code_part = mo.group(1).strip() if mo else code_part
            if code_part:
                clean.append(code_part)
            continue

        # ── Trailing output annotation on a regular code line ──
        mo = _INLINE_OUTPUT_RE.match(line)
        if mo:
            code_part = mo.group(1).strip()
            if code_part:
                clean.append(code_part)
            continue

        # ── Regular code line ──
        clean.append(line.strip())

    # Resolve control from appendix
    livecontrol = None
    if ctrl_uuid and ctrl_uuid in control_data:
        info = control_data[ctrl_uuid]
        data = dict(info['data'])
        # Normalize: button appendix uses "label"; parse_document callers expect "text"
        if 'text' not in data and 'label' in data:
            data['text'] = data['label']
        livecontrol = {'type': info['type'], 'data': data}

    return livecontrol, clean


# ---------------------------------------------------------------------------
# IR construction
# ---------------------------------------------------------------------------

def _build_ir(segments: list, control_data: dict, class_name: str) -> AppIR:
    """Convert (label_text, raw_code_lines) segments into AppIR."""
    private_props = []
    section_irs = []

    for label_text, raw_lines in segments:
        livecontrol, clean_lines = _extract_control_from_lines(raw_lines, control_data)

        code_text = '\n'.join(clean_lines)

        labels = []
        if label_text:
            labels.append(LabelIR(style='heading', text=label_text))

        # Skip segments with no content at all
        if not clean_lines and not labels and livecontrol is None:
            continue

        # ── No control: init, display, or plot section ──
        if livecontrol is None and not _has_plot_call(code_text) and not labels:
            lines = [l for l in code_text.strip().splitlines() if l.strip()]
            if _is_pure_assignment(lines):
                private_props.extend(_parse_assignments(code_text))
            else:
                section_irs.append(SectionIR(
                    labels=[],
                    plot_lines=[],
                    button_sections=[],
                    dropdown_sections=[],
                    code_lines=lines,
                ))
            continue

        # ── Build section components ──
        plot_lines = []
        sec_buttons = []
        sec_dropdowns = []
        sec_controls = []

        if livecontrol is None:
            if _has_plot_call(code_text):
                plot_lines = [l for l in code_text.strip().splitlines() if l.strip()]
            else:
                private_props.extend(_parse_assignments(code_text))
        elif livecontrol.get('type') == 'button':
            label = livecontrol['data']['text']
            lines = [l for l in code_text.strip().splitlines() if l.strip()]
            sec_buttons.append(ButtonSection(label=label, code_lines=lines,
                                             component_name=_to_pascal_case(label)))
        elif livecontrol.get('type') == 'comboBox':
            sec, prop = _parse_dropdown_section(livecontrol['data'], code_text)
            sec_dropdowns.append(sec)
            private_props.append(prop)
        else:
            ctrl_type = _resolve_control_type(livecontrol)
            if ctrl_type:
                sec, prop = _parse_control_section(livecontrol['data'], code_text, ctrl_type)
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
