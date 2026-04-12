# Contract: Output Capture

This spec defines how MATLAB code and its dynamic text output are displayed
in generated App Designer apps.

---

## Motivation

Live Script sections contain visible code and produce text output (from `disp()`,
`fprintf()`, or expressions without semicolons). Generated apps must show both:
the source code (static) and the output it produces when run (dynamic).

---

## Scope

Every section that contains executable MATLAB code gets two TextArea components:
- A **CodeTextArea** — shows the source code, static, set at design time
- An **OutputTextArea** — shows captured runtime output, populated by a callback

Initialization sections (whose assignments become private properties) do NOT get
TextAreas — they produce no visible code or output.

This contract covers three section types:
- **Display sections** — code with no livecontrol and no plot call
- **Button sections** — code + button livecontrol
- **Dropdown sections** — code + comboBox livecontrol

Initialization sections (pure assignments) do NOT get TextAreas.

---

## Component Naming

**Display sections** — named globally across all display sections:
- 1 display section: `CodeTextArea` / `OutputTextArea`
- 2+ display sections: `CodeTextArea_1` / `OutputTextArea_1`, `CodeTextArea_2` / `OutputTextArea_2`, …

`code_text_area_name` and `output_text_area_name` are set on `SectionIR` by codegen.

**Button sections** — named after the button label:
- `{Label}CodeTextArea` / `{Label}OutputTextArea` (e.g. `RunCodeTextArea` / `RunOutputTextArea`)

**Dropdown sections** — named after the PascalCase component name:
- `{ComponentName}CodeTextArea` / `{ComponentName}OutputTextArea` (e.g. `DropDownCodeTextArea` / `DropDownOutputTextArea`)

`code_text_area_name` and `output_text_area_name` are set on `ButtonSection` and
`DropDownSection` by `_assign_text_area_names()` in codegen.

---

## CodeTextArea Component Properties

| Property | Value |
|---|---|
| `BackgroundColor` | `[0 0 0]` |
| `Editable` | `'off'` |
| `FontColor` | `[1 1 1]` |
| `FontName` | `'Courier New'` |
| `Position` | computed by layout engine |
| `Value` | cell array of code lines (or single string for 1 line) |

Height: **120px**

`Value` format (confirmed against `matlab/text_area/textArea_example_app.m`):
- Single line: `'code line'`
- Multiple lines: `{'line1'; 'line2'; ...}`
- Single quotes in code lines are escaped by doubling: `'` → `''`

---

## OutputTextArea Component Properties

| Property | Value |
|---|---|
| `BackgroundColor` | `[0.149 0.149 0.149]` |
| `Editable` | `'off'` |
| `FontColor` | `[0.4 1 0.4]` |
| `FontName` | `'Courier New'` |
| `Position` | computed by layout engine |
| `Value` | `''` (empty, populated at runtime) |

Height: **120px**

---

## XML Layout Entry (properties in alphabetical order)

```xml
<TextArea name='CodeTextArea'>
    <BackgroundColor>[0 0 0]</BackgroundColor>
    <Editable>'off'</Editable>
    <FontColor>[1 1 1]</FontColor>
    <FontName>'Courier New'</FontName>
    <Position>[20 bottom 1060 120]</Position>
    <Value>{'a = 1;'; 'fprintf(''The value of a is %d'',a);'}</Value>
</TextArea>
<TextArea name='OutputTextArea'>
    <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
    <Editable>'off'</Editable>
    <FontColor>[0.4 1 0.4]</FontColor>
    <FontName>'Courier New'</FontName>
    <Position>[20 bottom 1060 120]</Position>
    <Value>''</Value>
</TextArea>
```

Do not include a `label` attribute on TextArea tags — that attribute links a
TextArea to a paired input Label. Our TextAreas are output displays, not inputs.

---

## Layout Placement (Inline Mode)

Within each section, the component stack order is:

1. Labels (heading, text)
2. Button / DropDown widget (if interactive section)
3. CodeTextArea
4. UIAxes (if plot section)
5. OutputTextArea

