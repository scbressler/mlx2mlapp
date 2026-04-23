"""
Entry point for the Live Script → App Designer translator.

Supported input formats:
    - Plain-text Live Script (.m):  parsed by parse_plaintext()
    - Live Script binary (.mlx):    unzipped; matlab/document.xml parsed by parse_document()
    - Raw document.xml:             parsed by parse_document() (legacy / test fixture path)

Usage (module):
    from src.translate import translate
    m_text, layout_xml = translate("path/to/script.m", "MyApp")
    m_text, layout_xml = translate("path/to/script.mlx", "MyApp")

Usage (CLI):
    python -m src.translate script.m   MyApp [--release R2025b] [--out-dir .]
    python -m src.translate script.mlx MyApp [--release R2025b] [--out-dir .]
"""
import tempfile
import zipfile
from pathlib import Path

from .parse import parse_document
from .parse_plaintext import parse_plaintext
from .codegen import generate_layout_xml, generate_m


def translate(input_path: str, class_name: str, app_id: str = None,
              release: str = "R2025b", view_mode: str = "output_inline") -> tuple:
    """
    Translate a Live Script into App Designer plain-text files.

    Args:
        input_path: Path to a plain-text Live Script (.m), a binary Live Script
                    (.mlx), or a raw document.xml extracted from a .mlx archive.
        class_name: MATLAB classdef name for the generated app.
        app_id:     UUID string for the app (random if None).
        release:    MATLAB release string embedded in appendix (default "R2025b").
        view_mode:  Layout strategy — "output_inline" (default), "output_right",
                    or "hide_code".

    Returns:
        (m_text, layout_xml_text)
    """
    suffix = Path(input_path).suffix.lower()

    if suffix == '.m':
        ir = parse_plaintext(input_path, class_name)
    elif suffix == '.mlx':
        ir = _parse_mlx(input_path, class_name)
    else:
        # Treat as a raw document.xml (existing behaviour; used by all golden tests)
        ir = parse_document(input_path, class_name)

    layout_xml = generate_layout_xml(ir, view_mode=view_mode)
    m_text = generate_m(ir, layout_xml, app_id=app_id, release=release)
    return m_text, layout_xml


def _parse_mlx(mlx_path: str, class_name: str):
    """Unzip a .mlx file and parse its embedded document.xml."""
    with zipfile.ZipFile(mlx_path) as zf:
        with zf.open('matlab/document.xml') as xml_file:
            xml_bytes = xml_file.read()

    # Write to a temp file so parse_document (which takes a file path) can read it
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
        tmp.write(xml_bytes)
        tmp_path = tmp.name

    try:
        return parse_document(tmp_path, class_name)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Translate a Live Script (.m or .mlx) to App Designer files."
    )
    parser.add_argument(
        "input_path",
        help="Path to a plain-text Live Script (.m), binary Live Script (.mlx), "
             "or raw document.xml",
    )
    parser.add_argument("class_name", help="MATLAB class name for the output app")
    parser.add_argument("--release", default="R2025b",
                        help="MATLAB release string (default: R2025b)")
    parser.add_argument("--view-mode", default="output_inline",
                        choices=["output_inline", "output_right", "hide_code"],
                        help="Layout mode (default: output_inline)")
    parser.add_argument("--out-dir", default=".", help="Output directory")
    args = parser.parse_args()

    m_text, layout_xml = translate(
        args.input_path,
        args.class_name,
        release=args.release,
        view_mode=args.view_mode,
    )

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.class_name}.m").write_text(m_text)
    (out / f"{args.class_name}.xml").write_text(layout_xml)
    print(f"Wrote {args.class_name}.m and {args.class_name}.xml to {out}/")
