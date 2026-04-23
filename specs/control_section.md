# Spec: Generic Control Section

A **generic control section** is a code section paired with any Live Editor livecontrol
that is not a `button` or `comboBox`. All such controls share a single translation
contract, implemented via the `ControlSection` IR dataclass.

---

## Covered Control Types

| `control_type` token | Live Script `"type"` | App Designer component |
|----------------------|----------------------|------------------------|
| `slider` | `slider` | `Slider` |
| `spinner` | `spinner` | `Spinner` |
| `rangeslider` | `rangeslider` | `RangeSlider` |
| `checkbox` | `checkbox` | `CheckBox` |
| `statebutton` | `statebutton` | `StateButton` |
| `editfield_numeric` | `editfield` (valueType `"Double"`) | `NumericEditField` |
| `editfield_text` | `editfield` (valueType `"String"`) | `EditField` |
| `colorpicker` | `colorPicker` | `ColorPicker` |
| `datepicker` | `datePicker` | `DatePicker` |
| `filebrowser` | `filebrowser` | `EditField` |

---

## Layout

- Always uses the layout engine path (1100×760 canvas).
- Control widget: 32 px tall. **Exception: `slider` is 3 px** (`_SLIDER_NATURAL_HEIGHT`).
  MATLAB's UISlider has a fixed track height; setting 32 triggers "The height of this
  component cannot be changed" and corrupts tick-label rendering.
  - **Non-labeled types** (`slider`, `checkbox`, `statebutton`, `colorpicker`, `filebrowser`):
    full usable width (1060 px in `output_inline`/`hide_code`; 520 px in `output_right` left column),
    positioned at `x = 20` (margin).
  - **Labeled types** (`spinner`, `rangeslider`, `editfield_numeric`, `editfield_text`, `datepicker`):
    a 100 px `<Label>` sibling is emitted to the left; the control starts at `x = 130` with
    width = usable_width − 110 px (950 px in `output_inline`/`hide_code`; 410 px in `output_right`).
- **Slider / RangeSlider tick mark gap**: An extra 20 px is added below the widget (before the
  CodeTextArea) to prevent tick marks from overlapping the TextArea below.
- Below the widget (plus tick gap if applicable): `{ComponentName}CodeTextArea` (120 px, black bg, white text).
- Below that: `{ComponentName}OutputTextArea` (120 px, dark gray bg, green text).
- In `output_right` mode: CodeTextArea in left column, OutputTextArea in right column,
  bottom-aligned to CodeTextArea (same pattern as button/dropdown sections).

---

## IR Fields (`ControlSection`)

| Field | Description |
|-------|-------------|
| `control_type` | Internal token (see table above) |
| `component_name` | PascalCase label (e.g. `"MySlider"`) |
| `bound_var` | Variable name whose init assignment is replaced by `.Value` read (empty if none) |
| `default_value` | MATLAB expression for private property initializer |
| `callback_name` | `{ComponentName}ValueChanged` |
| `code_lines` | Remaining code lines after bound-var assignment removed |
| `limits` | `"[min max]"` string for slider/spinner/rangeslider; `""` otherwise |
| `step` | Step value for spinner only; `None` otherwise |
| `display_format` | `displayFormat` string for datepicker; `""` otherwise |
| `browser_type` | `browserType` string for filebrowser; `""` otherwise |

---

## Bound Variable Detection

The bound variable is the first assignment in the section code whose RHS (after
stripping outer double-quotes) matches the JSON `defaultValue` (normalized):

- `bool` → `"true"` / `"false"`
- `int/float` → integer string when lossless (e.g. `0` not `0.0`)
- string JSON value → stripped of outer double-quotes

The matching assignment line is **removed** from `code_lines`. In the callback,
it is replaced by `app.{bound_var} = app.{ComponentName}.Value;` before the
diary block.

---

## Private Property

- Emitted as `(bound_var, matlab_default)` when a bound var is detected.
- `matlab_default` conversion from JSON `defaultValue`:
  - `bool` → `"true"` / `"false"`
  - `int/float` → integer string when lossless
  - `editfield_text` / `filebrowser` string → char vector `'...'`
  - `rangeslider` / `colorpicker` array string → bare array literal (e.g. `[0 100]`)
