"""
Golden test for the hide_code_plot exemplar.
Covers: plot section in hide_code view mode → layout identical to output_inline
(no CodeTextArea to suppress; Labels + UIAxes at full 1060 px width).
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/hide_code_plot")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/hide_code_plot.m"
EXPECTED_XML = GOLDEN_DIR / "expected/hide_code_plot.xml"

GOLDEN_APP_ID = "c3d4e5f6-a7b8-9012-cdef-012345678901"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "hide_code_plot"


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
