# Contract: Canvas and Layout Engine

This spec defines the canvas dimensions and the layout engine that assigns
`[x y w h]` positions to App Designer components generated from Live Script
sections.

---

## Canvas Dimensions

The UIFigure is sized for a 1440×1024 pixel presentation window:

```
<Position>[100 100 1440 1024]</Position>
```

The usable interior (inside a 20 px margin on all sides) is:

- **Origin**: `(20, 20)` (bottom-left, MATLAB coordinate convention)
- **Width**: 1400 px
- **Height**: 984 px

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
y_cursor = margin + usable_height   # top of usable area = 20 + 984 = 1004
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
| UIAxes | 440 px |

These heights may be overridden by explicit layout rules in individual
translation contracts.

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

- Scrolling (all content must fit within the 1440×1024 canvas)
- Responsive layout (fixed pixel positions only)
- GridLayout-based positioning
- Components that exceed canvas bounds (no overflow handling)
