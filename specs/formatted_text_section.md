# Contract: Formatted Text Section

This spec defines how formatted text paragraphs (headings, body text) in a
Live Script section map to App Designer Label components.

---

## Detection

A paragraph is a **formatted text paragraph** when:
- It is a `<w:p>` element
- Its `<w:pPr><w:pStyle w:val="..."/>` matches one of the recognized text styles
- It does NOT have `w:val="code"` (that is a code paragraph)

Recognized text styles (confirmed against `matlab/minimal_axes_with_text/document.xml`):

| XML `w:val` | Semantic type | App Designer mapping |
|---|---|---|
| `heading` | Section title | Label (large, bold) |
| `text` | Body paragraph | Label (normal weight) |
| (no pStyle) | Body paragraph | Label (normal weight) |

Text content is extracted from all `<w:t>` elements within the paragraph's
`<w:r>` runs, concatenated in order.

Empty paragraphs (no text content after concatenation) are skipped.

---

## Output: Label Component

Each non-empty formatted text paragraph produces one `Label` component.

**Component name**: `Label_<N>` where N is a 1-based counter across all
Labels in the app (e.g., `Label_1`, `Label_2`).

**Position**: assigned by the layout engine (see `specs/canvas_layout.md`).
Width spans the full column width for the active view mode.

**Font properties** by style:

| Style | FontSize | FontWeight | Height |
|---|---|---|---|
| `heading` | 18 | `'bold'` | 40 px |
| `text` | 12 | `'normal'` | 22 px |

**Other properties**:
- `Text`: the extracted string, wrapped in single quotes: `'My heading'`
- `WordWrap`: `'on'` for body paragraphs; `'off'` for headings
- No callback properties

Only non-default values are serialized in the layout XML. The Label defaults
in App Designer are FontSize=12, FontWeight='normal', WordWrap='off'.
Therefore:
- `heading` labels always serialize `FontSize` and `FontWeight`
- `text` labels serialize `WordWrap` (FontSize matches default so omitted)
- `Text` is always serialized (it has no meaningful default)

---

## Output: Public Properties

Each Label appears in the `properties (Access = public)` block:

```matlab
Label_1    matlab.ui.control.Label
Label_2    matlab.ui.control.Label
```

Padding follows the same column-alignment rule as other components.

---

## Section Composition

Formatted text paragraphs can appear in any section, before or after code and
livecontrols. Within the layout engine, text rows are placed before control
rows and before the UIAxes row (see `specs/view_modes.md`).

A section may have text-only content (no code, no livecontrol, no plot). In
that case, the section produces only Label components and no callbacks.

---

## Out of Scope

- Bold/italic inline formatting within a paragraph (entire paragraph uses
  the paragraph-level style only)
- Hyperlinks
- Bulleted or numbered lists
- Tables
- Images
- Equations
- Multi-paragraph Labels (each paragraph → one Label)
