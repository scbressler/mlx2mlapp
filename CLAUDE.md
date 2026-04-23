# CLAUDE.md — Project Guide for AI Assistants

This file captures the working conventions, architecture decisions, and
translation contracts established during development. Read this before
touching any code.

---

## What This Project Does

Translates MATLAB Live Script files into App Designer plain-text apps
(`.m` with embedded XML appendix). The output must open and be editable in
App Designer — not just runnable.

Input (any of):
- Plain-text Live Script (`.m`, R2025a+)
- Binary Live Script (`.mlx`, unzipped on-the-fly)
- Raw `document.xml` extracted from a `.mlx` archive (legacy/test path)

Output: a single `.m` file containing the classdef + XML appendix

---

## Architecture: Three-Stage Pipeline

```
.m / .mlx / document.xml  →  [parse]  →  AppIR  →  [codegen]  →  .m + layout XML
```

- **`src/parse.py`** — reads `document.xml` (from `.mlx` or raw file), builds `AppIR`
- **`src/parse_plaintext.py`** — reads plain-text Live Script `.m` files (R2025a+), builds same `AppIR`
- **`src/ir.py`** — dataclasses: `AppIR`, `SectionIR`, `ButtonSection`, `DropDownSection`, `ControlSection`, `LabelIR`
- **`src/codegen.py`** — generates layout XML and the full `.m` classdef
- **`src/translate.py`** — entry point; auto-detects format by extension (`.m` → `parse_plaintext`, `.mlx` → unzip+`parse`, else `parse`)

Do not translate directly from Live Script XML to App Designer XML. The IR
is load-bearing: it makes failures explainable and tests meaningful.

---

## How to Add a New Feature

1. Write the spec first (`specs/`) — define what "correct" means before coding
2. Create the golden exemplar (`golden/<name>/input/` and `expected/`)
3. Write the failing test (`tests/test_<name>.py`)
4. Extend IR, parse, codegen until the test passes
5. The spec and golden are the authority — if they conflict with code, fix code

## How to Add a New Widget Type

New Live Editor controls (Slider, Spinner, ColorPicker, etc.) require knowing
the `context` JSON structure embedded in `document.xml` for that control type.
The fastest way to obtain this without zip extraction:

1. Create a minimal Live Script in MATLAB Live Editor using the target control
2. **File → Save As → MATLAB Live Code File (UTF-8) (*.m)** (plain-text format, R2025a+)
3. Read the `%[control:controltype:controlid]` data block in the appendix — that
   JSON contains all field names (type, min, max, step, defaultValue, items, etc.)
4. Use those field names to manually construct `golden/<name>/input/document.xml`
5. Then follow the standard feature workflow above

**Full Live Editor control inventory** (from the Live Script toolstrip):

| Control | `type` string | App Designer component | Status |
|---------|--------------|------------------------|--------|
| Button | `button` | `Button` | ✓ implemented |
| Drop Down | `comboBox` | `DropDown` | ✓ implemented |
| Slider | `slider` | `Slider` | ✓ implemented |
| Spinner | `spinner` | `Spinner` | ✓ implemented |
| Range Slider | `rangeslider` | `RangeSlider` | ✓ implemented |
| Checkbox | `checkbox` | `CheckBox` | ✓ implemented |
| State Button | `statebutton` | `StateButton` | ✓ implemented |
| Edit Field (numeric) | `editfield` (`valueType:"Double"`) | `NumericEditField` | ✓ implemented |
| Edit Field (text) | `editfield` (`valueType:"String"`) | `EditField` | ✓ implemented |
| Color Picker | `colorPicker` | `ColorPicker` | ✓ implemented |
| Date Picker | `datePicker` | `DatePicker` | ✓ implemented |
| File Browser | `filebrowser` | `EditField` (path display) | ✓ implemented |

All 12 Live Editor controls are implemented. No unknowns remain.

**Key discoveries from plain-text `.m` inspection:**
- Both edit field variants share `type: "editfield"`, differentiated by `valueType`
- File Browser is a first-class control (`filebrowser`), not an EditField+Button composite
- Range slider `defaultValue` is a string like `"[0 100]"`, not a pair of numbers
- Color picker `defaultValue` is a string like `"[1 1 1]"` (RGB 0–1 floats)
- Date picker has no `defaultValue` field in the JSON
- Slider, Spinner, and Range Slider all share identical JSON shape (`defaultValue`, `min`, `max`, `step`, `runOn`)
- State Button and Checkbox share identical JSON shape (boolean `defaultValue`, `label`, `run`)

