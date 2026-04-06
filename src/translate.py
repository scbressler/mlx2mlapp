"""
Entry point for the Live Script → App Designer translator.

Usage (module):
    from src.translate import translate
    m_text, layout_xml = translate("path/to/document.xml", "MyApp")

Usage (CLI):
    python -m src.translate document.xml MyApp [--release R2025b] [--out-dir .]
"""
from .parse import parse_document
from .codegen import generate_layout_xml, generate_m


def translate(xml_path: str, class_name: str, app_id: str = None,
              release: str = "R2025b") -> tuple:
    """
    Translate a Live Script document.xml into App Designer plain-text files.

    Returns:
        (m_text, layout_xml_text)
    """
    ir = parse_document(xml_path, class_name)
    layout_xml = generate_layout_xml(ir)
    m_text = generate_m(ir, layout_xml, app_id=app_id, release=release)
    return m_text, layout_xml


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Translate a Live Script document.xml to App Designer files."
    )
    parser.add_argument("xml_path", help="Path to the Live Script document.xml")
    parser.add_argument("class_name", help="MATLAB class name for the output app")
    parser.add_argument("--release", default="R2025b",
                        help="MATLAB release string (default: R2025b)")
    parser.add_argument("--out-dir", default=".", help="Output directory")
    args = parser.parse_args()

    m_text, layout_xml = translate(args.xml_path, args.class_name,
                                   release=args.release)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.class_name}.m").write_text(m_text)
    (out / f"{args.class_name}.xml").write_text(layout_xml)
    print(f"Wrote {args.class_name}.m and {args.class_name}.xml to {out}/")
