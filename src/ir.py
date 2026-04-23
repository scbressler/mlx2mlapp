from dataclasses import dataclass, field


@dataclass
class LabelIR:
    style: str   # 'heading' or 'text'
    text: str


@dataclass
class ButtonSection:
    label: str           # display text, e.g. "Run" or "Plot it"
    code_lines: list     # list of str, stripped
    component_name: str = ""         # PascalCase identifier, e.g. "Run" or "PlotIt"; set by parser
    code_text_area_name: str = ""    # set by codegen: e.g. "RunCodeTextArea"
    output_text_area_name: str = ""  # set by codegen: e.g. "RunOutputTextArea"


@dataclass
class DropDownSection:
    component_name: str  # e.g. "DropDown"
    bound_var: str       # e.g. "value"
    items: list          # e.g. ["one", "two"]
    default_value: str   # e.g. "one" (raw, no quotes)
    callback_name: str   # e.g. "DropDownValueChanged"
    code_lines: list     # remaining lines after bound-var assignment removed
    code_text_area_name: str = ""    # set by codegen: e.g. "DropDownCodeTextArea"
    output_text_area_name: str = ""  # set by codegen: e.g. "DropDownOutputTextArea"


@dataclass
class ControlSection:
    """Generic interactive control: Slider, Spinner, RangeSlider, CheckBox,
    StateButton, NumericEditField, EditField, ColorPicker, DatePicker, FileBrowser."""
    control_type: str      # 'slider','spinner','rangeslider','checkbox','statebutton',
                           # 'editfield_numeric','editfield_text','colorpicker',
                           # 'datepicker','filebrowser'
    component_name: str    # PascalCase from livecontrol label, e.g. "Slider"
    bound_var: str         # MATLAB variable name (LHS of matching assignment); "" if none
    default_value: str     # MATLAB expression for private property init, e.g. "0", "''"
    callback_name: str     # e.g. "SliderValueChanged"
    code_lines: list       # remaining code after bound-var line removed
    limits: str = ""       # "[min max]" for slider/spinner/rangeslider; "" otherwise
    step: object = None    # numeric step for spinner; None for others
    display_format: str = ""   # DatePicker displayFormat, e.g. "dd-MMM-uuuu"
    browser_type: str = ""     # FileBrowser browserType, e.g. "File"
    code_text_area_name: str = ""    # set by codegen
    output_text_area_name: str = ""  # set by codegen


@dataclass
class SectionIR:
    labels: list             # list of LabelIR (heading/text for this section)
    plot_lines: list         # all code lines when section has a plot call; else []
    button_sections: list    # list of ButtonSection in this section
    dropdown_sections: list  # list of DropDownSection in this section
    control_sections: list = field(default_factory=list)  # list of ControlSection
    axes_name: str = ""      # set by codegen: "UIAxes" or "UIAxes_N"
    code_lines: list = field(default_factory=list)   # raw code lines for CodeTextArea (display sections)
    code_text_area_name: str = ""    # set by codegen: "CodeTextArea" or "CodeTextArea_N"
    output_text_area_name: str = ""  # set by codegen: "OutputTextArea" or "OutputTextArea_N"


@dataclass
class AppIR:
    class_name: str
    private_props: list   # list of (name: str, init_expr: str); from init sections
    sections: list        # ordered list of SectionIR
