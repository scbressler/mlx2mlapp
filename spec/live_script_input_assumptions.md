# Live Script Input Assumptions

This document defines the assumptions the translator makes about Live Script
inputs. These assumptions constrain scope and enable deterministic translation.

They are **intentional limitations**, not statements about all Live Script
capabilities.

---

## Input Artifact

- The translator consumes `document.xml` extracted from a `.mlx` file.
- The `.mlx` container itself is not processed.
- Only structural and semantic information in `document.xml` is considered.

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
- Supported control types (initial scope):
  - Button
  - Slider
  - Dropdown (ComboBox)

