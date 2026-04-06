# Contract: View Modes

This spec defines the three layout strategies corresponding to Live Script's
three view modes. The view mode is passed as a string parameter to the
translator (`view_mode`).

---

## Overview

| Mode | Parameter value | Description |
|---|---|---|
| Output inline | `output_inline` | Text, controls, and plot stacked vertically |
| Output on right | `output_right` | Text+controls in left column, plot in right column |
| Hide code | `hide_code` | Same as output_inline; code-only sections produce no component |

Default: `output_inline`.

---

## Mode: `output_inline`

Within each section, components are stacked vertically in this order:

1. Text rows (heading, body) — in order of appearance
2. Interactive control rows (Button, DropDown, etc.)
3. UIAxes row (if section has a plot)

All rows span the full usable width (1400 px).

The layout engine advances `y_cursor` after each row (row height + 10 px gap).
After all rows in a section, `y_cursor` is decremented by an additional 10 px
section gap (total 20 px between sections).

---

## Mode: `output_right`

The usable width is split into two columns with a 20 px gutter:

| Column | x offset | Width |
|---|---|---|
| Left (text + controls) | 20 | 540 px (≈ 40% of 1400) |
| Right (plot) | 580 | 840 px (≈ 60% of 1400) |

Within each section:
- Text rows and control rows occupy the **left column**, stacked vertically
- The UIAxes occupies the **right column**; its top aligns with the first
  text or control row of the section
- The section height is `max(left_column_height, uiaxes_height)`

`y_cursor` advances by section height + section gap after each section.

---

## Mode: `hide_code`

Identical to `output_inline` with one addition:

- Sections that contain **only code** (no livecontrol, no plot, no formatted
  text) produce **no components**. They are initialization-only sections;
  their code still contributes to the classdef (private props / startupFcn)
  but nothing appears on the canvas.
- Sections with formatted text, controls, or plots are laid out identically
  to `output_inline`.

---

## Shared Rules (all modes)

- Components never overlap. The layout engine is strictly sequential.
- If the total height of all sections exceeds the usable height (984 px),
  components are placed beyond the canvas bottom. This is an authoring error;
  no overflow handling is performed.
- The UIFigure `Position` is always `[100 100 1440 1024]` regardless of mode.

---

## Out of Scope

- Mixed modes within a single app
- Per-section mode overrides
- Automatic height fitting or shrinking to fill canvas
