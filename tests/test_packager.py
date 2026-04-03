"""Tests for src/packager.py"""

import sys
import os
import tempfile
import zipfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from lxml import etree

import scipy.io as sio
from src.packager import pack, _app_metadata_xml, _core_properties_xml, _REFERENCE_MAT


SAMPLE_CLASSDEF = """\
classdef TestApp < matlab.apps.AppBase

    properties (Access = public)
        UIFigure  matlab.ui.Figure
        UIAxes    matlab.ui.control.UIAxes
        RunButton matlab.ui.control.Button
    end

    properties (Access = private)
        freq
        amp
    end

    methods (Access = private)

        function startupFcn(app)
            app.freq = app.freqSlider.Value;
            runScript(app);
        end

        function runScript(app)
            freq = app.freqSlider.Value;
            t = 0:0.001:1;
            plot(app.UIAxes, t, sin(2*pi*freq*t));
        end

        function RunButtonPushed(app, event)
            runScript(app);
        end

    end

    methods (Access = public)
        function app = TestApp
            if nargout == 0; clear app; end
        end
        function delete(app)
            delete(app.UIFigure)
        end
    end
end
"""


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def mlapp_path(tmp_path):
    out = str(tmp_path / "test.mlapp")
    pack(SAMPLE_CLASSDEF, out, app_name="TestApp")
    return out


# ---------------------------------------------------------------------------
# Tests: ZIP structure
# ---------------------------------------------------------------------------

