import re
import uuid as uuid_mod

from .ir import AppIR, ControlSection

# Default geometry constants (small canvas, existing exemplars)
_FIGURE_POSITION = "[100 100 640 480]"
_BUTTON_POSITION = "[272 219 100 22]"
_DROPDOWN_POSITION = "[270 229 100 22]"
_UIAXES_POSITION_SMALL = "[15 15 610 440]"

# Layout engine constants (1100x760 canvas — fits on 1470x956 screens without auto-scaling)
_CANVAS_LARGE = "[100 100 1100 760]"
_LAYOUT_MARGIN = 20
_LAYOUT_USABLE_W = 1060   # 1100 - 2*20
_LAYOUT_USABLE_H = 720    # 760 - 2*20
_LAYOUT_TOP = _LAYOUT_MARGIN + _LAYOUT_USABLE_H  # 740 (top of usable area in MATLAB coords)
_ROW_GAP = 10
_SECTION_GAP = 20

# Two-column layout constants (output_right mode)
_LEFT_COL_W = 520          # left column width
_RIGHT_COL_X = 560         # right column x: 20 (margin) + 520 (left) + 20 (gutter)
_RIGHT_COL_W = 520         # right column width; ends at 1080 = 1100 - 20 margin

_LABEL_HEIGHTS = {'heading': 40, 'text': 22}
_BUTTON_HEIGHT = 32
_DROPDOWN_HEIGHT = 32
_UIAXES_HEIGHT = 440        # single plot section
_UIAXES_HEIGHT_MULTI = 260  # multiple plot sections
_CODE_TEXT_AREA_HEIGHT = 120
_OUTPUT_TEXT_AREA_HEIGHT = 120

# TextArea styling
_CODE_BG_COLOR = "[0 0 0]"
_CODE_FONT_COLOR = "[1 1 1]"
_OUTPUT_BG_COLOR = "[0.149 0.149 0.149]"
_OUTPUT_FONT_COLOR = "[0.4 1 0.4]"
_TEXT_AREA_FONT = "'Courier New'"

# Maps control_type → (XML element tag, MATLAB class name)
_CONTROL_COMPONENT = {
    "slider":           ("Slider",           "matlab.ui.control.Slider"),
    "spinner":          ("Spinner",          "matlab.ui.control.Spinner"),
    "rangeslider":      ("RangeSlider",      "matlab.ui.control.RangeSlider"),
    "checkbox":         ("CheckBox",         "matlab.ui.control.CheckBox"),
    "statebutton":      ("StateButton",      "matlab.ui.control.StateButton"),
    "editfield_numeric":("NumericEditField", "matlab.ui.control.NumericEditField"),
    "editfield_text":   ("EditField",        "matlab.ui.control.EditField"),
    "colorpicker":      ("ColorPicker",      "matlab.ui.control.ColorPicker"),
    "datepicker":       ("DatePicker",       "matlab.ui.control.DatePicker"),
    "filebrowser":      ("EditField",        "matlab.ui.control.EditField"),
}

_CONTROL_HEIGHT = 32  # px — same as Button/DropDown


def _render_control_xml(ctrl: ControlSection, bottom: int, width: int,
                        margin_x: int, indent: str = "            ") -> list:
    """Return XML lines for a ControlSection component (no TextAreas)."""
    tag, _ = _CONTROL_COMPONENT.get(ctrl.control_type, ("EditField", "matlab.ui.control.EditField"))
    pos = f"[{margin_x} {bottom} {width} {_CONTROL_HEIGHT}]"
    lines = [f"{indent}<{tag} name='{ctrl.component_name}'>"]

    # Properties in alphabetical order (Children last — not applicable here)
    # DisplayFormat (DatePicker)
    if ctrl.display_format:
        lines.append(f"{indent}    <DisplayFormat>'{ctrl.display_format}'</DisplayFormat>")
    # Limits (Slider, Spinner, RangeSlider)
    if ctrl.limits:
        lines.append(f"{indent}    <Limits>{ctrl.limits}</Limits>")
    lines.append(f"{indent}    <Position>{pos}</Position>")
    # Step (Spinner only — Slider has no Step property in App Designer)
    if ctrl.control_type == "spinner" and ctrl.step is not None:
        step_val = int(ctrl.step) if ctrl.step == int(ctrl.step) else ctrl.step
        lines.append(f"{indent}    <Step>{step_val}</Step>")
    # Text (CheckBox, StateButton)
    if ctrl.control_type in ("checkbox", "statebutton"):
        lines.append(f"{indent}    <Text>'{ctrl.component_name}'</Text>")
    # Value — emit for all except DatePicker (no sensible default literal)
    if ctrl.control_type != "datepicker" and ctrl.default_value:
        # Wrap in quotes only if already a quoted char vector (starts/ends with ')
        val = ctrl.default_value
        if not (val.startswith("'") or val.startswith("[") or val[0].isdigit()
                or val in ("true", "false", "NaT") or val.lstrip('-')[0].isdigit()):
            val = f"'{val}'"
        lines.append(f"{indent}    <Value>{val}</Value>")
    lines.append(f"{indent}    <ValueChangedFcn>{ctrl.callback_name}</ValueChangedFcn>")
    lines.append(f"{indent}</{tag}>")
    return lines


