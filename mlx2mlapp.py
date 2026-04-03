#!/usr/bin/env python3
"""
mlx2mlapp.py — Convert a MATLAB LiveScript (.mlx) to an App Designer file (.mlapp).

Usage
-----
    python mlx2mlapp.py <input.mlx> <output.mlapp> [options]

Options
-------
    --app-name NAME      Class/app name (default: derived from output filename)
    --release RELEASE    Target MATLAB release string (default: R2025b)
    -v, --verbose        Print conversion summary
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _derive_app_name(output_path: str) -> str:
    """Derive a valid MATLAB class name from the output filename."""
    stem = Path(output_path).stem
    # Remove invalid characters, ensure starts with a letter
    import re
    name = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    if name and name[0].isdigit():
        name = "App_" + name
    return name or "GeneratedApp"


def convert(
    input_path: str,
    output_path: str,
    app_name: str | None = None,
    release: str = "R2025b",
    template_mat: str | None = None,
    finalize: bool = False,
    verbose: bool = False,
) -> None:
    """
    Full pipeline: parse → codegen → pack [→ finalize with MATLAB].

    Parameters
    ----------
    input_path:    Path to the source .mlx file.
    output_path:   Destination path for the .mlapp file.
    app_name:      MATLAB class name.  Derived from *output_path* if None.
    release:       Target MATLAB release string, e.g. ``'R2025b'``.
    template_mat:  Optional path to an appModel.mat from a blank App Designer
                   app (New → Blank App → save → unzip → appdesigner/appModel.mat).
                   When supplied, the design view in App Designer will show a
                   blank canvas instead of the reference app's layout.
                   When None, the bundled SimpleMLApp reference mat is used.
    finalize:      If True, run tools/finalize_mlapp.m via MATLAB after
                   packaging to regenerate a proper appModel.mat.  Requires
                   MATLAB on PATH (or MATLAB_PATH env var).
    verbose:       Print a conversion summary to stdout.
    """
    # Lazy imports so the module is importable even before pip install
    from src.parser import parse
    from src.codegen import generate
    from src.packager import pack

    if app_name is None:
        app_name = _derive_app_name(output_path)

    # ── 1. Parse ──────────────────────────────────────────────────────
    ls = parse(input_path)

    if verbose:
        print(f"Parsed  : {input_path}")
        print(f"Sections: {len(ls.sections)}")
        for i, s in enumerate(ls.sections):
            heading = s.heading or "(no heading)"
            n_ctrl  = len(s.controls)
            n_lines = len(s.code.splitlines()) if s.code else 0
            print(f"  [{i}] {heading!r:40s}  {n_lines:4d} code lines  {n_ctrl} controls")
        if ls.all_controls:
            print("Controls:")
            for c in ls.all_controls:
                print(f"  {c.variable:<20s} {c.type:<12s} default={c.default}")
        print()

    # ── 2. Generate classdef ──────────────────────────────────────────
    classdef = generate(ls, app_name=app_name)

    if verbose:
        print(f"Generated classdef: {len(classdef.splitlines())} lines")

    # ── 3. Package ────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    pack(classdef, output_path, app_name=app_name, matlab_release=release,
         template_mat=template_mat)

    if verbose:
        size_kb = Path(output_path).stat().st_size / 1024
        print(f"Written : {output_path}  ({size_kb:.1f} KB)")

    # ── 4. Finalize via MATLAB (regenerate appModel.mat) ─────────────
    if finalize:
        from tools.run_finalize import run_finalize
        if verbose:
            print("Running finalize_mlapp.m via MATLAB ...")
        rc = run_finalize(output_path)
        if rc != 0:
            raise RuntimeError(
                f"finalize_mlapp.m failed (exit code {rc}). "
                "Check that MATLAB is on PATH or set MATLAB_PATH."
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mlx2mlapp",
        description="Convert a MATLAB LiveScript (.mlx) to App Designer (.mlapp)",
    )
    parser.add_argument("input",  help="Source .mlx file")
    parser.add_argument("output", help="Destination .mlapp file")
    parser.add_argument("--app-name", default=None,
                        help="MATLAB class name (default: derived from output filename)")
    parser.add_argument("--release", default="R2025b",
                        help="Target MATLAB release (default: R2025b)")
    parser.add_argument("--template-mat", default=None, metavar="PATH",
                        help=(
                            "Path to an appModel.mat from a blank App Designer app. "
                            "Gives App Designer a clean design-view canvas. "
                            "Create one: App Designer → New → Blank App → save as "
                            "blank.mlapp → unzip → appdesigner/appModel.mat"
                        ))
    parser.add_argument("--finalize", action="store_true",
                        help=(
                            "After packaging, run tools/finalize_mlapp.m via MATLAB "
                            "to regenerate a proper appModel.mat (requires MATLAB on "
                            "PATH or MATLAB_PATH env var). Produces a .mlapp that "
                            "opens correctly in App Designer."
                        ))
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print conversion summary")

    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 1

    if args.template_mat and not os.path.exists(args.template_mat):
        print(f"Error: template mat not found: {args.template_mat}", file=sys.stderr)
        return 1

    try:
        convert(
            input_path=args.input,
            output_path=args.output,
            app_name=args.app_name,
            release=args.release,
            template_mat=args.template_mat,
            finalize=args.finalize,
            verbose=args.verbose,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
