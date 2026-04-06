from dataclasses import dataclass


@dataclass
class LabelIR:
    style: str   # 'heading' or 'text'
    text: str


@dataclass
class ButtonSection:
    label: str         # e.g. "Run"
    code_lines: list   # list of str, stripped


@dataclass
class DropDownSection:
    component_name: str  # e.g. "DropDown"
    bound_var: str       # e.g. "value"
    items: list          # e.g. ["one", "two"]
    default_value: str   # e.g. "one" (raw, no quotes)
    callback_name: str   # e.g. "DropDownValueChanged"
    code_lines: list     # remaining lines after bound-var assignment removed


@dataclass
class AppIR:
    class_name: str
    private_props: list      # list of (name: str, init_expr: str)
    button_sections: list    # list of ButtonSection
    dropdown_sections: list  # list of DropDownSection
    startup_lines: list      # code lines for startupFcn body; empty = no startup
    labels: list             # list of LabelIR; empty = no formatted text
