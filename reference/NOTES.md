# Reverse-Engineering Notes: LiveScript → App Designer Format Conversion

_Last updated: 2026-04-01 (rev 2)_

---

## 1. LiveScript (.mlx) File Format

`.mlx` files are ZIP archives (ECMA-376 Open Packaging Conventions).

### ZIP contents

| Path | Description |
|---|---|
| `matlab/document.xml` | Section structure and code (OOXML/WordprocessingML) |
| `matlab/output.xml` | Cached output from last run (can be ignored) |
| `metadata/coreProperties.xml` | OPC standard properties |
| `metadata/mwcoreProperties.xml` | MathWorks content type, MATLAB release |
| `metadata/mwcorePropertiesExtension.xml` | UUID |
| `metadata/mwcorePropertiesReleaseInfo.xml` | MATLAB version info |

### document.xml schema

Uses WordprocessingML namespace (`xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"`)
with MathWorks extensions.

**Paragraph styles** (`<w:pStyle w:val="..."/>`):

| Style value | Meaning |
|---|---|
| `heading` | Section title text |
| `text` | Narrative prose paragraph |
| `code` | MATLAB code block (content in `<![CDATA[...]]>`) |

**Section boundary**: A paragraph containing `<w:sectPr/>` in its `<w:pPr>` marks the end of a
independently-runnable section. Sections map roughly to "Run Section" blocks in the Live Editor.

**Interactive controls**: Embedded in code paragraphs as `<mc:AlternateContent>` blocks
(namespace `http://schemas.openxmlformats.org/markup-compatibility/2006`).

```xml
<mc:AlternateContent>
  <mc:Choice Requires="R2018a">
    <w:customXml w:element="livecontrol">
      <w:customXmlPr>
        <w:attr w:name="context" w:val="{JSON}"/>
        <w:attr w:name="startOffsetLine" w:val="0"/>
        <w:attr w:name="startColumn"     w:val="7"/>
        <w:attr w:name="endColumn"       w:val="9"/>
      </w:customXmlPr>
    </w:customXml>
  </mc:Choice>
  <mc:Fallback/>
</mc:AlternateContent>
```

The `context` attribute is a JSON string with this shape:

```json
{
  "type": "slider" | "comboBox" | "editField",
  "data": {
    "text":         "Display label",
    "value":        <current value>,
    "defaultValue": <default>,
    "minimum":      1,       // slider only
    "maximum":      500,     // slider only
    "step":         10,      // slider only
    "items":        [{"label": "...", "value": "\"...\""}, ...],  // comboBox only
    "itemLabels":   ["...", "..."],  // comboBox only
    "executionModel": "AllSections" | "Section"
  }
}
```

`startOffsetLine` / `startColumn` / `endColumn` give the 0-based line and column of the
**literal value** in the code block.  This locates the assignment whose LHS is the controlled
variable (e.g. `freq = 100;` → line 0, cols 7–9 → variable `freq`).

**comboBox value quirk**: Item values are MATLAB string literals with embedded double-quotes,
e.g. `"\"Time Domain\""`.  Strip the outer double-quotes to get the bare string `"Time Domain"`.

---

## 2. App Designer (.mlapp) File Format

`.mlapp` files are also OPC ZIP archives.

### ZIP contents

| Path | Description |
|---|---|
| `matlab/document.xml` | Full App Designer classdef wrapped in OOXML |
| `appdesigner/appModel.mat` | MATLAB binary UI model (**see Section 3**) |
| `metadata/appMetadata.xml` | App UUID, MLAPPVersion, minimumSupportedMATLABRelease |
| `metadata/coreProperties.xml` | OPC standard properties (title, timestamps) |
| `metadata/mwcoreProperties.xml` | Content type, MATLAB release |
| `metadata/mwcorePropertiesExtension.xml` | Second UUID |
| `metadata/mwcorePropertiesReleaseInfo.xml` | MATLAB version string |
| `[Content_Types].xml` | MIME type declarations for each part |
| `_rels/.rels` | OPC relationship declarations |
| `metadata/appScreenshot.png` | Auto-generated thumbnail (written by App Designer on save; not required for compilation) |

### document.xml schema

