# Contract: View Modes

This spec defines the three layout strategies corresponding to Live Script's
three view modes. The view mode is passed as a string parameter to the
translator (`view_mode`).

---

## Overview

| Mode | Parameter value | Description |
|---|---|---|
| Output inline | `output_inline` | Text, controls, plot, and output stacked vertically |
| Output on right | `output_right` | Text+controls in left column, plot in right column |
| Hide code | `hide_code` | Same as output_inline; code-only sections produce no component |

Default: `output_inline`.

---

## Mode: `output_inline`

Within each section, components are stacked vertically in this order:

1. Text rows (heading, body) — in order of appearance
2. Interactive control rows (Button, DropDown, etc.)
3. UIAxes row (if section has a plot)
4. TextArea row (output capture — always present for code sections)

All rows span the full usable width (1060px on the 1100×760 canvas).

The layout engine advances `y_cursor` after each row (row height + `_ROW_GAP`).
After the last row in a section (TextArea), `y_cursor` is decremented by
`_SECTION_GAP` (20px) to create space before the next section.

See `output_capture.md` for TextArea component details.
See `canvas_layout.md` for canvas dimensions and y_cursor algorithm.

---

## Mode: `output_right`

In `output_right` mode the usable 1060 px width is split into two equal columns
with a 20 px gutter:

| Column | x  | width |
|--------|----|-------|
| Left   | 20 | 520   |
| Right  | 560| 520   |

### Column assignment

| Component | Column |
|-----------|--------|
| Label (heading / text) | Left |
| Button widget | Left |
| DropDown widget | Left |
| CodeTextArea | Left |
| OutputTextArea | Right |
| UIAxes | Right |

### Layout algorithm

Within each section two independent cursors (`left_cursor`, `right_cursor`)
both start at the global `y_cursor`. Components are placed top-to-bottom in
their respective column, advancing that column's cursor by
`component_height + _ROW_GAP` after each placement.

After all components in the section:

```
section_bottom = min(left_cursor, right_cursor)
gap = _ROW_GAP if last_section else _SECTION_GAP
y_cursor = section_bottom + _ROW_GAP - gap
```

(Adding `_ROW_GAP` back removes the trailing intra-column gap before applying
the inter-section gap.)

### Classdef behavior

The `.m` classdef (public props, private props, callbacks, startupFcn) is
**identical to `output_inline`**. The view mode only affects component positions
in the layout XML, not the generated MATLAB code.

### TextArea vertical alignment (button/dropdown sections)

For button and dropdown sections, the `OutputTextArea` (right column) is
**bottom-aligned to the `CodeTextArea`** (left column), not top-aligned to
the section start. This ensures the two text areas share the same vertical
position even though the left column is taller (Button/DropDown sits above
the CodeTextArea).

Concretely:
```
code_bottom = left_cursor_after_widget - _CODE_TEXT_AREA_HEIGHT
OutputTextArea.Position[2] = code_bottom   # same bottom as CodeTextArea
```

For **display sections** (CodeTextArea + OutputTextArea only, no widget above),
both TextAreas start at `y_cursor` and their bottoms are identical by default.

### Example: display section in `output_right`

Input: `a = 1; fprintf(...)` (same as minimal_output)

```
y_cursor = 740

Left column:
  CodeTextArea   bottom = 740 - 120 = 620  →  [20  620 520 120]

Right column:
  OutputTextArea bottom = 740 - 120 = 620  →  [560 620 520 120]
```

### Example: button section in `output_right`

Input: init section (`counter = 0;`) + button section with "Run" label

```
y_cursor = 740

Left column:
  RunButton        bottom = 740 - 32  = 708  →  [20  708 520  32]
  RunCodeTextArea  bottom = 698 - 120 = 578  →  [20  578 520 120]

Right column:
  RunOutputTextArea bottom = code_bottom = 578  →  [560 578 520 120]
```

---

## Mode: `hide_code`

In `hide_code` mode the source code is hidden but outputs remain visible.
The rule is: **CodeTextArea components are suppressed; all other components
(Button, DropDown, UIAxes, OutputTextArea) are emitted normally.**

### Effect per section type

| Section type | CodeTextArea | OutputTextArea | Widget (Button/DropDown) | UIAxes |
|---|---|---|---|---|
| Display | suppressed | emitted | — | — |
| Button | suppressed | emitted | emitted | — |
| Dropdown | suppressed | emitted | emitted | — |
| Plot | — | — | — | emitted |
| Initialization | — | — | — | — |

### Classdef behavior

- `code_text_area_name` is cleared (empty string) for all section types.
- `output_text_area_name` is set as normal.
- The classdef (`startupFcn`, callbacks, private props) is identical to
  `output_inline` — all code still runs and all `OutputTextArea.Value`
  assignments are preserved.
- `CodeTextArea` components are absent from the public properties block.

### Layout

- The layout engine path (1100×760 canvas, y_cursor) is used when triggered
  by the same conditions as `output_inline`.
- The `y_cursor` advances only for components that are actually emitted.
  Suppressed CodeTextArea rows contribute no height.

### Example: display section in `hide_code`

Input: `a = 1; fprintf(...)`

Layout XML: only `OutputTextArea` at `[20 620 1060 120]`

classdef: `startupFcn` diary-wraps the code and sets `app.OutputTextArea.Value`
(unchanged from `output_inline`, just no `CodeTextArea` public property or
XML element).

### Plot sections in `hide_code`

Plot sections never emit a `CodeTextArea`, so `hide_code` has no effect on
their layout. The output XML for a plot section in `hide_code` is **identical**
to `output_inline`. Labels and UIAxes appear at full 1060 px width exactly as
in `output_inline`.

---

## Shared Rules (all modes)

- Components never overlap. The layout engine is strictly sequential.
- The UIFigure `Position` for the layout engine path is always `[100 100 1100 760]`.
  This canvas fits on a 1470×956 screen (MacBook Air) without auto-scaling.
  Do not use a canvas taller than ~800px or MATLAB will auto-scale the figure,
  causing UIAxes positions to drift unpredictably.
- If the total height of all sections exceeds the usable height (720px),
  components are placed beyond the canvas bottom. This is an authoring error;
  no overflow handling is performed.

---

## Out of Scope

- Mixed modes within a single app
- Per-section mode overrides
- Automatic height fitting or shrinking to fill canvas