_PLOT_FUNCTIONS = frozenset({
    "plot", "scatter", "bar", "barh", "histogram", "imagesc", "surf",
    "mesh", "contour", "fplot", "polarplot", "loglog", "semilogx",
    "semilogy", "stem", "stairs", "area", "fill", "pie",
})


def _assign_text_area_names(ir: AppIR, view_mode: str = "output_inline") -> None:
    """Set code/output TextArea names on display sections, buttons, and dropdowns.

    In hide_code mode, code_text_area_name is left empty (suppressed from layout).
    """
    hide_code = (view_mode == "hide_code")

    display_sections = [s for s in ir.sections if s.code_lines]
    n = len(display_sections)
    if n == 1:
        if not hide_code:
            display_sections[0].code_text_area_name = "CodeTextArea"
        display_sections[0].output_text_area_name = "OutputTextArea"
    else:
        for i, sec in enumerate(display_sections, 1):
            if not hide_code:
                sec.code_text_area_name = f"CodeTextArea_{i}"
            sec.output_text_area_name = f"OutputTextArea_{i}"

    for sec in ir.sections:
        for btn in sec.button_sections:
            if not hide_code:
                btn.code_text_area_name = f"{btn.label}CodeTextArea"
            btn.output_text_area_name = f"{btn.label}OutputTextArea"
        for dd in sec.dropdown_sections:
            if not hide_code:
                dd.code_text_area_name = f"{dd.component_name}CodeTextArea"
            dd.output_text_area_name = f"{dd.component_name}OutputTextArea"
        for ctrl in sec.control_sections:
            if not hide_code:
                ctrl.code_text_area_name = f"{ctrl.component_name}CodeTextArea"
            ctrl.output_text_area_name = f"{ctrl.component_name}OutputTextArea"


def _escape_matlab_str(s: str) -> str:
    """Escape a string for use inside a MATLAB single-quoted string."""
    return s.replace("'", "''")


def _code_lines_xml_value(lines: list) -> str:
    """Format code lines as a MATLAB string or cell array for XML Value."""
    escaped = [f"'{_escape_matlab_str(line)}'" for line in lines]
    if len(escaped) == 1:
        return escaped[0]
    return "{" + "; ".join(escaped) + "}"


def _assign_axes_names(ir: AppIR) -> None:
    """Set axes_name on each SectionIR in-place based on total plot section count."""
    plot_sections = [s for s in ir.sections if s.plot_lines]
    n = len(plot_sections)
    if n == 1:
        plot_sections[0].axes_name = "UIAxes"
    else:
        for i, sec in enumerate(plot_sections, 1):
            sec.axes_name = f"UIAxes_{i}"


def _use_layout_engine(ir: AppIR) -> bool:
    """Use layout engine when any section has labels, code lines, buttons, dropdowns, controls, or there are multiple sections."""
    if len(ir.sections) > 1:
        return True
    return any(
        sec.labels or sec.code_lines or sec.button_sections or sec.dropdown_sections or sec.control_sections
        for sec in ir.sections
    )


def generate_layout_xml(ir: AppIR, view_mode: str = "output_inline") -> str:
    _assign_axes_names(ir)
    _assign_text_area_names(ir, view_mode=view_mode)
    if _use_layout_engine(ir):
        if view_mode == "output_right":
            return _generate_layout_xml_right(ir)
        return _generate_layout_xml_with_engine(ir)
    return _generate_layout_xml_fixed(ir)


def _generate_layout_xml_fixed(ir: AppIR) -> str:
    """Original fixed-position layout for single-section exemplars without labels."""
    # Flatten for backward compat
    button_sections = [b for s in ir.sections for b in s.button_sections]
    dropdown_sections = [d for s in ir.sections for d in s.dropdown_sections]
    has_plot = any(s.plot_lines for s in ir.sections)

    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<Components>",
        "    <UIFigure name='UIFigure'>",
        "        <Name>'MATLAB App'</Name>",
        f"        <Position>{_FIGURE_POSITION}</Position>",
        "        <Children>",
    ]
    for sec in button_sections:
        btn_name = f"{sec.label}Button"
        cb_name = f"{sec.label}ButtonPushed"
        lines += [
            f"            <Button name='{btn_name}'>",
            f"                <ButtonPushedFcn>{cb_name}</ButtonPushedFcn>",
            f"                <Position>{_BUTTON_POSITION}</Position>",
            f"                <Text>'{sec.label}'</Text>",
            "            </Button>",
        ]
    for sec in dropdown_sections:
        items_str = "{" + ", ".join(f"'{item}'" for item in sec.items) + "}"
        lines += [
            f"            <DropDown name='{sec.component_name}'>",
            f"                <Items>{items_str}</Items>",
            f"                <Position>{_DROPDOWN_POSITION}</Position>",
            f"                <Value>'{sec.default_value}'</Value>",
            f"                <ValueChangedFcn>{sec.callback_name}</ValueChangedFcn>",
            f"            </DropDown>",
        ]
    if has_plot:
        lines += [
            "            <UIAxes name='UIAxes'>",
            f"                <Position>{_UIAXES_POSITION_SMALL}</Position>",
            "                <Title.String>''</Title.String>",
            "                <XLabel.String>''</XLabel.String>",
            "                <YLabel.String>''</YLabel.String>",
            "                <ZLabel.String>''</ZLabel.String>",
            "            </UIAxes>",
        ]
    lines += [
        "        </Children>",
        "    </UIFigure>",
        "</Components>",
    ]
    return "\n".join(lines)


