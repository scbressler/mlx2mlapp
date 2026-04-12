"""
Golden test for the multiple_sections exemplar.
Covers: two sections each with heading + body text + plot (UIAxes_1, UIAxes_2).
Canvas: 1440x1024. UIAxes height reduced to 300px when multiple plots present.
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/multiple_sections")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/multiple_sections.m"
EXPECTED_XML = GOLDEN_DIR / "expected/multiple_sections.xml"

GOLDEN_APP_ID = "d5e6f7a8-b9c0-1234-5678-901234567890"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "multiple_sections"


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