Row height: 120px for both TextAreas. `_ROW_GAP` (10px) after each component
except the last. The last component in a section uses `_SECTION_GAP` (20px),
or `_ROW_GAP` if it is the final section.

---

## Output Capture Mechanism

Text output is captured using MATLAB's `diary` command:

```matlab
diaryFile = [tempname '.txt'];
diary(diaryFile);
diary('on');
% ... section code lines ...
diary('off');
if exist(diaryFile, 'file')
    capturedOutput = fileread(diaryFile);
    delete(diaryFile);
else
    capturedOutput = '';
end
app.OutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
```

This pattern:
- Captures all command window output (disp, fprintf, unsilenced expressions)
- Trims leading/trailing whitespace before splitting into lines
- Sets `OutputTextArea.Value` as a cell array of strings (MATLAB's required format)

---

## Code Pattern: Button/Dropdown Section in Callback

Button and dropdown callbacks wrap the code body in the same `diary` pattern.
The diary block follows the bound-variable assignment (for dropdowns) and
precedes the remaining code lines.

```matlab
% Button pushed function: RunButton
function RunButtonPushed(app, event)
    diaryFile = [tempname '.txt'];
    diary(diaryFile);
    diary('on');
    app.counter = app.counter + 1;
    disp(app.counter);
    diary('off');
    if exist(diaryFile, 'file')
        capturedOutput = fileread(diaryFile);
        delete(diaryFile);
    else
        capturedOutput = '';
    end
    app.RunOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
end
```

For dropdowns, the bound-var assignment comes first (before the diary block):
```matlab
function DropDownValueChanged(app, event)
    app.value = app.DropDown.Value;
    diaryFile = [tempname '.txt'];
    diary(diaryFile);
    diary('on');
    disp(app.value);
    diary('off');
    ...
    app.DropDownOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
end
```

No `startupFcn` or `%[app:runConfiguration]` is added for button/dropdown-only apps.

---

## Code Pattern: Display Section in startupFcn

Display sections run in `startupFcn(app)`. Variables are local (not promoted to
private properties). No `app.` prefixing is applied to code lines.

```matlab
% Code that executes after component creation
function startupFcn(app)
    diaryFile = [tempname '.txt'];
    diary(diaryFile);
    diary('on');
    a = 1;
    fprintf('The value of a is %d',a);
    diary('off');
    if exist(diaryFile, 'file')
        capturedOutput = fileread(diaryFile);
        delete(diaryFile);
    else
        capturedOutput = '';
    end
    app.OutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
end
```

A `%[app:runConfiguration]` appendix section is emitted (same as plot sections).

---

## Detection: Display Section

A section is a display section when ALL of the following are true:
- No livecontrol element
- No recognized plot function call
- No labels (heading/text paragraphs)
- Code lines are NOT all pure assignments (at least one line does not match
  `\w+ = expr;`)

A "pure assignment" line matches: `^\s*\w+\s*=\s*.+?;?\s*$`

If all lines are pure assignments, the section remains an initialization section
(private properties, no SectionIR).

---

## IR Changes

`SectionIR` gets three new fields (display sections):
```python
code_lines: list = field(default_factory=list)
code_text_area_name: str = ""
output_text_area_name: str = ""
```

`ButtonSection` and `DropDownSection` each get two new fields:
```python
code_text_area_name: str = ""
output_text_area_name: str = ""
```

All six names are set by `_assign_text_area_names()` in codegen before XML generation.

---

## Canvas Height Impact

At 120px per TextArea × 2 + 10px gap between = 250px per display section.
This leaves 470px of usable height (720 - 250) for labels and other components
in a single-display-section app — sufficient for one UIAxes (440px) with room
for one heading label.

---

## Out of Scope

- Per-output-statement capture (one TextArea per disp call)
- Syntax highlighting
- Output from initialization sections
- Unsilenced assignment expressions echoing to command window
