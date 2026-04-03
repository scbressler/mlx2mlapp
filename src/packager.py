"""
packager.py — Assemble a .mlapp ZIP archive from a classdef string.

The .mlapp format follows Open Packaging Conventions (OPC / ECMA-376):

  [Content_Types].xml          — MIME types for each part
  _rels/.rels                  — top-level relationships
  matlab/document.xml          — classdef code wrapped in OOXML
  appdesigner/appModel.mat     — binary UI model
  metadata/appMetadata.xml     — app UUID, version, type
  metadata/coreProperties.xml  — OPC standard properties (title, dates)
  metadata/mwcoreProperties.xml            — MathWorks content type
  metadata/mwcorePropertiesExtension.xml   — second UUID
  metadata/mwcorePropertiesReleaseInfo.xml — MATLAB version info

appModel.mat — two-part problem
--------------------------------
The .mat file stores the UI model in two sections:

  code.ClassName / EditableSectionCode / Callbacks / StartupCallback
      Text fields that App Designer uses to display the Code View.
      We CAN write these from Python using scipy.io.

  components.UIFigure
      A MATLAB MCOS (binary object serialisation) blob encoding the full
      visual component tree.  We CANNOT construct this from Python without
      MATLAB.  When App Designer opens the file it reads components.UIFigure
      as the authoritative UI model and regenerates the classdef from it —
      overwriting document.xml if the two are out of sync.

Strategy
--------
We patch the text-based code.* fields in a *template* appModel.mat so
that App Designer's Code View shows our classdef.  The components.UIFigure
blob is carried over from the template unchanged, so the design canvas
may look different from the generated code until a proper template is
supplied.

For MATLAB Compiler / WebApp Server the compiler reads document.xml
directly — it does NOT go through App Designer's model.  So the output
is always correct for deployment even when the design view looks wrong.

Supplying a proper template
---------------------------
To get a design view that matches the generated UI:
  1. In MATLAB: App Designer → New → Blank App → save as blank_template.mlapp
  2. Pass its path via the template_mat parameter (or --template-mat CLI flag).
  A blank template has only a UIFigure on the canvas; App Designer will
  honour our classdef's createComponents() for the runtime component layout.
"""

from __future__ import annotations

import io
import os
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Path to the templates directory (sibling of this file)
_TEMPLATES_DIR = Path(__file__).parent / "templates"

# Path to the reference .mat used as a fallback template
_REFERENCE_MAT = (
    Path(__file__).parent.parent
    / "reference"
    / "SimpleMLApp_unpacked"
    / "appdesigner"
    / "appModel.mat"
)

# MATLAB release metadata for the generated app
_DEFAULT_RELEASE = "R2025b"
_DEFAULT_VERSION = "25.2.0.3042426"
_DEFAULT_RELEASE_DATE = "Oct 03 2025"
_DEFAULT_CHECKSUM = "3600278938"


def pack(
    classdef: str,
    output_path: str,
    app_name: str = "GeneratedApp",
    matlab_release: str = _DEFAULT_RELEASE,
    template_mat: str | None = None,
) -> None:
    """
    Write a valid .mlapp ZIP to *output_path*.

    Parameters
    ----------
    classdef:
        The complete App Designer classdef string.
    output_path:
        Destination path for the .mlapp file.
    app_name:
        Human-readable app name used in metadata.
    matlab_release:
        Target MATLAB release string, e.g. ``'R2025b'``.
    template_mat:
        Optional path to a template appModel.mat extracted from any
        .mlapp file.  The code.* text fields in the template are patched
        with values derived from *classdef*; the components.UIFigure blob
        is carried over unchanged.  When None the bundled reference mat
        (SimpleMLApp) is used.  For best App Designer design-view
        compatibility supply a blank App Designer template (New → Blank App).
    """
    jenv = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    app_uuid      = str(uuid.uuid4())
    ext_uuid      = str(uuid.uuid4())

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:

        # ── matlab/document.xml ──────────────────────────────────────────
        tmpl = jenv.get_template("document_xml.j2")
        zf.writestr("matlab/document.xml", tmpl.render(classdef=classdef))

        # ── appdesigner/appModel.mat ─────────────────────────────────────
        mat_source = Path(template_mat) if template_mat else _REFERENCE_MAT
        if mat_source.exists():
            patched = _patch_appmodel_mat(mat_source, classdef, app_name)
            zf.writestr("appdesigner/appModel.mat", patched)
        else:
            # No template available — write empty placeholder.
            # MATLAB Compiler still works; App Designer design view will not.
            zf.writestr("appdesigner/appModel.mat", b"")

        # ── metadata/appMetadata.xml ─────────────────────────────────────
        zf.writestr(
            "metadata/appMetadata.xml",
            _app_metadata_xml(app_uuid),
        )

        # ── metadata/coreProperties.xml ──────────────────────────────────
        zf.writestr(
            "metadata/coreProperties.xml",
            _core_properties_xml(app_name, ts),
        )

        # ── metadata/mwcoreProperties.xml ────────────────────────────────
        zf.writestr(
            "metadata/mwcoreProperties.xml",
            _mw_core_properties_xml(matlab_release),
        )

        # ── metadata/mwcorePropertiesExtension.xml ───────────────────────
        zf.writestr(
            "metadata/mwcorePropertiesExtension.xml",
            _mw_core_properties_ext_xml(ext_uuid),
        )

        # ── metadata/mwcorePropertiesReleaseInfo.xml ─────────────────────
        zf.writestr(
            "metadata/mwcorePropertiesReleaseInfo.xml",
            _mw_release_info_xml(matlab_release),
        )

        # ── [Content_Types].xml ──────────────────────────────────────────
        content_types = (_TEMPLATES_DIR / "content_types.xml").read_text(encoding="utf-8")
        zf.writestr("[Content_Types].xml", content_types)

        # ── _rels/.rels ──────────────────────────────────────────────────
        rels = (_TEMPLATES_DIR / "rels.xml").read_text(encoding="utf-8")
        zf.writestr("_rels/.rels", rels)

    Path(output_path).write_bytes(buf.getvalue())


