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

Output component in layout XML:
```xml
<Button name='RunButton'>
    <ButtonPushedFcn>RunButtonPushed</ButtonPushedFcn>
    <Position>[272 219 100 22]</Position>
    <Text>'Run'</Text>
</Button>
```

Output callback in classdef:
```matlab
% Button pushed function: RunButton
function RunButtonPushed(app, event)
    app.counter = app.counter + 1;
    disp(app.counter);
end
```

---

## Output: Public Component Properties

The app always declares `UIFigure` as a public property.
Each button section adds one `{Label}Button` public property.

Property declarations are right-padded so type annotations align.

---

## Output: Layout XML

- Root element is `<Components>`.
- `<UIFigure>` is the sole child of `<Components>`.
- UIFigure properties: `<Name>'MATLAB App'</Name>`, `<Position>[100 100 640 480]</Position>`.
- Component property elements are in alphabetical order.
- `<Children>` is always last.
- Default button position for a single centered button: `[272 219 100 22]`.

---

## Out of Scope for This Contract

- Multiple buttons (layout is not specified here)
- Sections with no livecontrol that are not initialization sections
- Livecontrol types other than button
