# Live Script Input Assumptions

This document defines the assumptions the translator makes about Live Script
inputs. These assumptions constrain scope and enable deterministic translation.

They are **intentional limitations**, not statements about all Live Script
capabilities.

---

## Input Artifact

The translator accepts three input formats, auto-detected by file extension:

| Extension | Format | Notes |
|-----------|--------|-------|
| `.m` | Plain-text Live Script (R2025a+) | Parsed by `parse_plaintext.py` |
| `.mlx` | Binary Live Script (ZIP archive) | `document.xml` extracted to temp file; parsed by `parse.py` |
| `.xml` | Raw `document.xml` | Legacy/test path; parsed by `parse.py` directly |

All three formats produce the same `AppIR`; codegen is format-agnostic.

---

## Authoring Expectations

Live Scripts used as inputs are expected to be authored with:

- Inline view (text, code, and controls interleaved)
- Code visible (not hidden)
- Section-based execution semantics
- Minimal or no rendered outputs

These expectations are used to simplify association between controls and code.

---

## Code Representation

- Executable MATLAB code appears in CDATA blocks.
- Code is treated as the authoritative source of computation and intent.
- Calls to `figure`, `axes`, and plotting functions are interpreted
  semantically, not literally.
  - For example, `axes` implies a persistent plotting target, not a new figure.

Rendered outputs are ignored.

---

## Live Controls

- Live controls are detected via embedded `customXml` blocks.
- Control metadata (type, label, items, default value, execution model)
  is treated as authoritative.
- The `context` attribute of each `customXml` block contains a JSON object
  with `"type"` and `"data"` fields. The `"type"` string determines which
  control parser is invoked.
- **Real MATLAB `.mlx` files** omit the `"type"` field; type is inferred from
  the `className` XML attribute (e.g. `SpinnerControlNode → "spinner"`). This
  normalization is applied by `_normalize_livecontrol()` in `parse.py`.
- **Real MATLAB `.mlx` files** use `minimum`/`maximum` instead of `min`/`max`
  in control data; `_normalize_livecontrol()` renames these before parsing.

### Confirmed control types (with known `context` JSON structure)

Field names below are from the plain-text `.m` appendix format. In `document.xml`
the same fields appear inside a `"data"` key and `executionModel` replaces `run`.

| Control | `"type"` string | Key `"data"` fields |
|---------|----------------|---------------------|
| Button | `button` | `text`, `value`, `executionModel` |
| Drop Down | `comboBox` | `text`, `value`, `executionModel`, `items`, `itemLabels`, `linkedVariable`, `defaultValue` |
| Range Slider | `rangeslider` | `defaultValue` (e.g. `"[0 100]"`), `min`, `max`, `step`, `label`, `run`, `runOn` |
| Checkbox | `checkbox` | `defaultValue` (boolean), `label`, `run` |
| Color Picker | `colorPicker` | `defaultValue` (e.g. `"[1 1 1]"` RGB 0–1), `colorFormat`, `label`, `run` |
| Date Picker | `datePicker` | `displayFormat`, `label`, `run` (no `defaultValue` field) |
| Edit Field (numeric) | `editfield` | `defaultValue` (number), `label`, `run`, `valueType: "Double"` |
| Edit Field (text) | `editfield` | `defaultValue` (string), `label`, `run`, `valueType: "String"` |
| File Browser | `filebrowser` | `defaultValue`, `browserType` (e.g. `"File"`), `label`, `run` |

**Note:** Both edit field variants share `type: "editfield"`, differentiated by `valueType`.
**Note:** File Browser is its own first-class control type — not an EditField+Button composite.

| Spinner | `spinner` | `defaultValue` (number), `min`, `max`, `step`, `label`, `run`, `runOn` |
| State Button | `statebutton` | `defaultValue` (boolean), `label`, `run` |
| Slider | `slider` | `defaultValue` (number), `min`, `max`, `step`, `label`, `run`, `runOn` |

**Note:** Slider, Spinner, and Range Slider share identical JSON shape (`defaultValue`, `min`, `max`, `step`, `label`, `run`, `runOn`).
State Button and Checkbox share identical JSON shape (boolean `defaultValue`, `label`, `run`).

All 12 Live Editor controls are implemented. Spinner confirmed from a real `.mlx` file; other `_CLASSNAME_TO_TYPE` mappings are inferred from naming convention — verify with real `.mlx` files if problems arise.

### Acquisition strategy for new widget types

To discover the `context` JSON for an unknown control without zip extraction:
1. Create a minimal Live Script containing the target control
2. Save As → **MATLAB Live Code File (UTF-8) (*.m)** (plain-text, R2025a+)
3. Read the `%[control:controltype:controlid]` data block in the file's appendix
4. The JSON there contains all field names needed to write the parser

---

## Plain-Text Live Script (`.m`) Format

Structural markup used by the parser (`parse_plaintext.py`):

| Marker | Meaning |
|--------|---------|
| `%[text] ## Heading` | Start new section; text after `## ` is the label |
| `%[text]` (blank) | Section boundary with no label |
| `code  %[control:type:uuid]{...}` | Inline control — bound to the code on the same line |
| `  %[control:type:uuid]{...}` | Standalone control line (e.g. button, unlabeled spinner) |
| `code  %[output:uuid]` | Output annotation — stripped; ignored by translator |
| `%[appendix]{...}` | Divides file; everything after is appendix |
| `%[control:type:uuid]` | Appendix control header (standalone line) |
| `%   data: {json}` | Appendix control data line (follows header, skipping blanks/`%---`) |
| `%---` | Appendix section separator |

**Button normalization:** the appendix JSON for buttons uses `"label"` not `"text"` as the display name key. `parse_plaintext.py` copies `data['label']` to `data['text']` so downstream code (`_parse_control_section`, codegen) works unchanged.

