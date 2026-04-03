"""
codegen.py — Generate an App Designer classdef from a LiveScript IR.

Strategy
--------
All code sections are concatenated into a single private ``runScript``
method.  Before the code runs, local variable aliases are read from UI
component values::

    freq = app.freqSlider.Value;
    plot_type = app.plot_typeDropDown.Value;

Variables assigned from ``figure()`` / ``axes()`` calls are detected and
removed; their references are rewritten to ``app.UIAxes``.

A ``startupFcn`` initialises the app and calls ``runScript``.
A "Run" button callback also calls ``runScript``.

UI layout
---------
- Window: 640 × 480
- UIAxes fills the top portion (y = 100 → 440)
- Control rows occupy the bottom strip, each row is 30 px tall
- Sliders are 200 px wide; dropdowns / edit fields are 120 px wide
- Each control has a right-aligned label 80 px to its left
"""

from __future__ import annotations

import re
import textwrap
import uuid
from typing import Any

from .parser import Control, LiveScript, Section


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate(ls: LiveScript, app_name: str = "GeneratedApp") -> str:
    """Return the full App Designer classdef string for *ls*."""
    gen = _Generator(ls, app_name)
    return gen.build()


# ---------------------------------------------------------------------------
# Internal generator
# ---------------------------------------------------------------------------

_FIGURE_W = 640
_FIGURE_H = 480
_AXES_PAD_LEFT   = 60
_AXES_PAD_RIGHT  = 20
_AXES_PAD_TOP    = 20
_CTRL_ROW_H      = 30
_CTRL_AREA_TOP   = 10   # y from bottom for control area
_LABEL_W         = 80
_SLIDER_W        = 200
_COMBO_W         = 150
_EDIT_W          = 100
_BUTTON_W        = 80


