# Contract: Code Section with ComboBox (Dropdown) Livecontrol

This spec defines how a Live Script section containing a comboBox livecontrol
maps to an App Designer DropDown component and callback.

---

## Input: ComboBox Section

A Live Script section containing:
- One or more `<w:pStyle w:val="code"/>` paragraphs with MATLAB code
- An embedded `livecontrol` customXml element with `"type": "comboBox"`

The comboBox livecontrol carries:
- `data.text` — display label (e.g. `"Drop down"`)
- `data.itemLabels` — list of item display strings (e.g. `["one", "two"]`)
- `data.defaultValue` — MATLAB expression for the current value (e.g. `"\"one\""`)
- `data.linkedVariable` — variable name if explicitly linked (may be empty)

---

## Bound Variable Detection

The bound variable is the MATLAB variable managed by the comboBox.

Detection rule (applied in order):
1. If `data.linkedVariable` is non-empty, use it directly.
2. Otherwise, find the first assignment in the code whose RHS, when stripped of
   outer double-quotes, matches the `defaultValue` (similarly stripped).
   The LHS of that assignment is the bound variable.

The bound-variable assignment line is **removed** from the callback code body.

---

## Component Name

The component name is derived from `data.text` by converting to PascalCase
(capitalize each word, remove spaces).

Example: `"Drop down"` → `DropDown`

---

## Output: Component

- **Type**: `DropDown` in layout XML; `matlab.ui.control.DropDown` in classdef
- **Name attribute**: the PascalCase component name
- **Items**: MATLAB cell array from `itemLabels` with char-vector elements
  (e.g. `{'one', 'two'}`)
- **Value**: char vector of the raw default value (e.g. `'one'`)
- **ValueChangedFcn**: `{ComponentName}ValueChanged`
- Properties are serialized in alphabetical order (`Items`, `Position`, `Value`,
  `ValueChangedFcn`)
- Dropdown sections always use the layout engine path (1100×760 canvas).
  Dropdown height: 32px, full usable width (1060px), left-aligned at x=20.
- Two TextArea components follow: `{ComponentName}CodeTextArea` and
  `{ComponentName}OutputTextArea`. See `specs/output_capture.md` for styling.

---

## Output: Private Property

The bound variable becomes a private property initialized to a char vector of
the raw default value.

Example: bound variable `value`, defaultValue `"one"` → `value = 'one' % Description`

Note: MATLAB double-quoted strings from the Live Script are converted to
char vectors (`'...'`) to match the type returned by `DropDown.Value`.

---

## Output: Callback

The callback name is `{ComponentName}ValueChanged`.

The callback body:
1. First line: `app.{bound_var} = app.{ComponentName}.Value;`
2. `diary` capture block (see `specs/output_capture.md`)
3. Remaining code lines (bound-var assignment removed), with private prop names prefixed `app.`
4. `diary` teardown and `app.{ComponentName}OutputTextArea.Value = ...`

Example:

Original code (`value  = "one";\ndisp(value);`), bound var `value`:

```matlab
% Value changed function: DropDown
function DropDownValueChanged(app, event)
    app.value = app.DropDown.Value;
    diaryFile = [tempname '.txt'];
    diary(diaryFile);
    diary('on');
    disp(app.value);
    diary('off');
    if exist(diaryFile, 'file')
        capturedOutput = fileread(diaryFile);
        delete(diaryFile);
    else
        capturedOutput = '';
    end
    app.DropDownOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
end
```

---

## Out of Scope for This Contract

- ComboBox with `linkedVariable` set to a non-empty string (not yet tested)
- Items with non-string values
- Multi-select or editable dropdowns
- Sections with both a dropdown and other interactive livecontrols