- **DatePicker exception:** no `defaultValue` in JSON → no bound var, no private prop.

---

## Callback Structure

```matlab
function {ComponentName}ValueChanged(app, event)
    app.{bound_var} = app.{ComponentName}.Value;   % only if bound_var is set
    diary_file = tempname;
    diary(diary_file);
    diary on;
    {code_lines...}
    diary off;
    output = fileread(diary_file);
    lines = strsplit(output, newline);
    app.{ComponentName}OutputTextArea.Value = lines;
end
```

When `bound_var` is empty, `output_text_area_name` is empty, and `code_lines` is empty,
the body would be completely empty. In that case codegen emits `% value changed` as a
placeholder — an empty Slider callback body crashes App Designer on file open.

---

## Labeled Components

App Designer requires certain controls to have an associated `<Label>` sibling element.
Without it, App Designer throws "Index exceeds the number of array elements" on load.

**Labeled types:** `spinner`, `rangeslider`, `editfield_numeric`, `editfield_text`, `datepicker`

**Non-labeled types:** `slider`, `checkbox`, `statebutton`, `colorpicker`, `filebrowser`

For labeled types, the XML emits a `<Label>` element **before** the main component, and the
main component carries a `label='...'` attribute:

```xml
<Label name='{ComponentName}Label'>
    <HorizontalAlignment>'right'</HorizontalAlignment>
    <Position>[20 {bottom+5} 100 22]</Position>
    <Text>'{ComponentName}'</Text>
</Label>
<Spinner name='{ComponentName}' label='{ComponentName}Label'>
    ...
</Spinner>
```

- Label position: `[margin, bottom + (ctrl_h − label_h) // 2, 100, 22]` — vertically centered
  within the 32 px control row (offset = 5 px from control bottom).
- Label text: the PascalCase component name (same as `component_name`).
- A `{ComponentName}Label  matlab.ui.control.Label` entry is added to the public properties
  block in the `.m` classdef, immediately before the main component entry.

---

## Layout XML Properties (alphabetical, `<Children>` last)

### Common to all control types
- `<Position>` always emitted
- `<ValueChangedFcn>` always emitted

### Type-specific properties

| Property | Condition |
|----------|-----------|
| `<DisplayFormat>` | `datepicker` only |
| `<Limits>` | `slider`, `spinner`, `rangeslider` |
| `<Step>` | `spinner` only |
| `<Text>` | `checkbox`, `statebutton` (PascalCase component name) |
| `<Value>` | All except `datepicker`; numeric/array literals unquoted, char vectors quoted |

---

## Special Cases

- **DatePicker**: no `defaultValue` → `default_value = "NaT"`, `bound_var = ""`,
  no `<Value>` in XML, no private prop emitted.
- **FileBrowser**: maps to `EditField` XML tag and `matlab.ui.control.EditField`
  class (App Designer has no native FileBrowser component). Not a labeled type.
- **Slider**: no `<Step>` property in App Designer XML (only `<Limits>` and `<Value>`).
  Not a labeled type. Height is 3 px (`_SLIDER_NATURAL_HEIGHT`), not 32 px — MATLAB's
  horizontal Slider has a fixed track height; using 32 corrupts tick-label rendering.
  Tick marks require an additional 20 px gap (`_SLIDER_TICK_EXTRA`) below the widget.
  **Empty callback crash**: a Slider whose `ValueChangedFcn` has an empty body triggers
  "Dimensions of position argument…" when App Designer opens the file (unrelated to
  position or limits). Codegen guards against this with `% value changed` placeholder
  when no other lines are generated (see Hard-Won Decisions in CLAUDE.md).
- **RangeSlider**: labeled type AND has tick marks — gets both the `<Label>` sibling
  and the 20 px tick gap before the CodeTextArea.
- **CheckBox / StateButton**: `<Value>` is omitted when the default is `false`
  (App Designer default); `<Text>` uses the PascalCase component name.
- **camelCase type strings**: `colorPicker` and `datePicker` use camelCase in the
  JSON `"type"` field — matched case-sensitively in `_CONTROL_TYPE_MAP`.