Identical namespace to LiveScript but the entire classdef is a **single paragraph**:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<w:document xmlns:w="...">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="code"/></w:pPr>
      <w:r><w:t><![CDATA[ classdef MyApp < matlab.apps.AppBase
  ...
]]></w:t></w:r>
    </w:p>
  </w:body>
</w:document>
```

The standalone attribute is `no` (differs from LiveScript which uses `yes`).

### Required metadata field values

**appMetadata.xml**
- `MLAPPVersion`: `2`
- `minimumSupportedMATLABRelease`: `R2018a`
- `AppType`: `Standard`
- `screenshotMode`: `auto`
- `uuid`: any valid UUID v4

**[Content_Types].xml** Override for document.xml must specify:
```
ContentType="application/vnd.mathworks.matlab.code.document+xml;plaincode=true"
```

**_rels/.rels** Must include relationships for all parts including:
- `appdesigner/appModel.mat` with type `http://schemas.mathworks.com/appDesigner/app/2014/relationships/appModel`

---

## 3. appModel.mat — The Critical Complication

This is the most important finding for the mlx2mlapp project.

### What it is

A MATLAB Level-5 `.mat` binary file with two top-level variables:

| Variable | Type | Description |
|---|---|---|
| `code` | MATLAB struct | Text fields describing class name and callback code |
| `components` | MATLAB struct | MCOS binary blob encoding the visual component tree |

### code struct fields

| Field | Type | Description |
|---|---|---|
| `ClassName` | string | MATLAB class name (e.g. `'SimpleMLApp'`) |
| `EditableSectionCode` | char array | Private properties block and any user-editable sections |
| `Callbacks` | struct (`Name`, `Code`) | Callback method name and code lines |
| `StartupCallback` | struct (`Name`, `Code`) | Startup function name and code lines |
| `AppTypeData` | struct | Empty struct (purpose unknown) |

**Schema varies by template type**: A fully-built app (e.g. SimpleMLApp) has all five fields.
A freshly-saved blank App Designer app only has `['ClassName', 'AppTypeData']` — the callback
fields are absent because no callbacks have been defined yet.

### components struct fields

| Field | Type | Description |
|---|---|---|
| `UIFigure` | MATLAB MCOS object | Serialised component tree rooted at `matlab.ui.Figure` |
| `Groups` | struct (`Id`, `ParentGroupId`) | Component hierarchy (parent-child relationships) |

The `UIFigure` value uses MATLAB's **MCOS (MATLAB Class Object Serialization)** binary format —
identifiable by the `b'MCOS'` magic bytes.  This encodes the entire visual layout including all
child components (UIAxes, DropDowns, Buttons, Sliders, labels, positions, properties).

A **blank App Designer app** has `components._fieldnames = ['UIFigure']` only — no `Groups`
field, and the UIFigure MCOS blob contains only the root figure with no child components.

**MCOS objects cannot be constructed or reliably modified from Python without MATLAB.**

### How App Designer uses appModel.mat

When App Designer opens an `.mlapp` file:
1. Reads `components.UIFigure` → renders the **Design View** canvas
2. Reads `code.*` fields → populates **Code View**
3. If `code.*` and `components` are out of sync, **`components` wins** — the classdef in
   `document.xml` is regenerated from the component model, overwriting whatever was there

**Consequence for mlx2mlapp**: If we use a foreign `appModel.mat` (e.g. from SimpleMLApp), App
Designer will display SimpleMLApp's interface and regenerate SimpleMLApp's classdef, discarding
the converter output.

### mat file binary format — miCOMPRESSED elements

appModel.mat uses **zlib-compressed data elements** (`miCOMPRESSED`, data type tag = 15) in
the MATLAB Level-5 mat format.  The file header is 128 bytes; each subsequent data element
has an 8-byte header `[dtype:uint32 | nbytes:uint32]` followed by the (compressed) data and
padding to the next 8-byte boundary.

Verified structure of the blank template (3905 bytes):
```
offset   0–127   : 128-byte Level-5 header
offset 128–255   : miCOMPRESSED element (nbytes=118, decompresses to 240 bytes)
                   → contains: components, UIFigure, MCOS, matlab.ui.Figure
offset 256–...   : second miCOMPRESSED element → contains: code struct
```

### Why scipy.io.savemat cannot be used to patch appModel.mat

