"""
Golden test for the minimal_axes_with_text exemplar.
Covers: heading + body text labels + UIAxes with layout engine (1440x1024 canvas).
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/minimal_axes_with_text")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/minimal_axes_with_text.m"
EXPECTED_XML = GOLDEN_DIR / "expected/minimal_axes_with_text.xml"

GOLDEN_APP_ID = "c4d5e6f7-a8b9-0123-4567-890123456789"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "minimal_axes_with_text"


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines())


def outputs():
    return translate(
        str(INPUT_XML),
        class_name=GOLDEN_CLASS,
        app_id=GOLDEN_APP_ID,
        release=GOLDEN_RELEASE,
    )


def test_layout_xml():
    _, layout_xml = outputs()
    expected = EXPECTED_XML.read_text()
    assert normalize(layout_xml) == normalize(expected)


def test_m_file():
    m_text, _ = outputs()
    expected = EXPECTED_M.read_text()
    assert normalize(m_text) == normalize(expected)
