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
- Control widget: 32 px tall, full usable width (1060 px in `output_inline`/`hide_code`;
  520 px in `output_right` left column).
- Below the widget: `{ComponentName}CodeTextArea` (120 px, black bg, white text).
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
  class (App Designer has no native FileBrowser component).
- **Slider**: no `<Step>` property in App Designer XML (only `<Limits>` and `<Value>`).
- **CheckBox / StateButton**: `<Value>` is omitted when the default is `false`
  (App Designer default); `<Text>` uses the PascalCase component name.
- **camelCase type strings**: `colorPicker` and `datePicker` use camelCase in the
  JSON `"type"` field — matched case-sensitively in `_CONTROL_TYPE_MAP`.