`scipy.io.loadmat` correctly **reads** MCOS data (exposing `code.*` fields as Python strings).
However, `scipy.io.savemat` cannot reconstruct the file faithfully:

- It writes all data elements **uncompressed** (no `miCOMPRESSED` wrapping)
- It **silently drops** MCOS object data — the UIFigure blob is lost entirely
- The output file shrinks dramatically (e.g. 3905 → 1176 bytes for the blank template;
  24083 → 10056 bytes for SimpleMLApp)
- MATLAB App Designer errors on open: _"Unrecognized file name 'UIFigure'"_ because
  the UIFigure field is no longer a valid MCOS object

**Attempted and abandoned**: loading, modifying `code.*` fields, and re-saving with scipy.
This approach is fundamentally blocked by scipy's inability to serialise MCOS objects.

### What mlx2mlapp currently does

The packager copies the source `appModel.mat` bytes **verbatim** — no Python-side
modification.  This is the only safe option from Python.

| Scenario | Behaviour |
|---|---|
| Design View (blank template) | Empty canvas — correct, no stale components |
| Design View (reference/SimpleMLApp template) | Shows SimpleMLApp's components — misleading |
| Code View (either template) | Shows code regenerated from appModel.mat, NOT our classdef |
| **MATLAB Compiler / webAppCompiler** | **Reads `document.xml` directly — always correct** |

**The deployment use case works.** App Designer's Code View does not, and opening the file
in App Designer before compiling will overwrite `document.xml` with wrong code.

### Recommended workflow

```
1. python mlx2mlapp.py input.mlx output.mlapp --template-mat blank_template_appModel.mat
2. In MATLAB: webAppCompiler → add output.mlapp → Package
   (do NOT open output.mlapp in App Designer first)
3. Deploy .ctf to MATLAB Web App Server
```

### Fix: blank template appModel.mat

Supply an `appModel.mat` from a fresh **Blank App** (no components added, just a UIFigure):

```
MATLAB: App Designer → New → Blank App → (don't add anything) → Save As blank_template.mlapp
shell: python tools/extract_blank_template.py blank_template.mlapp \
            --out reference/blank_template_appModel.mat
shell: python mlx2mlapp.py input.mlx output.mlapp \
            --template-mat reference/blank_template_appModel.mat
```

With a blank template the design canvas will be empty rather than showing a foreign app's
components.  The runtime component layout still comes from `createComponents()` in our
classdef, which executes correctly regardless.

### Generating a fully correct appModel.mat (future work)

A correct `components.UIFigure` MCOS blob must be generated by MATLAB itself.  Options:

1. **MATLAB script**: Write a `matlab.apps.AppBase` subclass, add components via the
   `matlab.ui.*` API, serialize the figure using App Designer's internal serialization API,
   and save the resulting `.mat`.
2. **Compressed-element binary patching**: Parse the mat file's `miCOMPRESSED` elements,
   decompress, patch only the `code.*` text fields in the decompressed bytes, recompress,
   and reconstruct the file.  This preserves MCOS data and avoids scipy savemat entirely.
   Complex but feasible with the zlib Python module.
3. **MATLAB Compiler bypass**: Test whether `webAppCompiler` accepts a bare `.m` classdef
   file directly, bypassing `.mlapp` packaging altogether.

---

## 4. Code Transformation Rules (LiveScript → App Designer classdef)

| LiveScript pattern | App Designer equivalent | Notes |
|---|---|---|
| `varname = value;` (control variable) | Dropped from code; replaced by `varname = app.<Component>.Value;` at top of `runScript` | All live variables read from UI on each run |
| `fig = figure;` / `figure;` | Line dropped entirely | Use `app.UIFigure` |
| `ax = axes;` / `axes;` | Line dropped entirely | Use `app.UIAxes` |
| `plot(ax, ...)` | `plot(app.UIAxes, ...)` | Axes variable substituted |
| `title(...)` | `title(app.UIAxes, ...)` | Prefixed when no axes arg present |
| `xlabel(...)` / `ylabel(...)` / `zlabel(...)` | Same prefix rule | |
| `legend(...)` | `legend(app.UIAxes, ...)` | |
| `hold on` | `hold(app.UIAxes, 'on')` | |
| `hold off` | `hold(app.UIAxes, 'off')` | |
| `grid on` | `app.UIAxes.XGrid = 'on'; app.UIAxes.YGrid = 'on';` | |
| `grid off` | `app.UIAxes.XGrid = 'off'; app.UIAxes.YGrid = 'off';` | |
| Multi-section code | All sections concatenated into `runScript(app)` | Section headings become comments |
| Bare live variables elsewhere in code | Left as-is; local aliases set from UI at top of `runScript` | Scoped correctly within `runScript` |

