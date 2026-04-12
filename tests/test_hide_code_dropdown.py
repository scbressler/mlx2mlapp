"""
Golden test for the hide_code_dropdown exemplar.
Covers: dropdown section in hide_code view mode →
  DropDown + DropDownOutputTextArea only (no CodeTextArea), full 1060 px width.
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/hide_code_dropdown")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/hide_code_dropdown.m"
EXPECTED_XML = GOLDEN_DIR / "expected/hide_code_dropdown.xml"

GOLDEN_APP_ID = "f6a7b8c9-d0e1-2345-fabc-345678901234"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "hide_code_dropdown"


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines())


def outputs():
    return translate(
        str(INPUT_XML),
        class_name=GOLDEN_CLASS,
        app_id=GOLDEN_APP_ID,
        release=GOLDEN_RELEASE,
        view_mode="hide_code",
    )


def test_layout_xml():
    _, layout_xml = outputs()
    expected = EXPECTED_XML.read_text()
    assert normalize(layout_xml) == normalize(expected)


def test_m_file():
    m_text, _ = outputs()
    expected = EXPECTED_M.read_text()
    assert normalize(m_text) == normalize(expected)
