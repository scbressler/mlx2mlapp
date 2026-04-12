"""
Golden test for the hide_code_output exemplar.
Covers: display section in hide_code view mode → OutputTextArea only (no CodeTextArea).
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/hide_code_output")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/hide_code_output.m"
EXPECTED_XML = GOLDEN_DIR / "expected/hide_code_output.xml"

GOLDEN_APP_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "hide_code_output"


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