def _generate_layout_xml_with_engine(ir: AppIR) -> str:
    """Layout engine path: 1440x1024 canvas, y_cursor placement, section-ordered."""
    plot_count = sum(1 for s in ir.sections if s.plot_lines)
    axes_h = _UIAXES_HEIGHT_MULTI if plot_count > 1 else _UIAXES_HEIGHT

    y_cursor = _LAYOUT_TOP
    child_lines = []
    label_counter = 0

    for sec_idx, sec in enumerate(ir.sections):
        is_last_section = (sec_idx == len(ir.sections) - 1)

        # Labels
        for label in sec.labels:
            label_counter += 1
            h = _LABEL_HEIGHTS.get(label.style, 22)
            bottom = y_cursor - h
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {h}]"
            y_cursor = bottom - _ROW_GAP

            child_lines.append(f"            <Label name='Label_{label_counter}'>")
            if label.style == 'heading':
                child_lines.append(f"                <FontSize>18</FontSize>")
                child_lines.append(f"                <FontWeight>'bold'</FontWeight>")
            child_lines.append(f"                <Position>{pos}</Position>")
            child_lines.append(f"                <Text>'{label.text}'</Text>")
            if label.style == 'text':
                child_lines.append(f"                <WordWrap>'on'</WordWrap>")
            child_lines.append(f"            </Label>")

        # Button sections
        for btn in sec.button_sections:
            btn_name = f"{btn.label}Button"
            cb_name = f"{btn.label}ButtonPushed"
            bottom = y_cursor - _BUTTON_HEIGHT
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_BUTTON_HEIGHT}]"
            child_lines += [
                f"            <Button name='{btn_name}'>",
                f"                <ButtonPushedFcn>{cb_name}</ButtonPushedFcn>",
                f"                <Position>{pos}</Position>",
                f"                <Text>'{btn.label}'</Text>",
                "            </Button>",
            ]
            y_cursor = bottom - _ROW_GAP
            if btn.code_text_area_name:
                bottom = y_cursor - _CODE_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_CODE_TEXT_AREA_HEIGHT}]"
                val = _code_lines_xml_value(btn.code_lines)
                child_lines += [
                    f"            <TextArea name='{btn.code_text_area_name}'>",
                    f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>{val}</Value>",
                    "            </TextArea>",
                ]
                y_cursor = bottom - _ROW_GAP
            if btn.output_text_area_name:
                bottom = y_cursor - _OUTPUT_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
                child_lines += [
                    f"            <TextArea name='{btn.output_text_area_name}'>",
                    f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>''</Value>",
                    "            </TextArea>",
                ]
                gap = _ROW_GAP if is_last_section else _SECTION_GAP
                y_cursor = bottom - gap

        # Dropdown sections
        for dd in sec.dropdown_sections:
            items_str = "{" + ", ".join(f"'{item}'" for item in dd.items) + "}"
            bottom = y_cursor - _DROPDOWN_HEIGHT
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_DROPDOWN_HEIGHT}]"
            child_lines += [
                f"            <DropDown name='{dd.component_name}'>",
                f"                <Items>{items_str}</Items>",
                f"                <Position>{pos}</Position>",
                f"                <Value>'{dd.default_value}'</Value>",
                f"                <ValueChangedFcn>{dd.callback_name}</ValueChangedFcn>",
                "            </DropDown>",
            ]
            y_cursor = bottom - _ROW_GAP
            if dd.code_text_area_name:
                bottom = y_cursor - _CODE_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_CODE_TEXT_AREA_HEIGHT}]"
                val = _code_lines_xml_value(dd.code_lines)
                child_lines += [
                    f"            <TextArea name='{dd.code_text_area_name}'>",
                    f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>{val}</Value>",
                    "            </TextArea>",
                ]
                y_cursor = bottom - _ROW_GAP
            if dd.output_text_area_name:
                bottom = y_cursor - _OUTPUT_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
                child_lines += [
                    f"            <TextArea name='{dd.output_text_area_name}'>",
                    f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>''</Value>",
                    "            </TextArea>",
                ]
                gap = _ROW_GAP if is_last_section else _SECTION_GAP
                y_cursor = bottom - gap

        # Generic control sections (Slider, Spinner, etc.)
        for ctrl in sec.control_sections:
            ctrl_lines = _render_control_xml(ctrl, y_cursor - _CONTROL_HEIGHT,
                                            _LAYOUT_USABLE_W, _LAYOUT_MARGIN)
            child_lines += ctrl_lines
            y_cursor = (y_cursor - _CONTROL_HEIGHT) - _ROW_GAP
            if ctrl.code_text_area_name:
                bottom = y_cursor - _CODE_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_CODE_TEXT_AREA_HEIGHT}]"
                val = _code_lines_xml_value(ctrl.code_lines)
                child_lines += [
                    f"            <TextArea name='{ctrl.code_text_area_name}'>",
                    f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>{val}</Value>",
                    "            </TextArea>",
                ]
                y_cursor = bottom - _ROW_GAP
            if ctrl.output_text_area_name:
                bottom = y_cursor - _OUTPUT_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
                child_lines += [
                    f"            <TextArea name='{ctrl.output_text_area_name}'>",
                    f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>''</Value>",
                    "            </TextArea>",
                ]
                gap = _ROW_GAP if is_last_section else _SECTION_GAP
                y_cursor = bottom - gap

        # Display CodeTextArea
        if sec.code_text_area_name:
            bottom = y_cursor - _CODE_TEXT_AREA_HEIGHT
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_CODE_TEXT_AREA_HEIGHT}]"
            val = _code_lines_xml_value(sec.code_lines)
            child_lines += [
                f"            <TextArea name='{sec.code_text_area_name}'>",
                f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                f"                <Editable>'off'</Editable>",
                f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                f"                <Position>{pos}</Position>",
                f"                <Value>{val}</Value>",
                f"            </TextArea>",
            ]
            y_cursor = bottom - _ROW_GAP

        # UIAxes
        if sec.plot_lines:
            bottom = y_cursor - axes_h
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {axes_h}]"
            child_lines += [
                f"            <UIAxes name='{sec.axes_name}'>",
                f"                <Position>{pos}</Position>",
                "                <Title.String>''</Title.String>",
                "                <XLabel.String>''</XLabel.String>",
                "                <YLabel.String>''</YLabel.String>",
                "                <ZLabel.String>''</ZLabel.String>",
                "            </UIAxes>",
            ]
            if sec.output_text_area_name:
                y_cursor = bottom - _ROW_GAP
            else:
                gap = _ROW_GAP if is_last_section else _SECTION_GAP
                y_cursor = bottom - gap

        # OutputTextArea
        if sec.output_text_area_name:
            bottom = y_cursor - _OUTPUT_TEXT_AREA_HEIGHT
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
            child_lines += [
                f"            <TextArea name='{sec.output_text_area_name}'>",
                f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                f"                <Editable>'off'</Editable>",
                f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                f"                <Position>{pos}</Position>",
                f"                <Value>''</Value>",
                f"            </TextArea>",
            ]
            gap = _ROW_GAP if is_last_section else _SECTION_GAP
            y_cursor = bottom - gap

    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<Components>",
        "    <UIFigure name='UIFigure'>",
        "        <Name>'MATLAB App'</Name>",
        f"        <Position>{_CANVAS_LARGE}</Position>",
        "        <Children>",
        *child_lines,
        "        </Children>",
        "    </UIFigure>",
        "</Components>",
    ]
    return "\n".join(lines)


