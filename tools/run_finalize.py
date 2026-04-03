#!/usr/bin/env python3
"""
run_finalize.py — Regenerate appModel.mat and patch it into a .mlapp file.

Usage
-----
    python tools/run_finalize.py <input.mlapp> [<output.mlapp>]

Requires MATLAB to be on PATH (or set MATLAB_PATH env var).

Workflow
--------
1. Calls tools/finalize_mlapp.m via `matlab -batch` which:
     - Instantiates the generated app class (runs createComponents)
     - Injects DesignTimeProperties.CodeName onto every component
     - Saves a properly-structured appModel.mat (with appData struct and
       App Designer's pre-save component adjusters) to a temp path
2. Patches the .mlapp ZIP using Python's zipfile module, replacing
   appdesigner/appModel.mat with the newly generated one.
   Python handles the ZIP so entry paths are preserved correctly.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def find_matlab() -> str:
    """Return path to the matlab executable."""
    env_path = os.environ.get("MATLAB_PATH")
    if env_path:
        return env_path

    # Common macOS install paths — pick the newest
    mac_paths = sorted(Path("/Applications").glob("MATLAB_R*.app/bin/matlab"), reverse=True)
    if mac_paths:
        return str(mac_paths[0])

    return "matlab"


def patch_zip(zip_in: str, zip_out: str, entry: str, new_file: str) -> None:
    """Replace one entry in a ZIP archive, preserving all other entry paths."""
    new_bytes = Path(new_file).read_bytes()

    tmp = zip_out + ".tmp"
    with zipfile.ZipFile(zip_in, "r") as zin, \
         zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == entry:
                zout.writestr(item, new_bytes)
            else:
                zout.writestr(item, zin.read(item.filename))

    Path(tmp).replace(zip_out)


def run_finalize(mlapp_in: str, mlapp_out: str | None = None) -> int:
    mlapp_in  = str(Path(mlapp_in).resolve())
    mlapp_out = str(Path(mlapp_out).resolve()) if mlapp_out else mlapp_in

    project_dir = Path(__file__).parent.parent.resolve()
    matlab      = find_matlab()

    # MATLAB writes the new appModel.mat here; Python patches it into the ZIP
    mat_fd, mat_path = tempfile.mkstemp(suffix=".mat", prefix="appModel_")
    os.close(mat_fd)

    try:
        cmd_str = (
            f"cd('{project_dir}'); "
            f"addpath('tools'); "
            f"finalize_mlapp('{mlapp_in}', '{mat_path}'); "
            f"exit(0);"
        )

        print(f"Running MATLAB: {matlab} -batch ...")
        print(f"  Input:  {mlapp_in}")
        print(f"  Output: {mlapp_out}")

        result = subprocess.run([matlab, "-batch", cmd_str])

        if result.returncode != 0:
            print(f"\nMATLAB exited with code {result.returncode}", file=sys.stderr)
            return result.returncode

        if not Path(mat_path).exists() or Path(mat_path).stat().st_size == 0:
            print("Error: MATLAB did not produce appModel.mat", file=sys.stderr)
            return 1

        print(f"Patching appdesigner/appModel.mat into {mlapp_out} ...")
        if mlapp_in != mlapp_out:
            shutil.copy2(mlapp_in, mlapp_out)

        patch_zip(mlapp_out, mlapp_out, "appdesigner/appModel.mat", mat_path)
        print("finalize_mlapp completed successfully.")
        return 0

    finally:
        try:
            os.unlink(mat_path)
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_finalize",
        description="Regenerate appModel.mat in a .mlapp file using MATLAB",
    )
    parser.add_argument("input",  help="Python-generated .mlapp file")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output .mlapp path (default: overwrite input)")
    args = parser.parse_args(argv)

    if not Path(args.input).exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        return 1

    return run_finalize(args.input, args.output)


if __name__ == "__main__":
    sys.exit(main())
