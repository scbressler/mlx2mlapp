# mlx2mlapp — MATLAB LiveScript to App Designer Converter

## Project Goal
Convert a MATLAB LiveScript plain-text file (.mlx or .m Live Code format)
into a valid MATLAB App Designer file (.mlapp) suitable for packaging
with MATLAB Compiler for deployment to MATLAB Web App Server.

## Key Technical Facts
- .mlapp files are ZIP archives containing:
  - matlab/document.xml  (classdef code wrapped in XML)
  - metadata/appDesigner/appModel.mat (UI layout/model data)
  - [Content_Types].xml and _rels/.rels (Open Packaging Conventions)
- .mlapp format is undocumented by MathWorks and subject to change
- Source LiveScripts use custom markup in comments for text, output, controls
- Target is a minimal App Designer app that wraps the LiveScript logic
- Deployment chain: .mlapp → MATLAB Compiler (webAppCompiler) → .ctf → WebApp Server

## Language
Python (primary) — for file parsing, ZIP manipulation, XML generation

## Key Commands
- Run converter: python mlx2mlapp.py <input.mlx> <output.mlapp>
- Run tests: pytest tests/
```

---

### Step 3 — Scaffold your initial file structure

Create a few starter files so Claude Code has something concrete to work with and extend:
```
mlx2mlapp/
├── CLAUDE.md
├── README.md
├── mlx2mlapp.py          ← main entry point
├── src/
│   ├── parser.py         ← parse plain-text LiveScript markup
│   ├── codegen.py        ← generate App Designer classdef code
│   ├── packager.py       ← assemble the .mlapp ZIP structure
│   └── templates/
│       ├── document_xml.j2   ← Jinja2 template for document.xml
│       └── content_types.xml ← static OPC boilerplate
├── tests/
│   ├── test_parser.py
│   └── sample_inputs/
│       └── hello_world.m     ← a simple LiveScript for testing
└── reference/
    └── NOTES.md          ← your reverse-engineering findings