class TestZIPStructure:

    def test_output_is_valid_zip(self, mlapp_path):
        assert zipfile.is_zipfile(mlapp_path)

    def test_contains_document_xml(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            assert "matlab/document.xml" in zf.namelist()

    def test_contains_appmodel_mat(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            assert "appdesigner/appModel.mat" in zf.namelist()

    def test_contains_content_types(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            assert "[Content_Types].xml" in zf.namelist()

    def test_contains_rels(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            assert "_rels/.rels" in zf.namelist()

    def test_contains_all_metadata(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            names = zf.namelist()
        assert "metadata/appMetadata.xml" in names
        assert "metadata/coreProperties.xml" in names
        assert "metadata/mwcoreProperties.xml" in names
        assert "metadata/mwcorePropertiesExtension.xml" in names
        assert "metadata/mwcorePropertiesReleaseInfo.xml" in names


# ---------------------------------------------------------------------------
# Tests: document.xml content
# ---------------------------------------------------------------------------

class TestDocumentXML:

    def test_document_xml_is_valid_xml(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            data = zf.read("matlab/document.xml")
        root = etree.fromstring(data)
        assert root is not None

    def test_document_xml_contains_classdef(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            data = zf.read("matlab/document.xml").decode("utf-8")
        assert "classdef TestApp" in data

    def test_document_xml_has_code_style(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            data = zf.read("matlab/document.xml").decode("utf-8")
        assert 'w:val="code"' in data


# ---------------------------------------------------------------------------
# Tests: metadata XML content
# ---------------------------------------------------------------------------

class TestMetadataXML:

    def test_app_metadata_contains_uuid(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            data = zf.read("metadata/appMetadata.xml").decode("utf-8")
        assert "<uuid>" in data

    def test_app_metadata_version_2(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            data = zf.read("metadata/appMetadata.xml").decode("utf-8")
        assert "<MLAPPVersion>2</MLAPPVersion>" in data

    def test_core_properties_has_title(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            data = zf.read("metadata/coreProperties.xml").decode("utf-8")
        assert "<dc:title>TestApp</dc:title>" in data

    def test_mw_core_properties_has_release(self, mlapp_path):
        with zipfile.ZipFile(mlapp_path) as zf:
            data = zf.read("metadata/mwcoreProperties.xml").decode("utf-8")
        assert "<matlabRelease>R2025b</matlabRelease>" in data

    def test_custom_release_propagated(self, tmp_path):
        out = str(tmp_path / "r24.mlapp")
        pack(SAMPLE_CLASSDEF, out, app_name="TestApp", matlab_release="R2024b")
        with zipfile.ZipFile(out) as zf:
            data = zf.read("metadata/mwcoreProperties.xml").decode("utf-8")
        assert "<matlabRelease>R2024b</matlabRelease>" in data


# ---------------------------------------------------------------------------
# Tests: XML generators (unit)
# ---------------------------------------------------------------------------

class TestXMLGenerators:

    def test_app_metadata_xml_is_valid(self):
        import uuid
        xml = _app_metadata_xml(str(uuid.uuid4()))
        root = etree.fromstring(xml.encode())
        assert root is not None

    def test_core_properties_xml_is_valid(self):
        xml = _core_properties_xml("MyApp", "2026-01-01T00:00:00Z")
        root = etree.fromstring(xml.encode())
        assert root is not None


# ---------------------------------------------------------------------------
# Tests: round-trip via mlx2mlapp.convert
# ---------------------------------------------------------------------------

class TestRoundTrip:

    SAMPLE_MLX = os.path.join(os.path.dirname(__file__), "sample_inputs", "hello_world.mlx")

    def test_convert_produces_valid_mlapp(self, tmp_path):
        if not os.path.exists(self.SAMPLE_MLX):
            pytest.skip("hello_world.mlx not found")

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from mlx2mlapp import convert

        out = str(tmp_path / "hello_world.mlapp")
        convert(self.SAMPLE_MLX, out, app_name="HelloWorld", verbose=False)

        assert os.path.exists(out)
        assert zipfile.is_zipfile(out)

        with zipfile.ZipFile(out) as zf:
            doc = zf.read("matlab/document.xml").decode("utf-8")
        assert "classdef HelloWorld" in doc

    def test_convert_classdef_has_controls(self, tmp_path):
        if not os.path.exists(self.SAMPLE_MLX):
            pytest.skip("hello_world.mlx not found")

        from mlx2mlapp import convert
        out = str(tmp_path / "hello_world2.mlapp")
        convert(self.SAMPLE_MLX, out, app_name="HelloWorld", verbose=False)

        with zipfile.ZipFile(out) as zf:
            doc = zf.read("matlab/document.xml").decode("utf-8")

        # Should have at least one slider or dropdown
        assert "uislider" in doc or "uidropdown" in doc


# ---------------------------------------------------------------------------
# Tests: appModel.mat — verbatim copy (no scipy round-trip)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _REFERENCE_MAT.exists(), reason="reference appModel.mat not present")
class TestAppModelMat:

    def test_mat_bytes_are_unchanged(self, tmp_path):
        """pack() must copy appModel.mat verbatim — no scipy round-trip."""
        out = str(tmp_path / "verbatim.mlapp")
        pack(SAMPLE_CLASSDEF, out, app_name="TestApp")
        with zipfile.ZipFile(out) as zf:
            mat_bytes = zf.read("appdesigner/appModel.mat")
        original = _REFERENCE_MAT.read_bytes()
        assert mat_bytes == original

    def test_mat_still_parseable_by_scipy(self, tmp_path):
        """Verbatim bytes should still be readable by scipy."""
        import io as _io
        out = str(tmp_path / "parseable.mlapp")
        pack(SAMPLE_CLASSDEF, out, app_name="TestApp")
        with zipfile.ZipFile(out) as zf:
            mat_bytes = zf.read("appdesigner/appModel.mat")
        mat = sio.loadmat(_io.BytesIO(mat_bytes), struct_as_record=False, squeeze_me=True)
        assert "code" in mat
        assert "components" in mat

    def test_mat_components_uifigure_present(self, tmp_path):
        import io as _io
        out = str(tmp_path / "uifigure.mlapp")
        pack(SAMPLE_CLASSDEF, out, app_name="TestApp")
        with zipfile.ZipFile(out) as zf:
            mat_bytes = zf.read("appdesigner/appModel.mat")
        mat = sio.loadmat(_io.BytesIO(mat_bytes), struct_as_record=False, squeeze_me=True)
        assert "UIFigure" in mat["components"]._fieldnames
