"""
Golden test for the hide_code_button exemplar.
Covers: button section in hide_code view mode → Button + OutputTextArea only (no CodeTextArea).
"""
from pathlib import Path

from src.translate import translate

GOLDEN_DIR = Path("golden/hide_code_button")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/hide_code_button.m"
EXPECTED_XML = GOLDEN_DIR / "expected/hide_code_button.xml"

GOLDEN_APP_ID = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "hide_code_button"


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
