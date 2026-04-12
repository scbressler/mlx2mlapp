"""
Golden test for the output_right_multi exemplar.
Covers: two-section app in output_right view mode —
  Section 1 (display):  CodeTextArea left + OutputTextArea right, symmetric
  Section 2 (button):   RunButton + RunCodeTextArea left, RunOutputTextArea right
Exercises global y_cursor advancement across section boundary with _SECTION_GAP.
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/output_right_multi")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/output_right_multi.m"
EXPECTED_XML = GOLDEN_DIR / "expected/output_right_multi.xml"

GOLDEN_APP_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "output_right_multi"


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