# ---------------------------------------------------------------------------
# appModel.mat patching
# ---------------------------------------------------------------------------

def _patch_appmodel_mat(
    source_mat: Path,
    classdef: str,
    app_name: str,
) -> bytes:
    """
    Return the appModel.mat bytes to embed in the output .mlapp.

    The mat file uses zlib-compressed data elements (miCOMPRESSED) that
    contain MATLAB MCOS binary objects (components.UIFigure).  scipy's
    savemat writes elements back uncompressed and silently drops MCOS
    object data, corrupting the file and causing MATLAB to error on open.

    The only safe option from Python is to pass the source bytes through
    unchanged.  The template's appModel.mat is therefore copied verbatim:

    - Blank template: App Designer opens with an empty canvas (correct)
      and blank Code View (acceptable; MATLAB Compiler always reads
      document.xml directly and is unaffected).
    - Reference template (SimpleMLApp): App Designer shows SimpleMLApp's
      canvas, but MATLAB Compiler still reads our classdef correctly.

    Future work: implement compressed-element-level binary patching to
    update code.ClassName and code.* fields without touching the MCOS
    blob, or use a MATLAB script to regenerate appModel.mat from the
    classdef.
    """
    return source_mat.read_bytes()




# ---------------------------------------------------------------------------
# XML generators
# ---------------------------------------------------------------------------

def _app_metadata_xml(app_uuid: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
        '<metadata xmlns="http://schemas.mathworks.com/appDesigner/app/2017/appMetadata">'
        "<description></description>"
        "<MLAPPVersion>2</MLAPPVersion>"
        "<minimumSupportedMATLABRelease>R2018a</minimumSupportedMATLABRelease>"
        "<screenshotMode>auto</screenshotMode>"
        f"<uuid>{app_uuid}</uuid>"
        "<AppType>Standard</AppType>"
        "<componentProducts/>"
        "<imageRelativePaths/>"
        "<userComponents/>"
        "</metadata>"
    )


def _core_properties_xml(app_name: str, timestamp: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
        '<cp:coreProperties'
        ' xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
        ' xmlns:dcmitype="http://purl.org/dc/dcmitype/"'
        ' xmlns:dcterms="http://purl.org/dc/terms/"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>'
        "<dc:creator></dc:creator>"
        "<dc:description></dc:description>"
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>'
        f"<dc:title>{app_name}</dc:title>"
        "<cp:version>1.0</cp:version>"
        "</cp:coreProperties>"
    )


def _mw_core_properties_xml(release: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
        '<mwcoreProperties xmlns="http://schemas.mathworks.com/package/2012/coreProperties">\n'
        "  <contentType>application/vnd.mathworks.matlab.app</contentType>\n"
        "  <contentTypeFriendlyName>MATLAB App</contentTypeFriendlyName>\n"
        f"  <matlabRelease>{release}</matlabRelease>\n"
        "</mwcoreProperties>\n"
    )


def _mw_core_properties_ext_xml(ext_uuid: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
        '<mwcoreProperties xmlns="http://schemas.mathworks.com/package/2014/corePropertiesExtension">\n'
        f"  <uuid>{ext_uuid}</uuid>\n"
        "</mwcoreProperties>\n"
    )


def _mw_release_info_xml(release: str) -> str:
    # Use fixed version metadata matching the reference; this is informational only.
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<!-- Version information for MathWorks {release} Release -->\n"
        "<MathWorks_version_info>\n"
        f"  <version>{_DEFAULT_VERSION}</version>\n"
        f"  <release>{release}</release>\n"
        f"  <description>Update 1</description>\n"
        f"  <date>{_DEFAULT_RELEASE_DATE}</date>\n"
        f"  <checksum>{_DEFAULT_CHECKSUM}</checksum>\n"
        "</MathWorks_version_info>\n"
    )
