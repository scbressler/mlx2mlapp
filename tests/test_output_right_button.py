"""
Golden test for the output_right_button exemplar.
Covers: button section in output_right view mode →
  Left column:  RunButton + RunCodeTextArea (narrower, 520 px)
  Right column: RunOutputTextArea (top-aligned to section start, 520 px)
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/output_right_button")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/output_right_button.m"
EXPECTED_XML = GOLDEN_DIR / "expected/output_right_button.xml"

GOLDEN_APP_ID = "d4e5f6a7-b8c9-0123-defa-123456789012"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "output_right_button"


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines())


def outputs():
    return translate(
        str(INPUT_XML),
        class_name=GOLDEN_CLASS,
        app_id=GOLDEN_APP_ID,
        release=GOLDEN_RELEASE,
        view_mode="output_right",
    )


def test_layout_xml():
    _, layout_xml = outputs()
    expected = EXPECTED_XML.read_text()
    assert normalize(layout_xml) == normalize(expected)


def test_m_file():
    m_text, _ = outputs()
    expected = EXPECTED_M.read_text()
    assert normalize(m_text) == normalize(expected)
