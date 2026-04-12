"""
Golden test for the output_right_plot exemplar.
Covers: plot section in output_right view mode →
  Left column:  Labels (heading + body text, 520 px)
  Right column: UIAxes (440 px tall, top-aligned to section start)
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/output_right_plot")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/output_right_plot.m"
EXPECTED_XML = GOLDEN_DIR / "expected/output_right_plot.xml"

GOLDEN_APP_ID = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "output_right_plot"


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