class _Generator:

    def __init__(self, ls: LiveScript, app_name: str):
        self.ls = ls
        self.app_name = _sanitize_name(app_name)
        self.controls = ls.all_controls
        # Variables that are driven by UI controls
        self.live_vars: set[str] = {c.variable for c in self.controls}
        # Variables assigned from figure()/axes() — these map to app.UIAxes
        self.axes_vars: set[str] = set()
        self.figure_vars: set[str] = set()
        self._scan_axes_vars()

    # ------------------------------------------------------------------
    # Top-level builder
    # ------------------------------------------------------------------

    def build(self) -> str:
        parts = [
            self._class_header(),
            self._public_properties(),
            self._private_properties(),
            self._callback_methods(),
            self._create_components_method(),
            self._constructor_methods(),
            "end  % classdef",
        ]
        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _class_header(self) -> str:
        return f"classdef {self.app_name} < matlab.apps.AppBase"

    def _public_properties(self) -> str:
        lines = [
            "    % Properties that correspond to app components",
            "    properties (Access = public)",
            "        UIFigure    matlab.ui.Figure",
            "        UIAxes      matlab.ui.control.UIAxes",
            "        RunButton   matlab.ui.control.Button",
        ]
        for c in self.controls:
            prop_name = _component_name(c)
            matlab_type = _matlab_type(c)
            lines.append(f"        {prop_name:<30} {matlab_type}")
            label_name = _label_name(c)
            lines.append(f"        {label_name:<30} matlab.ui.control.Label")
        lines.append("    end")
        return "\n".join(lines)

    def _private_properties(self) -> str:
        if not self.live_vars:
            return "    properties (Access = private)\n    end"
        lines = ["    properties (Access = private)"]
        for v in sorted(self.live_vars):
            lines.append(f"        {v}")
        lines.append("    end")
        return "\n".join(lines)

    def _callback_methods(self) -> str:
        blocks = [
            "    methods (Access = private)",
            "",
            self._startup_fcn(),
            "",
            self._run_script_method(),
            "",
            self._run_button_callback(),
            "",
            "    end",
        ]
        return "\n".join(blocks)

    def _startup_fcn(self) -> str:
        lines = [
            "        % Code that executes after component creation",
            "        function startupFcn(app)",
        ]
        # Read UI defaults into private properties
        for c in self.controls:
            prop = _component_name(c)
            lines.append(f"            app.{c.variable} = app.{prop}.Value;")
        lines.append("            runScript(app);")
        lines.append("        end")
        return "\n".join(lines)

    def _run_script_method(self) -> str:
        lines = [
            "        % Execute the converted LiveScript logic",
            "        function runScript(app)",
            "            % Read current UI values into local variables",
        ]
        for c in self.controls:
            prop = _component_name(c)
            lines.append(f"            {c.variable} = app.{prop}.Value;")

        lines.append("")
        lines.append("            % Clear axes before redraw")
        lines.append("            cla(app.UIAxes, 'reset');")
        lines.append("")

        # Emit all code sections (transformed)
        all_code = self._collect_and_transform_code()
        if all_code:
            for ln in all_code.splitlines():
                lines.append(f"            {ln}")

        lines.append("        end")
        return "\n".join(lines)

    def _run_button_callback(self) -> str:
        return (
            "        % Button pushed function: RunButton\n"
            "        function RunButtonPushed(app, event)\n"
            "            runScript(app);\n"
            "        end"
        )

    def _create_components_method(self) -> str:
        lines = [
            "    methods (Access = private)",
            "",
            "        % Create UIFigure and components",
            "        function createComponents(app)",
            "",
            f"            % Create UIFigure",
            f"            app.UIFigure = uifigure('Visible', 'off');",
            f"            app.UIFigure.Position = [100 100 {_FIGURE_W} {_FIGURE_H}];",
            f"            app.UIFigure.Name = '{self.app_name}';",
            "",
            "            % Create UIAxes",
            "            app.UIAxes = uiaxes(app.UIFigure);",
        ]

        # Axes geometry: leave room at bottom for controls + Run button
        n_ctrl_rows = len(self.controls)
        ctrl_area_h = max(n_ctrl_rows, 1) * _CTRL_ROW_H + 10
        axes_h = _FIGURE_H - _AXES_PAD_TOP - ctrl_area_h - 10
        axes_w = _FIGURE_W - _AXES_PAD_LEFT - _AXES_PAD_RIGHT
        axes_y = ctrl_area_h + 10  # bottom of axes (MATLAB uses lower-left origin)

        lines += [
            f"            title(app.UIAxes, '');",
            f"            xlabel(app.UIAxes, '');",
            f"            ylabel(app.UIAxes, '');",
            f"            app.UIAxes.Position = [{_AXES_PAD_LEFT} {axes_y} {axes_w} {axes_h}];",
            "",
        ]

        # Controls
        for idx, c in enumerate(self.controls):
            row_y = ctrl_area_h - (idx + 1) * _CTRL_ROW_H + 5
            lines += self._create_control_code(c, idx, row_y)
            lines.append("")

        # Run button — right side of the bottom strip
        run_y = 10
        run_x = _FIGURE_W - _BUTTON_W - 20
        lines += [
            "            % Create RunButton",
            "            app.RunButton = uibutton(app.UIFigure, 'push');",
            "            app.RunButton.ButtonPushedFcn = createCallbackFcn(app, @RunButtonPushed, true);",
            f"            app.RunButton.Position = [{run_x} {run_y} {_BUTTON_W} 22];",
            "            app.RunButton.Text = 'Run';",
            "",
            "            % Show the figure",
            "            app.UIFigure.Visible = 'on';",
            "        end",
            "    end",
        ]
        return "\n".join(lines)

    def _constructor_methods(self) -> str:
        return (
            "    % App creation and deletion\n"
            "    methods (Access = public)\n"
            "\n"
            f"        % Construct app\n"
            f"        function app = {self.app_name}\n"
            "\n"
            "            % Create UIFigure and components\n"
            "            createComponents(app)\n"
            "\n"
            "            % Register the app with App Designer\n"
            "            registerApp(app, app.UIFigure)\n"
            "\n"
            "            % Execute the startup function\n"
            "            runStartupFcn(app, @startupFcn)\n"
            "\n"
            "            if nargout == 0\n"
            "                clear app\n"
            "            end\n"
            "        end\n"
            "\n"
            "        % Code that executes before app deletion\n"
            "        function delete(app)\n"
            "            delete(app.UIFigure)\n"
            "        end\n"
            "    end"
        )

    # ------------------------------------------------------------------
    # Control component creation code
    # ------------------------------------------------------------------

    def _create_control_code(self, c: Control, idx: int, row_y: int) -> list[str]:
        label_name = _label_name(c)
        prop_name  = _component_name(c)
        label_x    = 10
        ctrl_x     = label_x + _LABEL_W + 5

        lines = [
            f"            % Create {label_name}",
            f"            app.{label_name} = uilabel(app.UIFigure);",
            f"            app.{label_name}.HorizontalAlignment = 'right';",
            f"            app.{label_name}.Position = [{label_x} {row_y} {_LABEL_W} 22];",
            f"            app.{label_name}.Text = '{c.label}';",
            "",
        ]

        if c.type == "slider":
            ctrl_w = _SLIDER_W
            lines += [
                f"            % Create {prop_name}",
                f"            app.{prop_name} = uislider(app.UIFigure);",
            ]
            if c.min is not None:
                lines.append(f"            app.{prop_name}.Limits = [{c.min} {c.max}];")
            if c.step is not None and c.min is not None and c.max is not None:
                n_steps = max(1, round((c.max - c.min) / c.step))
                lines.append(f"            app.{prop_name}.MajorTicks = linspace({c.min}, {c.max}, min({n_steps}+1, 6));")
            default_val = _format_matlab_value(c.default)
            lines += [
                f"            app.{prop_name}.Value = {default_val};",
                f"            app.{prop_name}.Position = [{ctrl_x} {row_y + 5} {ctrl_w} 3];",
            ]

        elif c.type == "comboBox":
            ctrl_w = _COMBO_W
            items_str = _format_matlab_cell(c.item_labels or c.items or [])
            default_val = f"'{c.default}'" if c.default else "''"
            lines += [
                f"            % Create {prop_name}",
                f"            app.{prop_name} = uidropdown(app.UIFigure);",
                f"            app.{prop_name}.Items = {items_str};",
                f"            app.{prop_name}.Value = {default_val};",
                f"            app.{prop_name}.Position = [{ctrl_x} {row_y} {ctrl_w} 22];",
            ]

        elif c.type == "editField":
            ctrl_w = _EDIT_W
            default_val = _format_matlab_value(c.default)
            lines += [
                f"            % Create {prop_name}",
                f"            app.{prop_name} = uieditfield(app.UIFigure, 'numeric');",
                f"            app.{prop_name}.Value = {default_val};",
                f"            app.{prop_name}.Position = [{ctrl_x} {row_y} {ctrl_w} 22];",
            ]

        return lines

    # ------------------------------------------------------------------
    # Code transformation
    # ------------------------------------------------------------------

    def _scan_axes_vars(self) -> None:
        """Detect variables assigned from figure()/axes() calls."""
        for s in self.ls.sections:
            for line in s.code.splitlines():
                m = re.match(r"\s*([A-Za-z_]\w*)\s*=\s*axes\s*[;(]", line)
                if m:
                    self.axes_vars.add(m.group(1))
                m = re.match(r"\s*([A-Za-z_]\w*)\s*=\s*figure\s*[;(]", line)
                if m:
                    self.figure_vars.add(m.group(1))

    def _collect_and_transform_code(self) -> str:
        """Concatenate all code sections and apply transformations."""
        raw_lines: list[str] = []
        for s in self.ls.sections:
            if s.code:
                raw_lines.extend(s.code.splitlines())
                raw_lines.append("")  # blank line between sections

        transformed: list[str] = []
        for line in raw_lines:
            line = self._transform_line(line)
            if line is not None:
                transformed.append(line)

        return "\n".join(transformed)

    def _transform_line(self, line: str) -> str | None:
        """
        Return the transformed line, or None to drop the line entirely.
        Applies these rewrites in order:
          1. Drop figure()/axes() assignment lines
          2. Drop bare figure/axes calls
          3. Drop live-variable assignment lines (values come from UI now)
          4. Rewrite axes-variable references → app.UIAxes
          5. Rewrite figure-variable references → app.UIFigure (unused but safe)
          6. grid on/off → explicit property sets on app.UIAxes
          7. hold on/off → hold(app.UIAxes, ...)
          8. title/xlabel/ylabel/zlabel bare calls → prefixed with app.UIAxes
          9. legend(...) → legend(app.UIAxes, ...)
        """
        stripped = line.strip()

        # 1. Drop  varname = figure(...) / varname = axes(...)
        for var in self.figure_vars | self.axes_vars:
            if re.match(rf"\s*{re.escape(var)}\s*=\s*(figure|axes)\s*[;(]", line):
                return None

        # 2. Drop bare figure/axes calls
        if re.match(r"\s*(figure|axes)\s*[;(]", line):
            return None

        # 3. Drop re-assignment of live variables
        #    (they are read from UI components at the top of runScript)
        for var in self.live_vars:
            if re.match(rf"\s*{re.escape(var)}\s*=", line):
                return None

        # 4. Rewrite axes variables → app.UIAxes
        for var in self.axes_vars:
            line = re.sub(rf"\b{re.escape(var)}\b", "app.UIAxes", line)

        # 5. Rewrite figure variables → app.UIFigure
        for var in self.figure_vars:
            line = re.sub(rf"\b{re.escape(var)}\b", "app.UIFigure", line)

        # 6. grid on/off
        if re.match(r"\s*grid\s+on\s*;?\s*$", line):
            return ("app.UIAxes.XGrid = 'on'; "
                    "app.UIAxes.YGrid = 'on';")
        if re.match(r"\s*grid\s+off\s*;?\s*$", line):
            return ("app.UIAxes.XGrid = 'off'; "
                    "app.UIAxes.YGrid = 'off';")

        # 7. hold on/off
        line = re.sub(r"\bhold\s+on\b", "hold(app.UIAxes, 'on')", line)
        line = re.sub(r"\bhold\s+off\b", "hold(app.UIAxes, 'off')", line)

        # 8. standalone title/xlabel/ylabel/zlabel calls without an axes arg
        #    e.g.  title('foo')  →  title(app.UIAxes, 'foo')
        for fn in ("title", "xlabel", "ylabel", "zlabel"):
            line = re.sub(
                rf"\b{fn}\s*\((?!app\.UIAxes)",
                f"{fn}(app.UIAxes, ",
                line,
            )

        # 9. legend(...) → legend(app.UIAxes, ...)
        line = re.sub(
            r"\blegend\s*\((?!app\.UIAxes)",
            "legend(app.UIAxes, ",
            line,
        )

        return line


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitize_name(name: str) -> str:
    """Make *name* a valid MATLAB identifier."""
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if name and name[0].isdigit():
        name = "App_" + name
    return name or "GeneratedApp"


def _component_name(c: Control) -> str:
    """Return the App Designer property name for a control."""
    base = _sanitize_name(c.variable)
    suffix = {"slider": "Slider", "comboBox": "DropDown", "editField": "EditField"}
    return base + suffix.get(c.type, "Control")


def _label_name(c: Control) -> str:
    return _component_name(c) + "Label"


def _matlab_type(c: Control) -> str:
    return {
        "slider":    "matlab.ui.control.Slider",
        "comboBox":  "matlab.ui.control.DropDown",
        "editField": "matlab.ui.control.NumericEditField",
    }.get(c.type, "matlab.ui.control.NumericEditField")


def _format_matlab_value(v: Any) -> str:
    if v is None:
        return "0"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return f"'{v}'"


def _format_matlab_cell(items: list[str]) -> str:
    """Format a Python list as a MATLAB cell array string: {'a', 'b'}"""
    quoted = ", ".join(f"'{i}'" for i in items)
    return "{" + quoted + "}"
