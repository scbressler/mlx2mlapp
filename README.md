# Live Script → App Designer Translator

This repository contains a prototype workflow for converting a MATLAB Live Script
(saved in plain‑text Live Code format) into a plain‑text App Designer app that can
be opened and edited in MATLAB App Designer.

The goal is not to support every Live Script feature, but to reliably translate
**interactive intent** into a valid, editable App Designer app.

---

## What This Project Is (and Is Not)

This project is:

- A deterministic translator from Live Script structure to App Designer structure
- A testbed for understanding the plain‑text App Designer format
- A foundation for AI‑assisted or agentic app‑generation workflows

This project is not:

- A general Live Script renderer
- A visual layout optimizer
- A replacement for App Designer’s interactive authoring tools

Keeping this boundary explicit is essential for progress.

---

## Repository Structure
.
├── specs/          # Contracts the translator must obey
├── golden/         # Minimal, authoritative exemplars
├── tools/          # One‑off scripts for extraction or validation
├── src/            # Translation logic (IR → XML → M)
└── README.md

Each directory has a single responsibility. If a file feels like it belongs in
more than one place, that’s usually a signal to simplify.

---

## How to Succeed with This Project

### Start from Golden Exemplars

All translation logic should be validated against the contents of `golden/`.

Golden exemplars are intentionally small and boring. Each one exists to prove
a specific semantic contract, such as:

- A button maps cleanly to a callback
- A value‑producing control updates application state
- A plotting section implies a persistent UIAxes

If a change breaks a golden exemplar, treat that as a real regression.

---

### Treat `specs/` as Law, Not Guidance

The files in `specs/` define what “correct” means.

They are:

- Declarative
- Narrow in scope
- Free of examples and heuristics

When the translator’s behavior is unclear, the right question is:
“Which spec applies here?”

If the answer is “none,” update the specs *before* updating the code.

---

### Use an Intermediate Representation (IR)

Do not translate directly from Live Script XML to App Designer XML.

Instead:

1. Parse the Live Script into a structured IR
2. Translate the IR into:
   - layout XML
   - MATLAB class code

This separation dramatically reduces complexity and makes failures explainable.

---

### Prefer Determinism Over Cleverness

This project values:

- Stable output
- Predictable naming
- Small, inspectable diffs

It intentionally avoids:

- Layout inference based on rendered output
- Heuristic “best guess” UI placement
- Rewriting user computation logic

If the translator cannot be sure, it should choose the simplest valid option.

---

### Optimize for App Designer Editability

A successful output is not just runnable — it must be **editable in App Designer**.

That means:

- All callbacks referenced in XML exist in the `.m` file
- UI components have stable, readable names
- Business logic is separated from UI callbacks where possible

If App Designer opens the app cleanly and the user can keep working, the translation succeeded.

---

## Expected Workflow

A typical iteration looks like this:

1. Add or modify a golden exemplar
2. Update or clarify specs if needed
3. Run the translator
4. Validate against golden output
5. Open the result in App Designer
6. Fix the *smallest* thing that broke

Skipping steps usually leads to brittle behavior later.

---

## A Note on Scope

This repository intentionally ignores many Live Script and App Designer features.
That is not a limitation — it is a strategy.

New features should only be added when they introduce a **new semantic requirement**,
not just a new widget.

---

## Final Guiding Principle

If you ever feel tempted to ask:
“Should the translator be smarter here?”

First ask:
“Can I make the contract clearer instead?”

Clarity beats cleverness every time.