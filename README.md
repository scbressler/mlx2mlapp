# Live Script → App Designer Translator

This repository contains a prototype workflow for converting a MATLAB Live Script
(saved in plain‑text Live Code format) into a plain‑text App Designer app that can
be opened and edited in MATLAB App Designer.

The goal is not to support every Live Script feature, but to reliably translate
**interactive intent** into a valid, editable App Designer app.

---

## What This Project Is (and Is Not)

This project is:

- A deterministic translator from Live Script structure to App Designer structure
- A testbed for understanding the plain‑text App Designer format
- A foundation for AI‑assisted or agentic app‑generation workflows

This project is not:

- A general Live Script renderer
- A visual layout optimizer
- A replacement for App Designer’s interactive authoring tools

Keeping this boundary explicit is essential for progress.

---

## Repository Structure

```
.
├── specs/          # Contracts the translator must obey (write before coding)
├── spec/           # Reference documents (App Designer format, Live Script format)
├── golden/         # Minimal, authoritative exemplars (input + expected output)
│   └── <name>/
│       ├── input/document.xml
│       └── expected/<name>.m
│           expected/<name>.xml
├── src/            # Translation logic
│   ├── ir.py           IR dataclasses (AppIR, SectionIR, etc.)
│   ├── parse.py        document.xml → AppIR
│   ├── codegen.py      AppIR → .m text + layout XML
│   └── translate.py    entry point (module + CLI)
├── tests/          # Golden tests (one file per exemplar)
├── matlab/         # Source .mlx files and App Designer reference examples
└── README.md
```

Each directory has a single responsibility. If a file feels like it belongs in
more than one place, that’s usually a signal to simplify.

---

## How to Succeed with This Project

### Start from Golden Exemplars

All translation logic should be validated against the contents of `golden/`.

Golden exemplars are intentionally small and boring. Each one exists to prove
a specific semantic contract, such as:

- A button maps cleanly to a callback
- A value‑producing control updates application state
- A plotting section implies a persistent UIAxes

If a change breaks a golden exemplar, treat that as a real regression.

---

### Treat `specs/` as Law, Not Guidance

The files in `specs/` define what “correct” means.

They are:

- Declarative
- Narrow in scope
- Free of examples and heuristics

When the translator’s behavior is unclear, the right question is:
“Which spec applies here?”

If the answer is “none,” update the specs *before* updating the code.

---

### Use an Intermediate Representation (IR)

Do not translate directly from Live Script XML to App Designer XML.

Instead:

1. Parse the Live Script into a structured IR
2. Translate the IR into:
   - layout XML
   - MATLAB class code

This separation dramatically reduces complexity and makes failures explainable.

---

### Prefer Determinism Over Cleverness

This project values:

- Stable output
- Predictable naming
- Small, inspectable diffs

It intentionally avoids:

- Layout inference based on rendered output
- Heuristic “best guess” UI placement
- Rewriting user computation logic

If the translator cannot be sure, it should choose the simplest valid option.

---

### Optimize for App Designer Editability

A successful output is not just runnable — it must be **editable in App Designer**.

That means:

- All callbacks referenced in XML exist in the `.m` file
- UI components have stable, readable names
- Business logic is separated from UI callbacks where possible

If App Designer opens the app cleanly and the user can keep working, the translation succeeded.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Tests compare translator output line-by-line (trailing whitespace stripped) against
files in `golden/*/expected/`. Metadata fields (`AppId`, `MATLABRelease`) are fixed
to known values in the test fixture so output is deterministic.

Currently: **50 tests across 25 golden exemplars**, all passing.

---

## Implemented Contracts