---

## Input Format Details

### Plain-text Live Script (`.m`, R2025a+)
Parsed by `src/parse_plaintext.py`. Key structural elements:

- **Section boundary:** `%[text] optional-heading` starts a new section; the text (after stripping `##` markdown) becomes the section label
- **Inline control annotation:** `code_line  %[control:type:uuid]{...}` on the same line as the bound assignment
- **Standalone control annotation:** `  %[control:type:uuid]` on its own line (button, standalone spinner, etc.)
- **Output annotation:** `code_line  %[output:uuid]` — stripped; the output data is ignored
- **Appendix:** after `%[appendix]`, each control has a `%[control:type:uuid]` header followed by `%   data: {json}` on the next non-blank line
- **Button normalization:** button appendix JSON uses `"label"` not `"text"`; the parser adds `data['text'] = data['label']` to match `parse_document` callers

### Binary Live Script (`.mlx`)
Parsed by extracting `matlab/document.xml` to a temp file and calling `parse.py`. Two differences from hand-crafted golden fixtures that `_normalize_livecontrol()` corrects:

1. **No `"type"` field in context JSON** — type is inferred from the `className` XML attribute via `_CLASSNAME_TO_TYPE`:
   ```
   SpinnerControlNode → spinner,  SliderControlNode → slider,
   RangeSliderControlNode → rangeslider,  CheckBoxControlNode → checkbox,
   StateButtonControlNode → statebutton,  EditFieldControlNode → editfield,
   ColorPickerControlNode → colorPicker,  DatePickerControlNode → datePicker,
   FileBrowserControlNode → filebrowser,  ComboBoxControlNode → comboBox
   ```
   (Spinner confirmed from real `.mlx`; others inferred from naming pattern — verify with real files if problems arise.)

2. **`minimum`/`maximum` instead of `min`/`max`** — renamed by `_normalize_livecontrol()` before the control is parsed.

### Section Splitting in `parse.py`
Hand-crafted golden fixtures use `sectPr` paragraph elements as explicit section breaks. Real MATLAB `.mlx` files instead use **heading paragraphs as logical section dividers**. The parser handles both:
- `sectPr` paragraph → flush and start new section (legacy path)
- `heading` paragraph **after** code in the current section → flush and start new section with the heading as first paragraph
- `heading` paragraph **before** any code → remains in the current section as a label (no split)

---

## Golden Tests

Tests compare translator output to files in `golden/*/expected/`.  
Comparison is **line-by-line with trailing whitespace stripped** (see
`spec/normalization_rules.md`). Metadata like `AppId` and `MATLABRelease`
are fixed to known values in the test fixture so output is deterministic.

Run all tests: `python -m pytest tests/ -v`

---

## Translation Contracts (Implemented)

### Initialization Section
A section with no livecontrol and no plot calls. Simple assignments
(`name = expr;`) become **private properties** with `% Description` comment.

### Button Section (`specs/button_section.md`)
A code section + `button` livecontrol:
- Always uses the layout engine path (1100×760 canvas)
- Creates a `{Label}Button` component (32px tall, full 1060px width) and `{Label}ButtonPushed` callback
- Init-section variables are prefixed `app.` in the callback body
- Callback is diary-wrapped; output goes to `{Label}OutputTextArea`
- Also emits `{Label}CodeTextArea` (static source) and `{Label}OutputTextArea` (dynamic output)

### Dropdown Section (`specs/dropdown_section.md`)
A code section + `comboBox` livecontrol:
- Always uses the layout engine path (1100×760 canvas)
- Creates a `DropDown` component (label PascalCased, spaces removed)
- Bound variable detected by matching code assignment RHS to `defaultValue`
- Bound-var assignment replaced by `app.var = app.DropDown.Value;` in callback (before diary block)
- MATLAB double-quoted strings (`"one"`) converted to char vectors (`'one'`)
  to match the type returned by `DropDown.Value`
