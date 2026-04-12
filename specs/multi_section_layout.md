# Contract: Multi-Section Layout

This spec defines how a Live Script with multiple sections maps to an
App Designer app when using the layout engine (1440×1024 canvas).

---

## Detection

A Live Script document contains multiple sections when its `<w:body>` contains
one or more `<w:p><w:pPr><w:sectPr/></w:pPr></w:p>` separator paragraphs.
Each separator ends the current section and begins a new one.

Sections that contain only simple assignments (no plot calls, no livecontrols,
no formatted text) are **init sections** and contribute only to
`private_props`. They do not produce UI components and are not represented
as `SectionIR` objects.

All other sections become `SectionIR` objects in `AppIR.sections`.

---

## IR: SectionIR

```python
@dataclass
class SectionIR:
    labels: list           # list of LabelIR (heading/text for this section)
    plot_lines: list       # code lines for this section (all code, incl. setup)
                           #   non-empty only when section has a plot call
    button_sections: list  # list of ButtonSection in this section
    dropdown_sections: list  # list of DropDownSection in this section
    axes_name: str         # assigned by codegen: "UIAxes" or "UIAxes_N"
```

`AppIR.sections` replaces the former flat `labels`, `startup_lines`,
`button_sections`, and `dropdown_sections` fields.

---

## UIAxes Naming

- Count the number of sections with non-empty `plot_lines` (call this N).
- If N == 1: the single UIAxes is named `"UIAxes"` (preserves backward compat).
- If N > 1: UIAxes are named `"UIAxes_1"`, `"UIAxes_2"`, ... in section order.

The `axes_name` field on `SectionIR` is set by the codegen layer (not the
parser), since naming depends on global count.

---

## UIAxes Height

- If N == 1 (single plot): `_UIAXES_HEIGHT = 440`
- If N > 1 (multiple plots): `_UIAXES_HEIGHT_MULTI = 300`

This ensures multiple sections fit within the 1440×1024 canvas for typical
Live Scripts (2–3 sections). Canvas overflow (more sections than fit) is out
of scope for this spec.

---

## Layout Engine: Section Ordering

The layout engine places components top-to-bottom using `y_cursor`, iterating
`AppIR.sections` in order.

Within each section, row order is:
1. Labels (heading then text, in document order)
2. UIAxes (if section has plot_lines)
3. Button/DropDown components (if any)

Gaps:
- Between rows within a section: `_ROW_GAP = 10`
- After the last component of a section (before next section's first row):
  `_SECTION_GAP = 20` (replaces the final `_ROW_GAP` of the section)

---

## Component Naming (global counters)

- Labels: `Label_1`, `Label_2`, ... across all sections in order
- UIAxes: `UIAxes` (N=1) or `UIAxes_1`, `UIAxes_2`, ... (N>1)

---

## Public Properties Block

Component names appear in this order:
`UIFigure`, then for each section in order: its Label_N names, then its
UIAxes_N name (if present), then its Button/DropDown names.

---

## startupFcn

All `plot_lines` from all plot sections are concatenated in section order
into a single `startupFcn`. Each section's plot calls have the correct
`app.UIAxes_N` (or `app.UIAxes`) injected as the first argument.

Each section's block begins with a Position reset line:
`app.UIAxes_N.Position = [x y w h];` using the same coordinates as the layout
XML. This prevents MATLAB's axes auto-layout engine from drifting the UIAxes
position across repeated runs.

---

## Layout Engine Activation

The layout engine path is used when:
- Any section has non-empty `labels`, OR
- `len(AppIR.sections) > 1`

Otherwise (single section, no labels) the fixed-position path is used for
backward compatibility.

---

## Example: multiple_sections

Input: two sections, each with heading + text + plot.

Layout positions (_UIAXES_HEIGHT_MULTI = 300, _SECTION_GAP = 20):

| Component | Position            | Notes                   |
|-----------|---------------------|-------------------------|
| Label_1   | [20 964 1400 40]    | heading, section 1      |
| Label_2   | [20 932 1400 22]    | text, section 1         |
| UIAxes_1  | [20 622 1400 300]   | plot, section 1         |
| Label_3   | [20 562 1400 40]    | heading, section 2      |
| Label_4   | [20 530 1400 22]    | text, section 2         |
| UIAxes_2  | [20 220 1400 300]   | plot, section 2         |

y_cursor trace:
- Start: 1004
- Label_1 (h=40): bottom=964, gap→ y=954
- Label_2 (h=22): bottom=932, gap→ y=922
- UIAxes_1 (h=300): bottom=622, section_gap→ y=602
- Label_3 (h=40): bottom=562, gap→ y=552
- Label_4 (h=22): bottom=530, gap→ y=520
- UIAxes_2 (h=300): bottom=220

---

## Out of Scope

- Canvas overflow (more than ~3 sections)
- Sections with both plot and button/dropdown in the same section
- Section-level gap customization
