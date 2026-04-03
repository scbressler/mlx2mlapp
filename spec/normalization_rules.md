# Normalization Rules

This document defines normalization rules used to ensure stable diffs
and reproducible golden exemplar comparisons.

---

## XML Normalization

- Whitespace differences are ignored unless semantically meaningful.
- Attribute ordering is ignored.
- Element ordering is preserved where required (e.g., `<Children>`).

---

## Property Ordering

- Component property order is not semantically significant.
- `<Children>` MUST appear last and is order‑sensitive.

---

## Numeric and String Formatting

- Numeric arrays are compared by value, not textual formatting.
- String quoting differences (`'` vs `"`) are treated as equivalent
  where MATLAB semantics allow.

---

## Comparison Scope

- Only user‑visible layout and callback declarations are compared.
- Internal metadata, IDs, timestamps, and editor artifacts are ignored.