- Callback is diary-wrapped; output goes to `{ComponentName}OutputTextArea`
- Also emits `{ComponentName}CodeTextArea` (static source) and `{ComponentName}OutputTextArea` (dynamic output)

### Display Section (`specs/output_capture.md`)
A code section with no livecontrol, no recognized plot call, no labels, and at least one
non-pure-assignment line (i.e., not a button/dropdown/plot/init section):
- Detected by `_is_pure_assignment()`: if any line doesn't match `\w+ = expr;`,
  the section is a display section (not an init section)
- Emits a `CodeTextArea` (black bg, white text) showing static source code and
  an `OutputTextArea` (dark gray bg, green text) populated at runtime via `diary`
- Both TextAreas are 120 px tall, full-width (1060 px) on the 1100×760 canvas
- Named `CodeTextArea`/`OutputTextArea` (single section) or
  `CodeTextArea_N`/`OutputTextArea_N` (multiple display sections)
- `startupFcn` wraps each section's code in `diary`/`fileread`/`strsplit` to
  capture all text output (disp, fprintf, unsilenced expressions)
- Triggers `has_startup = True` → adds `%[app:runConfiguration]` appendix

### Plotting Section (`specs/plotting_section.md`)
A section with no livecontrol that contains a recognized plot function call:
- All code goes into `startupFcn(app)` (variables remain local — no private props)
- Plot calls have `app.UIAxes` injected as first argument: `plot(t,x)` →
  `plot(app.UIAxes, t,x)`
- Adds `%[app:runConfiguration]` appendix section declaring the startup function
- **Fixed path** (single section, no labels): UIAxes at `[15 15 610 440]` on
  a 640×480 canvas
- **Layout engine path** (labels present or multiple sections): UIAxes height
  is 440px (one plot) or 260px (multiple plots); positioned by y_cursor on
  1100×760 canvas
- Multiple plot sections produce `UIAxes_1`, `UIAxes_2`, … components; each
  section's plot calls inject the corresponding axes name

### Generic Control Section (`specs/control_section.md`)
A code section + any non-button, non-comboBox livecontrol (slider, spinner, rangeslider,
checkbox, statebutton, editfield_numeric, editfield_text, colorpicker, datepicker, filebrowser):
- Handled by a single `ControlSection` IR dataclass with a `control_type` discriminator
- Always uses the layout engine path (1100×760 canvas)
- Creates a control widget (32px tall, **except slider: 3px**) and `{ComponentName}ValueChanged` callback
- Bound variable detected by matching code assignment RHS to the JSON `defaultValue`;
  bound-var assignment replaced by `app.{BoundVar} = app.{ComponentName}.Value;` in callback
- Callback is diary-wrapped; output goes to `{ComponentName}OutputTextArea`
- Also emits `{ComponentName}CodeTextArea` and `{ComponentName}OutputTextArea`
- **Labeled types** (`spinner`, `rangeslider`, `editfield_numeric`, `editfield_text`, `datepicker`):
  require a `<Label name='{ComponentName}Label'>` sibling element (right-aligned, 100px wide,
  vertically centered in 32px row) and a `label='{ComponentName}Label'` attribute on the main
  component. Without this, App Designer throws "Index exceeds the number of array elements."
  The control x shifts to 130 and width shrinks by 110px. A `{ComponentName}Label` entry is
  added to the public properties block.
- **Slider/RangeSlider tick gap**: 20px extra gap added below the widget so tick marks
  don't overlap the CodeTextArea.
- **Special cases by type:**
  - `datepicker`: no `defaultValue` → no private prop, no bound var; no `<Value>` in XML
  - `filebrowser`: maps to `EditField` XML tag and `matlab.ui.control.EditField` class; not labeled
  - `slider`: no `<Step>` property in App Designer (only `<Limits>` and `<Value>`); not labeled; height is 3 px (`_SLIDER_NATURAL_HEIGHT`), not 32 px — MATLAB's UISlider track height is fixed; using 32 corrupts tick-label rendering
  - `checkbox`/`statebutton`: `<Text>` property uses PascalCase component name; `<Value>` omitted when false
  - `colorpicker`/`datepicker`: type strings are camelCase in JSON — parsed case-sensitively
  - `rangeslider`: `defaultValue` is a string `"[0 100]"` — emitted as array literal, not quoted

