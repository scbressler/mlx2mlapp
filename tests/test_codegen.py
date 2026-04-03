"""Tests for src/codegen.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.parser import LiveScript, Section, Control
from src.codegen import generate, _sanitize_name, _component_name, _label_name, _format_matlab_cell


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_ls_with_slider() -> LiveScript:
    ctrl = Control(
        type="slider", variable="freq", label="Frequency",
        default=100, min=1, max=500, step=10,
    )
    section = Section(
        heading="Test",
        code="freq = 100;\ny = sin(2*pi*freq*t);\n",
        controls=[ctrl],
    )
    return LiveScript(sections=[section])


def _make_ls_with_combobox() -> LiveScript:
    ctrl = Control(
        type="comboBox", variable="mode", label="Mode",
        default="fast", items=["fast", "slow"], item_labels=["fast", "slow"],
    )
    section = Section(
        heading="Test",
        code='mode = "fast";\ndisp(mode);\n',
        controls=[ctrl],
    )
    return LiveScript(sections=[section])


def _make_ls_with_axes() -> LiveScript:
    section = Section(
        heading="Plot",
        code=(
            "t = 0:0.01:1;\n"
            "fig = figure;\n"
            "ax = axes;\n"
            "plot(ax, t, sin(t));\n"
            "title('Test');\n"
            "xlabel('Time');\n"
            "ylabel('Amp');\n"
            "grid on;\n"
        ),
        controls=[],
    )
    return LiveScript(sections=[section])


# ---------------------------------------------------------------------------
# Tests: classdef structure
# ---------------------------------------------------------------------------

class TestClassdefStructure:

    def test_contains_classdef_declaration(self):
        ls = _make_ls_with_slider()
        code = generate(ls, "MyApp")
        assert "classdef MyApp < matlab.apps.AppBase" in code

    def test_contains_public_properties(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "properties (Access = public)" in code
        assert "UIFigure" in code
        assert "UIAxes" in code
        assert "RunButton" in code

    def test_contains_private_methods(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "methods (Access = private)" in code

    def test_contains_startup_fcn(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "function startupFcn(app)" in code

    def test_contains_run_script(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "function runScript(app)" in code

    def test_contains_run_button_callback(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "function RunButtonPushed(app, event)" in code

    def test_contains_create_components(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "function createComponents(app)" in code

    def test_contains_constructor(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "function app = MyApp" in code

    def test_contains_delete_method(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert "function delete(app)" in code

    def test_ends_with_end(self):
        code = generate(_make_ls_with_slider(), "MyApp")
        assert code.strip().endswith("end  % classdef")


# ---------------------------------------------------------------------------
# Tests: slider control generation
# ---------------------------------------------------------------------------

class TestSliderGeneration:

    def setup_method(self):
        self.code = generate(_make_ls_with_slider(), "SliderApp")

    def test_slider_property_declared(self):
        assert "freqSlider" in self.code
        assert "matlab.ui.control.Slider" in self.code

    def test_slider_label_declared(self):
        assert "freqSliderLabel" in self.code

    def test_uislider_created(self):
        assert "uislider" in self.code

    def test_slider_limits_set(self):
        assert "Limits = [1 500]" in self.code

    def test_slider_default_value(self):
        assert "Value = 100" in self.code

    def test_live_var_read_in_run_script(self):
        # runScript should read: freq = app.freqSlider.Value;
        assert "freq = app.freqSlider.Value;" in self.code

    def test_live_var_assignment_dropped_from_code(self):
        # The line "freq = 100;" should NOT appear in runScript
        # (it is replaced by the UI read)
        assert "freq = 100;" not in self.code

    def test_private_property_for_live_var(self):
        assert "properties (Access = private)" in self.code
        # freq should be listed as a private property
        lines = self.code.splitlines()
        in_private = False
        found = False
        for ln in lines:
            if "properties (Access = private)" in ln:
                in_private = True
            if in_private and ln.strip() == "freq":
                found = True
                break
            if in_private and ln.strip() == "end":
                in_private = False
        assert found, "freq not found in private properties"


# ---------------------------------------------------------------------------
# Tests: comboBox control generation
# ---------------------------------------------------------------------------

class TestComboBoxGeneration:

    def setup_method(self):
        self.code = generate(_make_ls_with_combobox(), "ComboApp")

    def test_dropdown_property_declared(self):
        assert "modeDropDown" in self.code
        assert "matlab.ui.control.DropDown" in self.code

    def test_uidropdown_created(self):
        assert "uidropdown" in self.code

    def test_items_set(self):
        assert "{'fast', 'slow'}" in self.code

    def test_default_value_set(self):
        assert "Value = 'fast'" in self.code

    def test_live_var_read_in_run_script(self):
        assert "mode = app.modeDropDown.Value;" in self.code


# ---------------------------------------------------------------------------
# Tests: axes/figure variable transformation
# ---------------------------------------------------------------------------

class TestAxesTransformation:

    def setup_method(self):
        self.code = generate(_make_ls_with_axes(), "AxesApp")

    def test_figure_assignment_dropped(self):
        assert "fig = figure" not in self.code

    def test_axes_assignment_dropped(self):
        assert "ax = axes" not in self.code

    def test_axes_var_rewritten_to_app_uiaxes(self):
        assert "plot(app.UIAxes, t, sin(t));" in self.code

    def test_title_prefixed_with_uiaxes(self):
        assert "title(app.UIAxes," in self.code

    def test_xlabel_prefixed_with_uiaxes(self):
        assert "xlabel(app.UIAxes," in self.code

    def test_ylabel_prefixed_with_uiaxes(self):
        assert "ylabel(app.UIAxes," in self.code

    def test_grid_on_converted(self):
        assert "app.UIAxes.XGrid = 'on'" in self.code
        assert "app.UIAxes.YGrid = 'on'" in self.code

    def test_cla_added_at_top_of_run_script(self):
        assert "cla(app.UIAxes, 'reset');" in self.code


# ---------------------------------------------------------------------------
# Tests: helper functions
# ---------------------------------------------------------------------------

class TestHelpers:

    def test_sanitize_name_removes_special_chars(self):
        assert _sanitize_name("my-app.v2") == "my_app_v2"

    def test_sanitize_name_prefixes_digit(self):
        assert _sanitize_name("2app").startswith("App_")

    def test_component_name_slider(self):
        c = Control(type="slider", variable="freq", label="f", default=1)
        assert _component_name(c) == "freqSlider"

    def test_component_name_combobox(self):
        c = Control(type="comboBox", variable="mode", label="m", default="a")
        assert _component_name(c) == "modeDropDown"

    def test_component_name_editfield(self):
        c = Control(type="editField", variable="val", label="v", default=0)
        assert _component_name(c) == "valEditField"

    def test_label_name(self):
        c = Control(type="slider", variable="freq", label="f", default=1)
        assert _label_name(c) == "freqSliderLabel"

    def test_format_matlab_cell(self):
        assert _format_matlab_cell(["a", "b", "c"]) == "{'a', 'b', 'c'}"

    def test_format_matlab_cell_empty(self):
        assert _format_matlab_cell([]) == "{}"


# ---------------------------------------------------------------------------
# Tests: empty LiveScript
# ---------------------------------------------------------------------------

class TestEmptyLiveScript:

    def test_empty_livescript_generates_valid_classdef(self):
        ls = LiveScript(sections=[])
        code = generate(ls, "EmptyApp")
        assert "classdef EmptyApp" in code
        assert "end  % classdef" in code
