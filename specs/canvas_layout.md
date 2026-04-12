# Contract: Canvas and Layout Engine

This spec defines the canvas dimensions and the layout engine that assigns
`[x y w h]` positions to App Designer components generated from Live Script
sections.

---

## Canvas Dimensions

The UIFigure is sized to fit within a 1470×956 screen (MacBook Air) with room
for OS chrome:

```
<Position>[100 100 1100 760]</Position>
```

**Important:** MATLAB auto-scales figures that exceed screen dimensions,
triggering `AutoResizeChildren` which causes UIAxes positions to drift
unpredictably across runs. Keep canvas height ≤ ~800 px. Do not increase
without testing on target hardware.

The usable interior (inside a 20 px margin on all sides) is:

- **Origin**: `(20, 20)` (bottom-left, MATLAB coordinate convention)
- **Width**: 1060 px
- **Height**: 720 px

All component positions are computed within this usable area.

---

## Section Layout Model

A Live Script is a sequence of **sections**. Each section contributes one or
more component **rows** stacked vertically. The layout engine iterates through
sections top-to-bottom (in Live Script reading order), which in MATLAB
coordinates means bottom-to-top (y decreases as we go down the page).

**Working cursor**: the layout engine maintains a `y_cursor` that starts at the
top of the usable area and moves downward (decreasing) as components are placed.

```
y_cursor = margin + usable_height   # top of usable area = 20 + 720 = 740
```

Each component row is placed at `y_cursor - row_height`, then `y_cursor` is
decremented by `row_height + row_gap`.

**Row gap**: 10 px between component rows within a section.
**Section gap**: 20 px between sections.

---

## Component Row Heights (defaults)

| Component type | Default height |
|---|---|
| Label (heading1) | 40 px |
| Label (heading2) | 30 px |
| Label (body) | 22 px |
| Button | 32 px |
| DropDown | 32 px |
| UIAxes | 440 px (single), 260 px (multiple) |
| CodeTextArea | 120 px |
| OutputTextArea | 120 px |

These heights may be overridden by explicit layout rules in individual
translation contracts.

---

## Layout Engine Trigger

The layout engine path (1100×760 canvas, y_cursor algorithm) is used when **any**
of the following is true:

- More than one section
- Any section has labels (heading or text paragraphs)
- Any section has display code lines (`code_lines`)
- Any section has button livecontrols (`button_sections`)
- Any section has dropdown livecontrols (`dropdown_sections`)

The **fixed path** (640×480 canvas, hard-coded positions) is used only for a
single section with no labels and no livecontrols — i.e., a plain plot-only
or axes-only section.

---

## View Modes

The layout engine operates in one of three **view modes**, passed as a
parameter to the translator. The view mode controls how components within a
section are horizontally and vertically arranged.

See `specs/view_modes.md` for full definitions.

Default view mode: `output_inline`.

---

## Coordinate Convention

App Designer uses MATLAB figure coordinates:
- Origin `(0, 0)` is at the **bottom-left** of the UIFigure
- x increases rightward, y increases upward
- `Position` format: `[left bottom width height]`

The layout engine reads sections in top-to-bottom order, but assigns
bottom values by computing `bottom = y_cursor - height`.

---

## Out of Scope

- Scrolling (all content must fit within the 1100×760 canvas)
- Responsive layout (fixed pixel positions only)
- GridLayout-based positioning
- Components that exceed canvas bounds (no overflow handling)
