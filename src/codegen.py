import re
import uuid as uuid_mod

from .ir import AppIR

# Default geometry constants (small canvas, existing exemplars)
_FIGURE_POSITION = "[100 100 640 480]"
_BUTTON_POSITION = "[272 219 100 22]"
_DROPDOWN_POSITION = "[270 229 100 22]"
_UIAXES_POSITION_SMALL = "[15 15 610 440]"

# Layout engine constants (1440x1024 canvas)
_CANVAS_LARGE = "[100 100 1440 1024]"
_LAYOUT_MARGIN = 20
_LAYOUT_USABLE_W = 1400   # 1440 - 2*20
_LAYOUT_USABLE_H = 984    # 1024 - 2*20
_LAYOUT_TOP = _LAYOUT_MARGIN + _LAYOUT_USABLE_H  # 1004 (top of usable area in MATLAB coords)
_ROW_GAP = 10

_LABEL_HEIGHTS = {'heading': 40, 'text': 22}
_UIAXES_HEIGHT = 440

_PLOT_FUNCTIONS = frozenset({
    "plot", "scatter", "bar", "barh", "histogram", "imagesc", "surf",
    "mesh", "contour", "fplot", "polarplot", "loglog", "semilogx",
    "semilogy", "stem", "stairs", "area", "fill", "pie",
})


def generate_layout_xml(ir: AppIR) -> str:
    if ir.labels:
        return _generate_layout_xml_with_engine(ir)
    return _generate_layout_xml_fixed(ir)


def _generate_layout_xml_fixed(ir: AppIR) -> str:
    """Original fixed-position layout for exemplars without formatted text."""
    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<Components>",
        "    <UIFigure name='UIFigure'>",
        "        <Name>'MATLAB App'</Name>",
        f"        <Position>{_FIGURE_POSITION}</Position>",
        "        <Children>",
    ]
    for sec in ir.button_sections:
        btn_name = f"{sec.label}Button"
        cb_name = f"{sec.label}ButtonPushed"
        lines += [
            f"            <Button name='{btn_name}'>",
            f"                <ButtonPushedFcn>{cb_name}</ButtonPushedFcn>",
            f"                <Position>{_BUTTON_POSITION}</Position>",
            f"                <Text>'{sec.label}'</Text>",
            "            </Button>",
        ]
    for sec in ir.dropdown_sections:
        items_str = "{" + ", ".join(f"'{item}'" for item in sec.items) + "}"
        lines += [
            f"            <DropDown name='{sec.component_name}'>",
            f"                <Items>{items_str}</Items>",
            f"                <Position>{_DROPDOWN_POSITION}</Position>",
            f"                <Value>'{sec.default_value}'</Value>",
            f"                <ValueChangedFcn>{sec.callback_name}</ValueChangedFcn>",
            f"            </DropDown>",
        ]
    if ir.startup_lines:
        lines += [
            "            <UIAxes name='UIAxes'>",
            f"                <Position>{_UIAXES_POSITION_SMALL}</Position>",
            "            </UIAxes>",
        ]
    lines += [
        "        </Children>",
        "    </UIFigure>",
        "</Components>",
    ]
    return "\n".join(lines)


def _generate_layout_xml_with_engine(ir: AppIR) -> str:
    """Layout engine path: 1440x1024 canvas, y_cursor placement."""
    y_cursor = _LAYOUT_TOP
    child_lines = []

    # Labels (in order)
    for i, label in enumerate(ir.labels, 1):
        h = _LABEL_HEIGHTS.get(label.style, 22)
        bottom = y_cursor - h
        pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {h}]"
        y_cursor = bottom - _ROW_GAP

        child_lines.append(f"            <Label name='Label_{i}'>")
        if label.style == 'heading':
            child_lines.append(f"                <FontSize>18</FontSize>")
            child_lines.append(f"                <FontWeight>'bold'</FontWeight>")
        child_lines.append(f"                <Position>{pos}</Position>")
        child_lines.append(f"                <Text>'{label.text}'</Text>")
        if label.style == 'text':
            child_lines.append(f"                <WordWrap>'on'</WordWrap>")
        child_lines.append(f"            </Label>")

    # UIAxes
    if ir.startup_lines:
        bottom = y_cursor - _UIAXES_HEIGHT
        pos = f"[{_LAYOUT_MARGIN} {bottom} {_LAYOUT_USABLE_W} {_UIAXES_HEIGHT}]"
        child_lines += [
            "            <UIAxes name='UIAxes'>",
            f"                <Position>{pos}</Position>",
            "            </UIAxes>",
        ]

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

    prop_names = [name for name, _ in ir.private_props]

    # --- Public properties block ---
    component_names = ["UIFigure"]
    type_map = {"UIFigure": "matlab.ui.Figure"}

    for i, _ in enumerate(ir.labels, 1):
        component_names.append(f"Label_{i}")
        type_map[f"Label_{i}"] = "matlab.ui.control.Label"

    for sec in ir.button_sections:
        component_names.append(f"{sec.label}Button")
        type_map[f"{sec.label}Button"] = "matlab.ui.control.Button"

    for sec in ir.dropdown_sections:
        component_names.append(sec.component_name)
        type_map[sec.component_name] = "matlab.ui.control.DropDown"

    if ir.startup_lines:
        component_names.append("UIAxes")
        type_map["UIAxes"] = "matlab.ui.control.UIAxes"

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

    # --- Callbacks block ---
    cb_lines = []
    for sec in ir.button_sections:
        btn_name = f"{sec.label}Button"
        cb_name = f"{sec.label}ButtonPushed"
        cb_lines.append(f"        % Button pushed function: {btn_name}")
        cb_lines.append(f"        function {cb_name}(app, event)")
        for line in sec.code_lines:
            cb_lines.append(f"            {_prefix_vars(line.strip(), prop_names)}")
        cb_lines.append("        end")
    for sec in ir.dropdown_sections:
        cb_lines.append(f"        % Value changed function: {sec.component_name}")
        cb_lines.append(f"        function {sec.callback_name}(app, event)")
        cb_lines.append(f"            app.{sec.bound_var} = app.{sec.component_name}.Value;")
        for line in sec.code_lines:
            cb_lines.append(f"            {_prefix_vars(line.strip(), prop_names)}")
        cb_lines.append("        end")
    if ir.startup_lines:
        cb_lines.append("        % Code that executes after component creation")
        cb_lines.append("        function startupFcn(app)")
        for line in ir.startup_lines:
            cb_lines.append(f"            {_inject_axes(line.strip())}")
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
    if ir.startup_lines:
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


def _inject_axes(line: str) -> str:
    """Prepend app.UIAxes as first argument to recognized plotting function calls."""
    for fn in _PLOT_FUNCTIONS:
        line = re.sub(rf"\b{re.escape(fn)}\s*\(", f"{fn}(app.UIAxes, ", line)
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