### View Modes (`specs/view_modes.md`)
Three layout strategies controlled by the `view_mode` parameter to `translate()`:

**`output_inline`** (default): All components stacked vertically in one column,
full 1060 px width.

**`output_right`**: Two-column layout splitting the 1060 px usable width:
- Left column (x=20, w=520): Labels, Button, DropDown, control widget, CodeTextArea
- Right column (x=560, w=520): OutputTextArea, UIAxes
- Two independent cursors (`left_cursor`, `right_cursor`) advance per section
- Global cursor after each section: `y_cursor = min(left_cursor, right_cursor) + _ROW_GAP - gap`
- The `.m` classdef is **identical to `output_inline`** — only layout XML positions differ
- Implemented in `_generate_layout_xml_right()` in `codegen.py`
- **TextArea bottom-alignment (button/dropdown):** `OutputTextArea` is bottom-aligned
  to `CodeTextArea`, not top-aligned to the section. `code_bottom` is computed after
  the widget is placed and reused as the `OutputTextArea` bottom y-coordinate.

**`hide_code`**: CodeTextArea components are suppressed; all other components
(Button, DropDown, UIAxes, OutputTextArea) are emitted normally. The classdef
is identical to `output_inline` except `code_text_area_name` is empty string.
- Implemented by passing `view_mode` through to `_assign_text_area_names()` and
  suppressing CodeTextArea emission in `_generate_layout_xml_with_engine()`
- **Plot sections in `hide_code`:** plot sections have no CodeTextArea to suppress,
  so `hide_code` produces layout XML identical to `output_inline` for plot sections.

---

## Hard-Won Decisions

**`<Value>{}</Value>` in a TextArea crashes App Designer.**  
When `_code_lines_xml_value()` receives an empty list (e.g. a spinner section where the
only code line was the bound-var assignment, leaving `code_lines = []`), it must return `''`
not `{}`. App Designer rejects an empty MATLAB cell array as a `Value` property with:
`'Value' must be a character vector, or a N-by-1 array of the following type: cell array of
character vectors, string, or categorical.`
Fix: early return `if not lines: return "''"` at the top of `_code_lines_xml_value()`.

**Omit the private properties block when empty.**  
App Designer does not emit an empty `properties (Access = private)` block. If
`ir.private_props` is empty, skip the block entirely. Emitting it when empty
causes App Designer to behave unexpectedly.

**Appendix section order matters.**  
The `%[app:runConfiguration]` section (when present) goes between
`%[app:layout]` and `%[app:appDetails]`.

**Property ordering in layout XML is alphabetical**, with `<Children>` always last.

**Component name alignment** in the public properties block: all type annotations
are right-padded to align at column `max_name_length + 2`.

**Canvas size must fit the target screen without auto-scaling.**  
MATLAB auto-scales figures that exceed the screen dimensions, triggering
`AutoResizeChildren`, which causes UIAxes positions to drift unpredictably
across runs. The layout engine canvas is **1100×760** (`[100 100 1100 760]`),
which fits on a 1470×956 screen (MacBook Air) with room for OS chrome. Do not
increase canvas height beyond ~800 without testing on target hardware. Attempts
to fix drift via `PositionConstraint` in XML or `startupFcn` all failed — the
root cause was oversized canvas, not the axes constraint mode.

**Labeled components require a `<Label>` sibling or App Designer crashes.**  
Five control types — `Spinner`, `RangeSlider`, `NumericEditField`, `EditField`, `DatePicker` —
are "labeled components" in App Designer. They require both (1) a `<Label name='...Label'>`
sibling element with `<HorizontalAlignment>`, `<Position>`, and `<Text>` children, and (2)
a `label='...'` attribute on the main component pointing to that label. Omitting either causes
App Designer to throw "Index exceeds the number of array elements. Index must not exceed 3."
The label is 100px wide, right-aligned, vertically centered in the 32px row. The main
component x shifts from 20→130, width shrinks by 110px.

**Strings with single quotes in XML must use `char("…")`, not `'…'` escapes or bare `"…"`.**  
Two related crashes affect any XML string property that contains `'`:

1. **`''` escapes crash with labeled components:** `''` inside a TextArea `<Value>` causes
   "Index exceeds the number of array elements. Index must not exceed 3." when any labeled
   component (`Spinner`, `RangeSlider`, `NumericEditField`, `EditField`, `DatePicker`) is present.
