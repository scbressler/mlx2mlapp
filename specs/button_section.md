# Contract: Code Section with Button Livecontrol

This spec defines how a Live Script section containing a button livecontrol
maps to an App Designer app component and callback.

---

## Input: Initialization Section

A Live Script section whose paragraphs contain only code (no livecontrol)
and which appears before any interactive section.

### Rules

- Each simple assignment of the form `name = expr;` produces one private
  property with that name and initial value.
- The semicolon is stripped; no semicolon appears in the property declaration.
- A `% Description` placeholder comment is appended to each property line.
- Non-assignment statements in an initialization section are ignored.

### Example

Input code:
```
counter = 0;
```

Output private property:
```matlab
counter = 0 % Description
```

---

## Input: Button Section

A Live Script section containing:
- One or more `<w:pStyle w:val="code"/>` paragraphs with MATLAB code
- An embedded `livecontrol` customXml element with `"type": "button"`

### Rules

- The button label comes from `data.text` in the livecontrol `context` JSON.
- The component name is `{Label}Button` (e.g. `RunButton`).
- The callback method name is `{Label}ButtonPushed` (e.g. `RunButtonPushed`).
- All bare references to known private property names in the code body are
  prefixed with `app.` (word-boundary replacement, not preceded by `.`).
- Leading and trailing blank lines in the code block are stripped.

### Example

Input livecontrol context:
```json
{"type": "button", "data": {"text": "Run", ...}}
```

Input code block:
```
counter = counter + 1;
disp(counter);
```

Output components in layout XML (layout engine path, 1100×760 canvas):
```xml
<Button name='RunButton'>
    <ButtonPushedFcn>RunButtonPushed</ButtonPushedFcn>
    <Position>[20 708 1060 32]</Position>
    <Text>'Run'</Text>
</Button>
<TextArea name='RunCodeTextArea'>
    <BackgroundColor>[0 0 0]</BackgroundColor>
    <Editable>'off'</Editable>
    <FontColor>[1 1 1]</FontColor>
    <FontName>'Courier New'</FontName>
    <Position>[20 578 1060 120]</Position>
    <Value>{'counter = counter + 1;'; 'disp(counter);'}</Value>
</TextArea>
<TextArea name='RunOutputTextArea'>
    <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
    <Editable>'off'</Editable>
    <FontColor>[0.4 1 0.4]</FontColor>
    <FontName>'Courier New'</FontName>
    <Position>[20 448 1060 120]</Position>
    <Value>''</Value>
</TextArea>
```

Output callback in classdef (diary-wrapped):
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

---

## Output: Public Component Properties

Each button section adds three public properties: `{Label}Button`,
`{Label}CodeTextArea`, and `{Label}OutputTextArea`.

Property declarations are right-padded so type annotations align.

---

## Output: Layout XML

- Root element is `<Components>`.
- `<UIFigure>` is the sole child of `<Components>`.
- UIFigure uses the layout engine canvas: `<Position>[100 100 1100 760]</Position>`.
- Button sections always use the layout engine path (never the fixed 640×480 path).
- Component property elements are in alphabetical order; `<Children>` is always last.
- Button height: 32px, full usable width (1060px), left-aligned at x=20.
- CodeTextArea and OutputTextArea follow the button with 10px row gap between each.
  See `specs/output_capture.md` for TextArea styling and height.

---

## Out of Scope for This Contract

- Multiple buttons (layout is not specified here)
- Sections with no livecontrol that are not initialization sections
- Livecontrol types other than button
