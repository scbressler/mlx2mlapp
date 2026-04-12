"""
Golden test for the minimal_editfieldtext exemplar.
Covers: EditField (text) livecontrol → EditField component, char vector value
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/minimal_editfieldtext")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/minimal_editfieldtext.m"
EXPECTED_XML = GOLDEN_DIR / "expected/minimal_editfieldtext.xml"

GOLDEN_APP_ID = "7a8b9c0d-1e2f-3456-abcd-456789012345"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "minimal_editfieldtext"


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