2. **Bare `"…"` produces wrong MATLAB type:** A double-quoted string is a MATLAB `string`
   object, not a `char` vector. App Designer throws "'Value' must be a character vector, or a
   N-by-1 array…" for TextArea `<Value>`, and "Dimensions of the position argument must match
   the dimensions of the text argument or be 1" for Label `<Text>` containing apostrophes.

Fix: use `char("text with 'quotes'")` for any XML string property containing single quotes.
- `_code_lines_xml_value()` in `codegen.py`: wraps all lines in `char("…")` when any line contains `'`.
- `_matlab_str_value()` in `codegen.py`: uses `char("…")` for Label `<Text>` and Button `<Text>` when the text contains `'`.

**UISlider height must be 3 px; tick marks extend below its bounding box.**  
MATLAB's horizontal UISlider has a fixed track height in App Designer. Setting `<Position>`
height to 32 triggers "The height of this component cannot be changed" warning, which then
corrupts tick-label rendering ("Dimensions of the position argument must match the dimensions
of the text argument or be 1"). Fix: use `_SLIDER_NATURAL_HEIGHT = 3` for the `<Position>`
height of Slider controls (not `_CONTROL_HEIGHT = 32`).

Additionally, tick marks render below the slider's declared bounding box. With the default
10 px row gap they overlap the CodeTextArea below. Fix: add 20 px extra gap
(`_SLIDER_TICK_EXTRA`) after slider/rangeslider controls in both layout engine paths.

**UISlider crashes App Designer when its `ValueChangedFcn` callback body is empty.**  
A Slider whose callback function has no lines between `function ... (app, event)` and `end`
triggers "Dimensions of the position argument must match the dimensions of the text argument
or be 1" when App Designer opens the file. The crash has nothing to do with slider position,
limits, width, or the presence of other components — it is purely a consequence of the empty
callback body. Fix: codegen always emits `% value changed` as a placeholder when no other
lines would be present (see the `if len(cb_lines) == body_start` guard in `codegen.py`).
This occurs when a slider section's only code was the bound-var assignment (leaving
`code_lines = []`) and there is no `output_text_area_name`.

**Three codegen paths in `generate_layout_xml`:**
- **Fixed path** (`_generate_layout_xml_fixed`): single section with no labels.
  Uses a 640×480 canvas with hard-coded positions. Matches App Designer's own
  exemplars for simple apps.
- **Layout engine path** (`_generate_layout_xml_with_engine`): any app with
  labels or multiple sections in `output_inline` or `hide_code` mode. Uses
  1100×760 canvas with a y_cursor algorithm placing components top-to-bottom
  in MATLAB's bottom-left coordinate system.
- **Output-right path** (`_generate_layout_xml_right`): triggered when
  `view_mode == "output_right"` and the layout engine is needed. Same 1100×760
  canvas and y_cursor, but splits into left (x=20, w=520) and right (x=560,
  w=520) columns with two independent cursors per section.

---

## Appendix Section Names

| Element               | Appendix tag               |
|-----------------------|----------------------------|
| `<Components>`        | `%[app:layout]`            |
| `<RunConfigurations>` | `%[app:runConfiguration]`  |
| `<AppDetails>`        | `%[app:appDetails]`        |
| `<InternalData>`      | `%[app:internalData]`      |
| `<Thumbnail>`         | `%[app:thumbnail]`         |

---

## Directory Layout

```
specs/          Contracts the translator must obey (write before coding)
golden/         Minimal authoritative exemplars; each proves one contract
  <name>/
    input/document.xml      extracted from the .mlx zip
    expected/<name>.m       full .m file with appendix
    expected/<name>.xml     standalone layout XML (for diffability)
src/            Translation logic
  ir.py         IR dataclasses
  parse.py      document.xml → AppIR
  codegen.py    AppIR → .m text + layout XML
  translate.py  entry point (module + CLI)
tests/          Golden tests (one file per exemplar)
spec/           Reference documents (AD format specs, Live Script format)
matlab/         Source .mlx files and their extracted .zip counterparts
prompts/        Agentic prompt fragments (not directly used by translator)
```
