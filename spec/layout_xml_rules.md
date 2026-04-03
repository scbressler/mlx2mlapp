# Layout XML Rules

This document defines the structural and semantic rules that layout XML
must satisfy to be considered a valid App Designer plain‑text app layout.

These rules describe **what must always be true**, not layout heuristics.

---

## Root and Structure

- Layout XML MUST contain a `<Components>` root element.
- `<Components>` MUST contain exactly one `<UIFigure>` element.
- `<UIFigure>` is the root container for all UI components.

---

## Component Representation

- Each UI component is represented as an XML element whose name matches
  the MATLAB UI class name (e.g., `<Button>`, `<UIAxes>`, `<Slider>`).
- Every component element MUST have a `name` attribute.
  - The `name` attribute defines the component’s code name.
  - Component names MUST be unique within the app.

---

## Properties

- Component properties are expressed as child elements.
- Property element names MUST match App Designer property names exactly.
- Properties MAY be omitted if they are default values.
- Property order is not semantically meaningful, except for `<Children>`.

---

## Children and Containment

- Container components (including `UIFigure`) MAY contain a `<Children>` element.
- `<Children>` MUST be the final child element of its parent.
- Child components MUST be listed directly within `<Children>`.
- Child order reflects creation order and is preserved.

---

## Callbacks

- Callback properties (e.g., `ButtonPushedFcn`, `ValueChangedFcn`) MUST
  contain only a method name.
- Callback properties MUST NOT contain executable code.

---

## Unsupported Content

- Runtime state, rendered output, thumbnails, and internal metadata
  MUST NOT appear in layout XML.