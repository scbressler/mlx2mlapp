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

A single `UIAxes` component is added to the app:
- **Name**: `UIAxes`
- **Type**: `matlab.ui.control.UIAxes` in classdef
- **Default position**: `[15 15 610 440]`
- No callback properties

---

## Output: Startup Function

The plotting section's code becomes the body of `startupFcn(app)`.

- All variables in the plotting section remain **local** to `startupFcn`.
  No private properties are derived from a plotting section.
- Recognized plotting function calls have `app.UIAxes` injected as the first
  argument: `plot(t, x)` → `plot(app.UIAxes, t, x)`.
- Blank lines in the original code are stripped.

---

## Output: Private Properties Block

The private properties block is always emitted, even when empty. Omitting it
causes the MATLAB classdef to fail.

---

## Output: RunConfigurations

A `%[app:runConfiguration]` appendix section is added between `%[app:layout]`
and `%[app:appDetails]`:

```
%---
%[app:runConfiguration]
%{
<?xml version='1.0' encoding='UTF-8'?>
<RunConfigurations>
    <StartupFcn>startupFcn</StartupFcn>
</RunConfigurations>
%}
```

---

## Out of Scope for This Contract

- Multiple plotting sections (only the last one is used)
- Plotting sections combined with interactive livecontrols in the same section
- Variables from the plotting section shared with callback code
- Custom axes properties (titles, labels, limits)
