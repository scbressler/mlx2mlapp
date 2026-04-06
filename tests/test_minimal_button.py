"""
Golden test for the minimal_button exemplar.

Comparison strategy (per spec/normalization_rules.md):
- Strip trailing whitespace from each line before comparing.
- Internal metadata (AppId, release versions) is fixed to match the golden.
"""
from pathlib import Path

import pytest

from src.translate import translate

GOLDEN_DIR = Path("golden/minimal_button")
INPUT_XML = GOLDEN_DIR / "input/document.xml"
EXPECTED_M = GOLDEN_DIR / "expected/minimal_button.m"
EXPECTED_XML = GOLDEN_DIR / "expected/minimal_button.xml"

# Fixed values matching the golden file so output is deterministic.
GOLDEN_APP_ID = "598f11e1-95d1-4d6c-ad56-33eeae3af8f1"
GOLDEN_RELEASE = "R2025b"
GOLDEN_CLASS = "minimal_button"


def normalize(text: str) -> str:
    """Strip trailing whitespace from each line."""
    return "\n".join(line.rstrip() for line in text.splitlines())


@pytest.fixture(scope="module")
def outputs():
    m_text, layout_xml = translate(
        str(INPUT_XML),
        class_name=GOLDEN_CLASS,
        app_id=GOLDEN_APP_ID,
        release=GOLDEN_RELEASE,
    )
    return m_text, layout_xml


def test_layout_xml(outputs):
    _, layout_xml = outputs
    expected = EXPECTED_XML.read_text()
    assert normalize(layout_xml) == normalize(expected)


def test_m_file(outputs):
    m_text, _ = outputs
    expected = EXPECTED_M.read_text()
    assert normalize(m_text) == normalize(expected)
