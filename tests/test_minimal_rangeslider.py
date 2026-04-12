"""
Golden test for the minimal_rangeslider exemplar.
Covers: RangeSlider livecontrol → RangeSlider component, Value=[low high]
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/minimal_rangeslider")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/minimal_rangeslider.m"
EXPECTED_XML = GOLDEN_DIR / "expected/minimal_rangeslider.xml"

GOLDEN_APP_ID = "3c4d5e6f-7a8b-9012-cdef-012345678901"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "minimal_rangeslider"


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