### Known limitations / edge cases

- **Multiple figures/axes**: Only a single `app.UIAxes` is generated.  LiveScripts using
  multiple `figure` or `axes` calls will need manual cleanup.
- **String literal false positives**: Regex-based variable substitution could match variable
  names inside string literals.  No MATLAB AST parser is used.
- **Conditional variable assignment**: `if ...; ax = axes; end` — the axes-variable detection
  only catches bare top-level assignments.
- **`xlim` / `ylim`**: Currently passed through unchanged (they operate on `gca` implicitly;
  within `runScript` the current axes is `app.UIAxes` so this usually works).
- **`colororder`**: Left as-is; returns the current figure colororder which may differ in App
  Designer context.

---

## 5. UI Control → App Designer Component Mapping

| LiveScript control type | `matlab.ui.control.*` type | Creation function |
|---|---|---|
| `slider` | `Slider` | `uislider` |
| `comboBox` | `DropDown` | `uidropdown` |
| `editField` (numeric default) | `EditField` | `uieditfield(..., 'numeric')` |

Each control is paired with a `Label` (`uilabel`).

### Layout (current implementation)

- Window: 640 × 480 px
- UIAxes: fills top ~70%, leaving a control strip at the bottom
- Controls stacked vertically in the strip, 30 px per row
- Label (80 px wide, right-aligned) + control component to its right
- Run button: bottom-right corner

---

## 6. Deployment Chain Summary

```
LiveScript (.mlx)
      │
      │  python mlx2mlapp.py [--template-mat blank_template_appModel.mat]
      ▼
App Designer (.mlapp)
  ├── matlab/document.xml        ← correct generated classdef (always)
  └── appdesigner/appModel.mat   ← template copied verbatim
      │
      │  !! Do NOT open in App Designer before this step !!
      │  (App Designer overwrites document.xml from appModel.mat on open)
      │
      │  MATLAB: webAppCompiler → add .mlapp → Package
      │  (compiler reads document.xml directly; appModel.mat is ignored)
      ▼
Compiled archive (.ctf)
      │
      │  Deploy to server
      ▼
MATLAB Web App Server
```

MATLAB Compiler reads the classdef from `document.xml` and does **not** invoke App Designer's
model rendering pipeline.  The `appModel.mat` content does not affect compilation.

---

## 7. Open Questions

- **webAppCompiler with mismatched appModel.mat**: Does it compile correctly when
  `components.UIFigure` does not match the classdef?  **Believed yes** — compiler reads
  `document.xml` — but not yet confirmed by a successful end-to-end deployment test.
- **webAppCompiler with a bare `.m` file**: Does `webAppCompiler` accept a plain `.m`
  classdef that inherits from `matlab.apps.AppBase`, bypassing `.mlapp` entirely?  If so,
  we could skip the packaging step and the appModel.mat problem disappears.
- **Compressed-element binary patching**: Is the `code` struct always in a separate
  `miCOMPRESSED` element from `components`, making it safe to decompress/patch/recompress
  just that element?  The blank template appears to have at least two elements.
- **`appdesigner.internal` API**: Is there an undocumented MATLAB API for programmatically
  constructing and saving an appModel.mat?  Worth inspecting
  `matlabroot/toolbox/matlab/appdesigner/` for candidate functions.
- **`xlim` / `ylim` without explicit axes handle**: Do these correctly target `app.UIAxes`
  at runtime?  In a `uifigure` context `gca` returns the current axes of the figure, which
  should be `app.UIAxes` if it is the only axes — but this is untested.
- **App Designer overwrite on save vs. on open**: Does App Designer overwrite `document.xml`
  immediately on open, or only on the first save?  If only on save, the user could open the
  file, inspect Code View, and close without saving to verify the classdef without destroying
  it.