| Contract | Exemplar | What it proves |
|---|---|---|
| Initialization section | — | Simple assignments become private properties |
| Button section | `minimal_button` | `{Label}Button` + diary-wrapped callback + `{Label}CodeTextArea`/`{Label}OutputTextArea` |
| Dropdown section | `minimal_dropdown` | `DropDown` + bound-var wiring + diary-wrapped callback + `{ComponentName}CodeTextArea`/`{ComponentName}OutputTextArea` |
| Plotting section (simple) | `minimal_axes` | `UIAxes` + `startupFcn`, fixed 640×480 layout |
| Plotting section + labels | `minimal_axes_with_text` | Layout engine, 1100×760 canvas |
| Multiple plot sections | `multiple_sections` | `UIAxes_1`/`UIAxes_2`, y_cursor placement |
| Display section (output capture) | `minimal_output` | `CodeTextArea` + `OutputTextArea`, diary-based runtime capture |
| View mode: `hide_code` (display) | `hide_code_output` | CodeTextArea suppressed; only `OutputTextArea` emitted |
| View mode: `hide_code` (button) | `hide_code_button` | CodeTextArea suppressed; Button + `OutputTextArea` emitted |
| View mode: `hide_code` (dropdown) | `hide_code_dropdown` | CodeTextArea suppressed; DropDown + `OutputTextArea` emitted, full width |
| View mode: `output_right` (display) | `output_right_output` | Two-column layout; CodeTextArea left, OutputTextArea right, both 520 px wide |
| View mode: `output_right` (button) | `output_right_button` | Asymmetric columns; Button+CodeTextArea left, OutputTextArea right (bottom-aligned) |
| View mode: `output_right` (dropdown) | `output_right_dropdown` | DropDown+CodeTextArea left, OutputTextArea right (bottom-aligned) |
| View mode: `output_right` (multi-section) | `output_right_multi` | Two sections; global y_cursor advances with `_SECTION_GAP` between sections |
| View mode: `output_right` (plot) | `output_right_plot` | Labels left column, UIAxes right column (440 px, top-aligned to section) |
| View mode: `hide_code` (plot) | `hide_code_plot` | Plot sections have no CodeTextArea; layout identical to `output_inline` |
| Generic control: Slider | `minimal_slider` | `Slider` widget + bound-var wiring + diary callback |
| Generic control: Spinner | `minimal_spinner` | `Spinner` widget + bound-var wiring + diary callback |
| Generic control: Range Slider | `minimal_rangeslider` | `RangeSlider` widget + array-valued bound var |
| Generic control: Checkbox | `minimal_checkbox` | `CheckBox` widget; boolean bound var; Text = PascalCase label |
| Generic control: State Button | `minimal_statebutton` | `StateButton` widget; boolean bound var; Text = PascalCase label |
| Generic control: Edit Field (numeric) | `minimal_editfieldnum` | `NumericEditField` widget + numeric bound var |
| Generic control: Edit Field (text) | `minimal_editfieldtext` | `EditField` widget + string bound var (char vector) |
| Generic control: Color Picker | `minimal_colorpicker` | `ColorPicker` widget + array-valued bound var |
| Generic control: Date Picker | `minimal_datepicker` | `DatePicker` widget; no defaultValue; no private prop |
| Generic control: File Browser | `minimal_filebrowser` | `EditField` widget (no native FileBrowser in App Designer) |

---

## Widget Library

All 12 MATLAB Live Editor interactive controls are implemented.

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

See `spec/live_script_input_assumptions.md` for the full JSON field inventory
for each control type.

---

## Expected Workflow

A typical iteration looks like this:

1. Write the spec (`specs/`) — define correctness before coding
2. Create the golden exemplar (`golden/<name>/input/` and `expected/`)
3. Write the failing test (`tests/test_<name>.py`)
4. Extend IR, parse, codegen until the test passes
5. Open the result in App Designer and verify it renders correctly

Skipping steps usually leads to brittle behavior later.

---

## A Note on Scope

This repository intentionally ignores many Live Script and App Designer features.
That is not a limitation — it is a strategy.

New features should only be added when they introduce a **new semantic requirement**,
not just a new widget.

---

## Final Guiding Principle

If you ever feel tempted to ask:
“Should the translator be smarter here?”

First ask:
“Can I make the contract clearer instead?”

Clarity beats cleverness every time.