def _generate_layout_xml_right(ir: AppIR) -> str:
    """Two-column layout for output_right mode.

    Left column  (x=20,  w=520): labels, CodeTextArea, Button/DropDown widgets.
    Right column (x=560, w=520): OutputTextArea, UIAxes.
    """
    plot_count = sum(1 for s in ir.sections if s.plot_lines)
    axes_h = _UIAXES_HEIGHT_MULTI if plot_count > 1 else _UIAXES_HEIGHT

    y_cursor = _LAYOUT_TOP
    child_lines = []
    label_counter = 0

    for sec_idx, sec in enumerate(ir.sections):
        is_last_section = (sec_idx == len(ir.sections) - 1)

        left_cursor = y_cursor
        right_cursor = y_cursor

        # Left column: labels
        for label in sec.labels:
            label_counter += 1
            h = _LABEL_HEIGHTS.get(label.style, 22)
            bottom = left_cursor - h
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LEFT_COL_W} {h}]"
            left_cursor = bottom - _ROW_GAP
            child_lines.append(f"            <Label name='Label_{label_counter}'>")
            if label.style == 'heading':
                child_lines.append(f"                <FontSize>18</FontSize>")
                child_lines.append(f"                <FontWeight>'bold'</FontWeight>")
            child_lines.append(f"                <Position>{pos}</Position>")
            child_lines.append(f"                <Text>'{label.text}'</Text>")
            if label.style == 'text':
                child_lines.append(f"                <WordWrap>'on'</WordWrap>")
            child_lines.append(f"            </Label>")

        # Left column: button sections; right column: their output areas
        for btn in sec.button_sections:
            btn_name = f"{btn.label}Button"
            cb_name = f"{btn.label}ButtonPushed"
            bottom = left_cursor - _BUTTON_HEIGHT
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LEFT_COL_W} {_BUTTON_HEIGHT}]"
            child_lines += [
                f"            <Button name='{btn_name}'>",
                f"                <ButtonPushedFcn>{cb_name}</ButtonPushedFcn>",
                f"                <Position>{pos}</Position>",
                f"                <Text>'{btn.label}'</Text>",
                "            </Button>",
            ]
            left_cursor = bottom - _ROW_GAP
            code_bottom = None
            if btn.code_text_area_name:
                code_bottom = left_cursor - _CODE_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {code_bottom} {_LEFT_COL_W} {_CODE_TEXT_AREA_HEIGHT}]"
                val = _code_lines_xml_value(btn.code_lines)
                child_lines += [
                    f"            <TextArea name='{btn.code_text_area_name}'>",
                    f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>{val}</Value>",
                    "            </TextArea>",
                ]
                left_cursor = code_bottom - _ROW_GAP
            if btn.output_text_area_name:
                bottom = code_bottom if code_bottom is not None else right_cursor - _OUTPUT_TEXT_AREA_HEIGHT
                pos = f"[{_RIGHT_COL_X} {bottom} {_RIGHT_COL_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
                child_lines += [
                    f"            <TextArea name='{btn.output_text_area_name}'>",
                    f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>''</Value>",
                    "            </TextArea>",
                ]
                right_cursor = bottom - _ROW_GAP

        # Left column: dropdown sections; right column: their output areas
        for dd in sec.dropdown_sections:
            items_str = "{" + ", ".join(f"'{item}'" for item in dd.items) + "}"
            bottom = left_cursor - _DROPDOWN_HEIGHT
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LEFT_COL_W} {_DROPDOWN_HEIGHT}]"
            child_lines += [
                f"            <DropDown name='{dd.component_name}'>",
                f"                <Items>{items_str}</Items>",
                f"                <Position>{pos}</Position>",
                f"                <Value>'{dd.default_value}'</Value>",
                f"                <ValueChangedFcn>{dd.callback_name}</ValueChangedFcn>",
                "            </DropDown>",
            ]
            left_cursor = bottom - _ROW_GAP
            code_bottom = None
            if dd.code_text_area_name:
                code_bottom = left_cursor - _CODE_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {code_bottom} {_LEFT_COL_W} {_CODE_TEXT_AREA_HEIGHT}]"
                val = _code_lines_xml_value(dd.code_lines)
                child_lines += [
                    f"            <TextArea name='{dd.code_text_area_name}'>",
                    f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>{val}</Value>",
                    "            </TextArea>",
                ]
                left_cursor = code_bottom - _ROW_GAP
            if dd.output_text_area_name:
                bottom = code_bottom if code_bottom is not None else right_cursor - _OUTPUT_TEXT_AREA_HEIGHT
                pos = f"[{_RIGHT_COL_X} {bottom} {_RIGHT_COL_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
                child_lines += [
                    f"            <TextArea name='{dd.output_text_area_name}'>",
                    f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>''</Value>",
                    "            </TextArea>",
                ]
                right_cursor = bottom - _ROW_GAP

        # Left column: generic control sections; right column: their output areas
        for ctrl in sec.control_sections:
            ctrl_lines = _render_control_xml(ctrl, left_cursor - _CONTROL_HEIGHT,
                                            _LEFT_COL_W, _LAYOUT_MARGIN)
            child_lines += ctrl_lines
            left_cursor = (left_cursor - _CONTROL_HEIGHT) - _ROW_GAP
            code_bottom = None
            if ctrl.code_text_area_name:
                code_bottom = left_cursor - _CODE_TEXT_AREA_HEIGHT
                pos = f"[{_LAYOUT_MARGIN} {code_bottom} {_LEFT_COL_W} {_CODE_TEXT_AREA_HEIGHT}]"
                val = _code_lines_xml_value(ctrl.code_lines)
                child_lines += [
                    f"            <TextArea name='{ctrl.code_text_area_name}'>",
                    f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>{val}</Value>",
                    "            </TextArea>",
                ]
                left_cursor = code_bottom - _ROW_GAP
            if ctrl.output_text_area_name:
                bottom = code_bottom if code_bottom is not None else right_cursor - _OUTPUT_TEXT_AREA_HEIGHT
                pos = f"[{_RIGHT_COL_X} {bottom} {_RIGHT_COL_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
                child_lines += [
                    f"            <TextArea name='{ctrl.output_text_area_name}'>",
                    f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                    f"                <Editable>'off'</Editable>",
                    f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                    f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                    f"                <Position>{pos}</Position>",
                    f"                <Value>''</Value>",
                    "            </TextArea>",
                ]
                right_cursor = bottom - _ROW_GAP

        # Left column: display CodeTextArea
        if sec.code_text_area_name:
            bottom = left_cursor - _CODE_TEXT_AREA_HEIGHT
            pos = f"[{_LAYOUT_MARGIN} {bottom} {_LEFT_COL_W} {_CODE_TEXT_AREA_HEIGHT}]"
            val = _code_lines_xml_value(sec.code_lines)
            child_lines += [
                f"            <TextArea name='{sec.code_text_area_name}'>",
                f"                <BackgroundColor>{_CODE_BG_COLOR}</BackgroundColor>",
                f"                <Editable>'off'</Editable>",
                f"                <FontColor>{_CODE_FONT_COLOR}</FontColor>",
                f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                f"                <Position>{pos}</Position>",
                f"                <Value>{val}</Value>",
                f"            </TextArea>",
            ]
            left_cursor = bottom - _ROW_GAP

        # Right column: UIAxes
        if sec.plot_lines:
            bottom = right_cursor - axes_h
            pos = f"[{_RIGHT_COL_X} {bottom} {_RIGHT_COL_W} {axes_h}]"
            child_lines += [
                f"            <UIAxes name='{sec.axes_name}'>",
                f"                <Position>{pos}</Position>",
                "                <Title.String>''</Title.String>",
                "                <XLabel.String>''</XLabel.String>",
                "                <YLabel.String>''</YLabel.String>",
                "                <ZLabel.String>''</ZLabel.String>",
                "            </UIAxes>",
            ]
            right_cursor = bottom - _ROW_GAP

        # Right column: display OutputTextArea
        if sec.output_text_area_name:
            bottom = right_cursor - _OUTPUT_TEXT_AREA_HEIGHT
            pos = f"[{_RIGHT_COL_X} {bottom} {_RIGHT_COL_W} {_OUTPUT_TEXT_AREA_HEIGHT}]"
            child_lines += [
                f"            <TextArea name='{sec.output_text_area_name}'>",
                f"                <BackgroundColor>{_OUTPUT_BG_COLOR}</BackgroundColor>",
                f"                <Editable>'off'</Editable>",
                f"                <FontColor>{_OUTPUT_FONT_COLOR}</FontColor>",
                f"                <FontName>{_TEXT_AREA_FONT}</FontName>",
                f"                <Position>{pos}</Position>",
                f"                <Value>''</Value>",
                f"            </TextArea>",
            ]
            right_cursor = bottom - _ROW_GAP

        # Advance global cursor past the taller column
        # Each column cursor has had _ROW_GAP subtracted after its last component;
        # add it back then subtract the section gap.
        section_bottom = min(left_cursor, right_cursor)
        gap = _ROW_GAP if is_last_section else _SECTION_GAP
        y_cursor = section_bottom + _ROW_GAP - gap

    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<Components>",
        "    <UIFigure name='UIFigure'>",
        "        <Name>'MATLAB App'</Name>",
        f"        <Position>{_CANVAS_LARGE}</Position>",
        "        <Children>",
        *child_lines,
        "        </Children>",
        "    </UIFigure>",
        "</Components>",
    ]
    return "\n".join(lines)


