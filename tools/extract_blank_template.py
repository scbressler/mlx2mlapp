#!/usr/bin/env python3
"""
extract_blank_template.py — Extract appModel.mat from a blank App Designer app.

Usage
-----
    python tools/extract_blank_template.py <blank.mlapp> [--out PATH]

Creates the blank template .mat file used by mlx2mlapp's --template-mat flag.

How to create blank.mlapp in MATLAB
-------------------------------------
  1. Open MATLAB → Apps tab → Design App → Blank App
  2. Do NOT add any components — leave the canvas empty
  3. File → Save As → blank_template.mlapp
  4. Run:  python tools/extract_blank_template.py blank_template.mlapp

The extracted appModel.mat will have only a UIFigure with no child
components.  When mlx2mlapp uses it as a template, App Designer will
open the generated app with a blank canvas (design view) but the
correct code in Code View.  MATLAB Compiler always uses the classdef
from document.xml regardless.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


def extract(mlapp_path: str, out_path: str) -> None:
    with zipfile.ZipFile(mlapp_path) as zf:
        names = zf.namelist()
        mat_name = next(
            (n for n in names if n.endswith("appModel.mat")),
            None,
        )
        if mat_name is None:
            print(f"Error: no appModel.mat found in {mlapp_path}", file=sys.stderr)
            sys.exit(1)
        data = zf.read(mat_name)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(data)
    print(f"Extracted {mat_name} ({len(data)} bytes) → {out_path}")
    print()
    print("Use with:")
    print(f"  python mlx2mlapp.py input.mlx output.mlapp --template-mat {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract appModel.mat from a blank App Designer .mlapp file"
    )
    parser.add_argument("mlapp", help="Path to a blank App Designer .mlapp file")
    parser.add_argument(
        "--out", default="reference/blank_template_appModel.mat",
        help="Output path for the extracted .mat (default: reference/blank_template_appModel.mat)"
    )
    args = parser.parse_args()
    extract(args.mlapp, args.out)


if __name__ == "__main__":
    main()
