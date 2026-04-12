# Contract: Plotting Section

This spec defines how a Live Script section containing plotting function calls
(and no livecontrol) maps to a UIAxes component and a startup function.

---

## Detection

A section is a plotting section when:
- It contains no livecontrol element, AND
- Its code text contains a call to a recognized plotting function

Recognized plotting functions: `plot`, `scatter`, `bar`, `barh`, `histogram`,
`imagesc`, `surf`, `mesh`, `contour`, `fplot`, `polarplot`, `loglog`,
`semilogx`, `semilogy`, `stem`, `stairs`, `area`, `fill`, `pie`.

Sections with no livecontrol that do NOT contain a plot call are treated as
initialization sections (see `button_section.md`).

---

## Output: Component

A single `UIAxes` component is added to the app per plotting section:
- **Name**: `UIAxes` (single plot section) or `UIAxes_N` (multiple plot sections)
- **Type**: `matlab.ui.control.UIAxes` in classdef

**Fixed layout path** (single section, no labels — 640×480 canvas):
- Position: `[15 15 610 440]`

**Layout engine path** (labels present or multiple sections — 1100×760 canvas):
- Height: 440px (one total plot section) or 260px (two or more total plot sections)
- Position set by y_cursor algorithm; see `canvas_layout.md`

---

## Output: Startup Function

The plotting section's code becomes the body of `startupFcn(app)`.

- All variables in the plotting section remain **local** to `startupFcn`.
  No private properties are derived from a plotting section.
- Recognized plotting function calls have `app.UIAxes` (or `app.UIAxes_N`)
  injected as the first argument: `plot(t, x)` → `plot(app.UIAxes, t, x)`.
- Blank lines in the original code are stripped.
- Do NOT set `Position` programmatically in `startupFcn` — this was attempted
  and made layout instability worse. The root cause of past drift bugs was
  canvas oversizing (see `canvas_layout.md`), not axes constraint mode.

---

## Output: Private Properties Block

Omit the `properties (Access = private)` block entirely when there are no
private properties. App Designer does not emit this block when empty.

---

## Output: RunConfigurations

A `%[app:runConfiguration]` appendix section is added between `%[app:layout]`
and `%[app:appDetails]`:

```
%---
%[app:runConfiguration]
%{
<?xml version='1.0' encoding='UTF-8'?>
<RunConfiguration>
    <StartupFcn>startupFcn</StartupFcn>
</RunConfiguration>
%}
```

Note: the tag is `<RunConfiguration>` (singular), not `<RunConfigurations>`.

---

## Out of Scope for This Contract

- Plotting sections combined with interactive livecontrols in the same section
- Variables from the plotting section shared with callback code
- Custom axes properties (titles, labels, limits)
