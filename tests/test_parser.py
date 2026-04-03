"""Tests for src/parser.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.parser import parse, _parse_xml, _infer_variable, _strip_matlab_string

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_MLX = os.path.join(os.path.dirname(__file__), "sample_inputs", "hello_world.mlx")

MINIMAL_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
  <w:p>
    <w:pPr><w:pStyle w:val="heading"/></w:pPr>
    <w:r><w:t>My Heading</w:t></w:r>
  </w:p>
  <w:p>
    <w:pPr><w:pStyle w:val="text"/></w:pPr>
    <w:r><w:t>Some descriptive text.</w:t></w:r>
  </w:p>
  <w:p>
    <w:pPr><w:pStyle w:val="code"/></w:pPr>
    <w:r><w:t><![CDATA[x = 42;
y = x * 2;
]]></w:t></w:r>
  </w:p>
</w:body>
</w:document>
"""

SECTION_BREAK_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
  <w:p>
    <w:pPr><w:pStyle w:val="code"/></w:pPr>
    <w:r><w:t><![CDATA[a = 1;]]></w:t></w:r>
  </w:p>
  <w:p><w:pPr><w:sectPr/></w:pPr></w:p>
  <w:p>
    <w:pPr><w:pStyle w:val="code"/></w:pPr>
    <w:r><w:t><![CDATA[b = 2;]]></w:t></w:r>
  </w:p>
</w:body>
</w:document>
"""

CONTROL_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<w:document
  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
<w:body>
  <w:p>
    <w:pPr><w:pStyle w:val="code"/></w:pPr>
    <w:r><w:t><![CDATA[freq = 100;
amp = 0.5;
]]></w:t></w:r>
    <mc:AlternateContent>
      <mc:Choice Requires="R2018a">
        <w:customXml w:element="livecontrol">
          <w:customXmlPr>
            <w:attr w:name="context" w:val="{&quot;data&quot;:{&quot;text&quot;:&quot;Frequency&quot;,&quot;value&quot;:100,&quot;minimum&quot;:1,&quot;maximum&quot;:500,&quot;step&quot;:10,&quot;defaultValue&quot;:100},&quot;type&quot;:&quot;slider&quot;}"/>
            <w:attr w:name="startOffsetLine" w:val="0"/>
            <w:attr w:name="startColumn" w:val="7"/>
            <w:attr w:name="endColumn" w:val="10"/>
          </w:customXmlPr>
        </w:customXml>
      </mc:Choice>
      <mc:Fallback/>
    </mc:AlternateContent>
    <mc:AlternateContent>
      <mc:Choice Requires="R2018a">
        <w:customXml w:element="livecontrol">
          <w:customXmlPr>
            <w:attr w:name="context" w:val="{&quot;data&quot;:{&quot;text&quot;:&quot;Amplitude&quot;,&quot;value&quot;:0.5,&quot;minimum&quot;:0,&quot;maximum&quot;:1,&quot;step&quot;:0.1,&quot;defaultValue&quot;:0.5},&quot;type&quot;:&quot;slider&quot;}"/>
            <w:attr w:name="startOffsetLine" w:val="1"/>
            <w:attr w:name="startColumn" w:val="6"/>
            <w:attr w:name="endColumn" w:val="9"/>
          </w:customXmlPr>
        </w:customXml>
      </mc:Choice>
      <mc:Fallback/>
    </mc:AlternateContent>
  </w:p>
</w:body>
</w:document>
"""

COMBOBOX_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<w:document
  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
<w:body>
  <w:p>
    <w:pPr><w:pStyle w:val="code"/></w:pPr>
    <w:r><w:t><![CDATA[mode = "fast";
]]></w:t></w:r>
    <mc:AlternateContent>
      <mc:Choice Requires="R2018a">
        <w:customXml w:element="livecontrol">
          <w:customXmlPr>
            <w:attr w:name="context" w:val="{&quot;data&quot;:{&quot;text&quot;:&quot;Mode&quot;,&quot;value&quot;:&quot;\\&quot;fast\\&quot;&quot;,&quot;items&quot;:[{&quot;label&quot;:&quot;fast&quot;,&quot;value&quot;:&quot;\\&quot;fast\\&quot;&quot;},{&quot;label&quot;:&quot;slow&quot;,&quot;value&quot;:&quot;\\&quot;slow\\&quot;&quot;}],&quot;itemLabels&quot;:[&quot;fast&quot;,&quot;slow&quot;],&quot;defaultValue&quot;:&quot;\\&quot;fast\\&quot;&quot;},&quot;type&quot;:&quot;comboBox&quot;}"/>
            <w:attr w:name="startOffsetLine" w:val="0"/>
            <w:attr w:name="startColumn" w:val="7"/>
            <w:attr w:name="endColumn" w:val="13"/>
          </w:customXmlPr>
        </w:customXml>
      </mc:Choice>
      <mc:Fallback/>
    </mc:AlternateContent>
  </w:p>