def generate_m(ir: AppIR, layout_xml: str, app_id: str = None,
               release: str = "R2025b") -> str:
    if app_id is None:
        app_id = str(uuid_mod.uuid4())

    # Collect all private props and flatten callbacks/plots across sections
    prop_names = [name for name, _ in ir.private_props]
    all_button_sections = [b for s in ir.sections for b in s.button_sections]
    all_dropdown_sections = [d for s in ir.sections for d in s.dropdown_sections]
    plot_sections = [s for s in ir.sections if s.plot_lines]
    display_sections = [s for s in ir.sections if s.code_lines]
    has_plot = bool(plot_sections)
    has_startup = has_plot or bool(display_sections)

    # --- Public properties block ---
    component_names = ["UIFigure"]
    type_map = {"UIFigure": "matlab.ui.Figure"}

    label_counter = 0
    for sec in ir.sections:
        for _ in sec.labels:
            label_counter += 1
            component_names.append(f"Label_{label_counter}")
            type_map[f"Label_{label_counter}"] = "matlab.ui.control.Label"
        if sec.code_text_area_name:
            component_names.append(sec.code_text_area_name)
            type_map[sec.code_text_area_name] = "matlab.ui.control.TextArea"
        if sec.plot_lines:
            component_names.append(sec.axes_name)
            type_map[sec.axes_name] = "matlab.ui.control.UIAxes"
        for b in sec.button_sections:
            component_names.append(f"{b.label}Button")
            type_map[f"{b.label}Button"] = "matlab.ui.control.Button"
            if b.code_text_area_name:
                component_names.append(b.code_text_area_name)
                type_map[b.code_text_area_name] = "matlab.ui.control.TextArea"
            if b.output_text_area_name:
                component_names.append(b.output_text_area_name)
                type_map[b.output_text_area_name] = "matlab.ui.control.TextArea"
        for d in sec.dropdown_sections:
            component_names.append(d.component_name)
            type_map[d.component_name] = "matlab.ui.control.DropDown"
            if d.code_text_area_name:
                component_names.append(d.code_text_area_name)
                type_map[d.code_text_area_name] = "matlab.ui.control.TextArea"
            if d.output_text_area_name:
                component_names.append(d.output_text_area_name)
                type_map[d.output_text_area_name] = "matlab.ui.control.TextArea"
        for ctrl in sec.control_sections:
            _, matlab_class = _CONTROL_COMPONENT.get(ctrl.control_type,
                                                     ("EditField", "matlab.ui.control.EditField"))
            component_names.append(ctrl.component_name)
            type_map[ctrl.component_name] = matlab_class
            if ctrl.code_text_area_name:
                component_names.append(ctrl.code_text_area_name)
                type_map[ctrl.code_text_area_name] = "matlab.ui.control.TextArea"
            if ctrl.output_text_area_name:
                component_names.append(ctrl.output_text_area_name)
                type_map[ctrl.output_text_area_name] = "matlab.ui.control.TextArea"
        if sec.output_text_area_name:
            component_names.append(sec.output_text_area_name)
            type_map[sec.output_text_area_name] = "matlab.ui.control.TextArea"

    col_width = max(len(n) for n in component_names)
    pub_lines = []
    for name in component_names:
        padding = " " * (col_width - len(name) + 2)
        pub_lines.append(f"        {name}{padding}{type_map[name]}")

    # --- Private properties block (omitted when empty) ---
    priv_lines = []
    for name, val in ir.private_props:
        priv_lines.append(f"        {name} = {val} % Description")

    priv_block = []
    if priv_lines:
        priv_block = [
            "",
            "    ",
            "    properties (Access = private)",
            *priv_lines,
            "    end",
            "    ",
        ]

    all_control_sections = [c for s in ir.sections for c in s.control_sections]

    # --- Callbacks block ---
    cb_lines = []
    for sec in all_button_sections:
        btn_name = f"{sec.label}Button"
        cb_name = f"{sec.label}ButtonPushed"
        cb_lines.append(f"        % Button pushed function: {btn_name}")
        cb_lines.append(f"        function {cb_name}(app, event)")
        if sec.output_text_area_name:
            cb_lines.append("            diaryFile = [tempname '.txt'];")
            cb_lines.append("            diary(diaryFile);")
            cb_lines.append("            diary('on');")
        for line in sec.code_lines:
            cb_lines.append(f"            {_prefix_vars(line.strip(), prop_names)}")
        if sec.output_text_area_name:
            cb_lines.append("            diary('off');")
            cb_lines.append("            if exist(diaryFile, 'file')")
            cb_lines.append("                capturedOutput = fileread(diaryFile);")
            cb_lines.append("                delete(diaryFile);")
            cb_lines.append("            else")
            cb_lines.append("                capturedOutput = '';")
            cb_lines.append("            end")
            cb_lines.append(f"            app.{sec.output_text_area_name}.Value = strsplit(strtrim(capturedOutput), newline);")
        cb_lines.append("        end")
    for sec in all_dropdown_sections:
        cb_lines.append(f"        % Value changed function: {sec.component_name}")
        cb_lines.append(f"        function {sec.callback_name}(app, event)")
        cb_lines.append(f"            app.{sec.bound_var} = app.{sec.component_name}.Value;")
        if sec.output_text_area_name:
            cb_lines.append("            diaryFile = [tempname '.txt'];")
            cb_lines.append("            diary(diaryFile);")
            cb_lines.append("            diary('on');")
        for line in sec.code_lines:
            cb_lines.append(f"            {_prefix_vars(line.strip(), prop_names)}")
        if sec.output_text_area_name:
            cb_lines.append("            diary('off');")
            cb_lines.append("            if exist(diaryFile, 'file')")
            cb_lines.append("                capturedOutput = fileread(diaryFile);")
            cb_lines.append("                delete(diaryFile);")
            cb_lines.append("            else")
            cb_lines.append("                capturedOutput = '';")
            cb_lines.append("            end")
            cb_lines.append(f"            app.{sec.output_text_area_name}.Value = strsplit(strtrim(capturedOutput), newline);")
        cb_lines.append("        end")
    for ctrl in all_control_sections:
        cb_lines.append(f"        % Value changed function: {ctrl.component_name}")
        cb_lines.append(f"        function {ctrl.callback_name}(app, event)")
        if ctrl.bound_var:
            cb_lines.append(f"            app.{ctrl.bound_var} = app.{ctrl.component_name}.Value;")
        if ctrl.output_text_area_name:
            cb_lines.append("            diaryFile = [tempname '.txt'];")
            cb_lines.append("            diary(diaryFile);")
            cb_lines.append("            diary('on');")
        for line in ctrl.code_lines:
            cb_lines.append(f"            {_prefix_vars(line.strip(), prop_names)}")
        if ctrl.output_text_area_name:
            cb_lines.append("            diary('off');")
            cb_lines.append("            if exist(diaryFile, 'file')")
            cb_lines.append("                capturedOutput = fileread(diaryFile);")
            cb_lines.append("                delete(diaryFile);")
            cb_lines.append("            else")
            cb_lines.append("                capturedOutput = '';")
            cb_lines.append("            end")
            cb_lines.append(f"            app.{ctrl.output_text_area_name}.Value = strsplit(strtrim(capturedOutput), newline);")
        cb_lines.append("        end")
    if has_startup:
        cb_lines.append("        % Code that executes after component creation")
        cb_lines.append("        function startupFcn(app)")
        for sec in display_sections:
            cb_lines.append("            diaryFile = [tempname '.txt'];")
            cb_lines.append("            diary(diaryFile);")
            cb_lines.append("            diary('on');")
            for line in sec.code_lines:
                cb_lines.append(f"            {line.strip()}")
            cb_lines.append("            diary('off');")
            cb_lines.append("            if exist(diaryFile, 'file')")
            cb_lines.append("                capturedOutput = fileread(diaryFile);")
            cb_lines.append("                delete(diaryFile);")
            cb_lines.append("            else")
            cb_lines.append("                capturedOutput = '';")
            cb_lines.append("            end")
            cb_lines.append(f"            app.{sec.output_text_area_name}.Value = strsplit(strtrim(capturedOutput), newline);")
        for sec in plot_sections:
            for line in sec.plot_lines:
                cb_lines.append(f"            {_inject_axes(line.strip(), sec.axes_name)}")
        cb_lines.append("        end")

    # --- Assemble classdef ---
    classdef_lines = [
        f"classdef {ir.class_name} < matlab.apps.App",
        "",
        "    % Properties that correspond to app components",
        "    properties (Access = public)",
        *pub_lines,
        "    end",
        *priv_block,
        "",
        "    % Callbacks that handle component events",
        "    methods",
        "",
        *cb_lines,
        "    end",
        "",
        "end",
    ]

    # --- Appendix sections ---
    min_release = _prev_release(release)

    run_config_lines = []
    if has_startup:
        run_config_lines = [
            "",
            "%---",
            "%[app:runConfiguration]",
            "%{",
            "<?xml version='1.0' encoding='UTF-8'?>",
            "<RunConfiguration>",
            "    <StartupFcn>startupFcn</StartupFcn>",
            "</RunConfiguration>",
            "%}",
        ]

    appendix_lines = [
        "",
        "%[appendix]",
        "%---",
        "%[app:layout]",
        "%{",
        *layout_xml.splitlines(),
        "%}",
        *run_config_lines,
        "",
        "%---",
        "%[app:appDetails]",
        "%{",
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<AppDetails>",
        f"    <Name>{ir.class_name}</Name>",
        "    <Version>1.0</Version>",
        "</AppDetails>",
        "%}",
        "",
        "%---",
        "%[app:internalData]",
        "%{",
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<InternalData>",
        f"    <AppId>{app_id}</AppId>",
        "    <AppType>Standard</AppType>",
        f"    <MATLABRelease>{release}</MATLABRelease>",
        f"    <MinimumSupportedMATLABRelease>{min_release}</MinimumSupportedMATLABRelease>",
        "</InternalData>",
        "%}",
        "",
        "%---",
        "%[app:thumbnail]",
        "%{",
        "<!-- Thumbnail is used by file previewers. To change how the thumbnail is"
        " captured or stored, use the App Details dialog box in App Designer. -->",
        "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>",
        "<Thumbnail autoCapture='true'></Thumbnail>",
        "%}",
    ]

    return "\n".join(classdef_lines + appendix_lines) + "\n"


def _inject_axes(line: str, axes_name: str) -> str:
    """Prepend app.<axes_name> as first argument to recognized plotting function calls."""
    for fn in _PLOT_FUNCTIONS:
        line = re.sub(rf"\b{re.escape(fn)}\s*\(", f"{fn}(app.{axes_name}, ", line)
    return line


def _prefix_vars(code: str, prop_names: list) -> str:
    for name in prop_names:
        code = re.sub(rf"(?<!\.)\b{re.escape(name)}\b", f"app.{name}", code)
    return code


def _prev_release(release: str) -> str:
    m = re.match(r"R(\d{4})([ab])$", release)
    if not m:
        return release
    year, half = int(m.group(1)), m.group(2)
    return f"R{year}a" if half == "b" else f"R{year - 1}b"
