"""
Golden test for the minimal_datepicker exemplar.
Covers: DatePicker livecontrol → DatePicker component, DisplayFormat property
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/minimal_datepicker")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/minimal_datepicker.m"
EXPECTED_XML = GOLDEN_DIR / "expected/minimal_datepicker.xml"

GOLDEN_APP_ID = "9c0d1e2f-3a4b-5678-cdef-678901234567"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "minimal_datepicker"


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