</w:body>
</w:document>
"""


# ---------------------------------------------------------------------------
# Tests: basic paragraph styles
# ---------------------------------------------------------------------------

class TestBasicParagraphs:

    def test_heading_parsed(self):
        ls = _parse_xml(MINIMAL_XML)
        assert len(ls.sections) == 1
        assert ls.sections[0].heading == "My Heading"

    def test_text_block_parsed(self):
        ls = _parse_xml(MINIMAL_XML)
        assert "Some descriptive text." in ls.sections[0].text_blocks

    def test_code_block_parsed(self):
        ls = _parse_xml(MINIMAL_XML)
        code = ls.sections[0].code
        assert "x = 42;" in code
        assert "y = x * 2;" in code

    def test_empty_document_returns_empty_livescript(self):
        xml = b'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>'
        ls = _parse_xml(xml)
        assert ls.sections == []


# ---------------------------------------------------------------------------
# Tests: section breaks
# ---------------------------------------------------------------------------

class TestSectionBreaks:

    def test_section_break_splits_into_two_sections(self):
        ls = _parse_xml(SECTION_BREAK_XML)
        assert len(ls.sections) == 2

    def test_each_section_has_correct_code(self):
        ls = _parse_xml(SECTION_BREAK_XML)
        assert "a = 1;" in ls.sections[0].code
        assert "b = 2;" in ls.sections[1].code


# ---------------------------------------------------------------------------
# Tests: slider controls
# ---------------------------------------------------------------------------

class TestSliderControls:

    def setup_method(self):
        self.ls = _parse_xml(CONTROL_XML)

    def test_two_controls_detected(self):
        assert len(self.ls.all_controls) == 2

    def test_first_control_is_slider(self):
        c = self.ls.all_controls[0]
        assert c.type == "slider"

    def test_first_control_variable_inferred(self):
        c = self.ls.all_controls[0]
        assert c.variable == "freq"

    def test_first_control_range(self):
        c = self.ls.all_controls[0]
        assert c.min == 1
        assert c.max == 500
        assert c.step == 10

    def test_first_control_label(self):
        c = self.ls.all_controls[0]
        assert c.label == "Frequency"

    def test_second_control_variable(self):
        c = self.ls.all_controls[1]
        assert c.variable == "amp"

    def test_second_control_default(self):
        c = self.ls.all_controls[1]
        assert c.default == 0.5


# ---------------------------------------------------------------------------
# Tests: comboBox controls
# ---------------------------------------------------------------------------

class TestComboBoxControls:

    def setup_method(self):
        self.ls = _parse_xml(COMBOBOX_XML)

    def test_combobox_detected(self):
        assert len(self.ls.all_controls) == 1
        assert self.ls.all_controls[0].type == "comboBox"

    def test_combobox_variable(self):
        assert self.ls.all_controls[0].variable == "mode"

    def test_combobox_items(self):
        c = self.ls.all_controls[0]
        assert c.item_labels == ["fast", "slow"]


# ---------------------------------------------------------------------------
# Tests: sample .mlx fixture
# ---------------------------------------------------------------------------

class TestSampleMLX:

    @pytest.fixture(autouse=True)
    def skip_if_missing(self):
        if not os.path.exists(SAMPLE_MLX):
            pytest.skip("hello_world.mlx fixture not found")

    def test_parse_returns_livescript(self):
        ls = parse(SAMPLE_MLX)
        assert ls is not None

    def test_has_at_least_one_section(self):
        ls = parse(SAMPLE_MLX)
        assert len(ls.sections) >= 1

    def test_has_controls(self):
        ls = parse(SAMPLE_MLX)
        assert len(ls.all_controls) >= 1

    def test_has_slider_and_combobox(self):
        ls = parse(SAMPLE_MLX)
        types = {c.type for c in ls.all_controls}
        assert "slider" in types
        assert "comboBox" in types


# ---------------------------------------------------------------------------
# Tests: helper functions
# ---------------------------------------------------------------------------

class TestHelpers:

    def test_infer_variable_simple_assignment(self):
        assert _infer_variable(["freq = 100;", "amp = 0.5;"], 0, 7, 10) == "freq"

    def test_infer_variable_second_line(self):
        assert _infer_variable(["freq = 100;", "amp = 0.5;"], 1, 6, 9) == "amp"

    def test_infer_variable_out_of_range_returns_fallback(self):
        result = _infer_variable([], 5, 0, 0)
        assert result == "var5"

    def test_strip_matlab_string_removes_quotes(self):
        assert _strip_matlab_string('"hello"') == "hello"

    def test_strip_matlab_string_no_quotes(self):
        assert _strip_matlab_string("hello") == "hello"

    def test_strip_matlab_string_empty(self):
        assert _strip_matlab_string("") == ""
