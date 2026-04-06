# CLAUDE.md — Project Guide for AI Assistants

This file captures the working conventions, architecture decisions, and
translation contracts established during development. Read this before
touching any code.

---

## What This Project Does

Translates MATLAB Live Script files (`.mlx`) into App Designer plain-text apps
(`.m` with embedded XML appendix). The output must open and be editable in
App Designer — not just runnable.

Input: `document.xml` extracted from a `.mlx` zip archive  
Output: a single `.m` file containing the classdef + XML appendix

---

## Architecture: Three-Stage Pipeline

```
document.xml  →  [parse]  →  AppIR  →  [codegen]  →  .m + layout XML
```

- **`src/parse.py`** — reads Live Script XML, builds `AppIR`
- **`src/ir.py`** — dataclasses: `AppIR`, `ButtonSection`, `DropDownSection`
- **`src/codegen.py`** — generates layout XML and the full `.m` classdef
- **`src/translate.py`** — entry point wiring parse → codegen

Do not translate directly from Live Script XML to App Designer XML. The IR
is load-bearing: it makes failures explainable and tests meaningful.

---

## How to Add a New Feature

1. Write the spec first (`specs/`) — define what "correct" means before coding
2. Create the golden exemplar (`golden/<name>/input/` and `expected/`)
3. Write the failing test (`tests/test_<name>.py`)
4. Extend IR, parse, codegen until the test passes
5. The spec and golden are the authority — if they conflict with code, fix code

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
- Creates a `{Label}Button` component and `{Label}ButtonPushed` callback
- Init-section variables are prefixed `app.` in the callback body

### Dropdown Section (`specs/dropdown_section.md`)
A code section + `comboBox` livecontrol:
- Creates a `DropDown` component (label PascalCased, spaces removed)
- Bound variable detected by matching code assignment RHS to `defaultValue`
- Bound-var assignment replaced by `app.var = app.DropDown.Value;` in callback
- MATLAB double-quoted strings (`"one"`) converted to char vectors (`'one'`)
  to match the type returned by `DropDown.Value`

### Plotting Section (`specs/plotting_section.md`)
A section with no livecontrol that contains a recognized plot function call:
- Creates a `UIAxes` component at default position `[15 15 610 440]`
- All code goes into `startupFcn(app)` (variables remain local — no private props)
- Plot calls have `app.UIAxes` injected as first argument: `plot(t,x)` →
  `plot(app.UIAxes, t,x)`
- Adds `%[app:runConfiguration]` appendix section declaring the startup function

---

## Hard-Won Decisions

**Keep the empty private properties block.**  
Even when there are no private properties, the block must be emitted:
```matlab
properties (Access = private)
end
```
Removing it causes the MATLAB classdef to fail at runtime.

**Appendix section order matters.**  
The `%[app:runConfiguration]` section (when present) goes between
`%[app:layout]` and `%[app:appDetails]`.

**Property ordering in layout XML is alphabetical**, with `<Children>` always last.

**Component name alignment** in the public properties block: all type annotations
are right-padded to align at column `max_name_length + 2`.

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
