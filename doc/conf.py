# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import re
import sys
import textwrap
from pathlib import Path
import mlx.traceability

ZEPHYR_BASE = Path(os.getenv("ZEPHYR_BASE"))
DOC_BASE = Path(__file__).resolve().parents[1]
ZEPHYR_BUILD = Path(os.environ.get("OUTPUT_DIR")).resolve()

# Add the '_extensions' directory to sys.path, to enable finding Sphinx
# extensions within.
sys.path.insert(0, str(ZEPHYR_BASE / "doc" / "_extensions"))

project = 'Zephyr'
copyright = '2025, Zephyr Project Contributors'
author = 'Zephyr Project Contributors'
release = '1.0'


# parse version from 'VERSION' file
with open(ZEPHYR_BASE / "VERSION") as f:
    m = re.match(
        (
            r"^VERSION_MAJOR\s*=\s*(\d+)$\n"
            + r"^VERSION_MINOR\s*=\s*(\d+)$\n"
            + r"^PATCHLEVEL\s*=\s*(\d+)$\n"
            + r"^VERSION_TWEAK\s*=\s*\d+$\n"
            + r"^EXTRAVERSION\s*=\s*(.*)$"
        ),
        f.read(),
        re.MULTILINE,
    )

    if not m:
        sys.stderr.write("Warning: Could not extract kernel version\n")
        version = "Unknown"
    else:
        major, minor, patch, extra = m.groups(1)
        version = ".".join((major, minor, patch))
        if extra:
            version += "-" + extra

release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# parse SDK version from 'SDK_VERSION' file
with open(ZEPHYR_BASE / "SDK_VERSION") as f:
    sdk_version = f.read().strip()

SDK_URL_BASE="https://github.com/zephyrproject-rtos/sdk-ng/releases/download"

extensions = [
    "sphinx_rtd_theme",
    "zephyr.gh_utils",
    "sphinx_tabs.tabs",
    "zephyr.kconfig",
    "zephyr.domain",
    "zephyr.application",
    "zephyr.link-roles",
    "zephyr.external_content",
    "zephyr.doxyrunner",
    "zephyr.doxybridge",
    "zephyr.doxytooltip",
    "mlx.traceability"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

external_content_contents = [
    (DOC_BASE / "doc", "[!_]*"),
]

rst_epilog = f"""
.. include:: /substitutions.txt

.. |sdk-version-literal| replace:: ``{sdk_version}``
.. |sdk-version-trim| unicode:: {sdk_version}
   :trim:
.. |sdk-version-ltrim| unicode:: {sdk_version}
   :ltrim:
.. _Zephyr SDK bundle: https://github.com/zephyrproject-rtos/sdk-ng/releases/tag/v{sdk_version}
.. |sdk-url-linux| replace::
   `{SDK_URL_BASE}/v{sdk_version}/zephyr-sdk-{sdk_version}_linux-x86_64.tar.xz`
.. |sdk-url-linux-sha| replace::
   `{SDK_URL_BASE}/v{sdk_version}/sha256.sum`
.. |sdk-url-macos| replace::
   `{SDK_URL_BASE}/v{sdk_version}/zephyr-sdk-{sdk_version}_macos-x86_64.tar.xz`
.. |sdk-url-macos-sha| replace::
   `{SDK_URL_BASE}/v{sdk_version}/sha256.sum`
.. |sdk-url-windows| replace::
   `{SDK_URL_BASE}/v{sdk_version}/zephyr-sdk-{sdk_version}_windows-x86_64.7z`
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": True,
    "prev_next_buttons_location": None,
    "navigation_depth": 5,
}
html_baseurl = "https://docs.zephyrproject.org/latest/"
html_title = "Zephyr Project Documentation"
html_logo = str(ZEPHYR_BASE / "doc" / "_static" / "images" / "logo.svg")
html_favicon = str(ZEPHYR_BASE / "doc" / "_static" / "images" / "favicon.png")
html_static_path = [str(DOC_BASE / "doc" / "_static")]
html_last_updated_fmt = "%b %d, %Y"
html_domain_indices = False
html_split_index = True
html_show_sourcelink = False
html_show_sphinx = False
html_search_scorer = str(DOC_BASE / "doc" / "_static" / "js" / "scorer.js")
html_static_path = ['_static']

def setup(app):
    # theme customizations
    app.add_css_file("css/custom.css")
    app.add_js_file("js/custom.js")



# -- Options for zephyr.doxyrunner plugin ---------------------------------

doxyrunner_doxygen = os.environ.get("DOXYGEN_EXECUTABLE", "doxygen")
doxyrunner_projects = {
    "zephyr": {
        "doxyfile": DOC_BASE / "doc" / "zephyr.doxyfile.in",
        "outdir": ZEPHYR_BUILD / "doxygen",
        "fmt": True,
        "fmt_vars": {
            "ZEPHYR_BASE": str(ZEPHYR_BASE),
            "ZEPHYR_VERSION": version,
            "DOC_BASE": str(DOC_BASE) + '/doc', 
        },
        "outdir_var": "DOXY_OUT",
    },
}

# -- Options for zephyr.doxybridge plugin ---------------------------------

doxybridge_projects = {"zephyr": doxyrunner_projects["zephyr"]["outdir"]}



traceability_relationships = {
    'trace': 'traced_by',
    'depends_on': 'impacts_on',
    'fulfills': 'fulfilled_by',
    'implements': 'implemented_by',
    'validates': 'validated_by',
    'ext_toolname': ''
}

traceability_render_relationship_per_item = True

traceability_relationship_to_string = {
    'trace': 'Traces',
    'traced_by': 'Traced by',
    'depends_on': 'Depends on',
    'impacts_on': 'Impacts on',
    'fulfills': 'Fulfills',
    'fulfilled_by': 'Fulfilled by',
    'implements': 'Implements',
    'implemented_by': 'Implemented by',
    'validates': 'Validates',
    'validated_by': 'Validated by',
    'ext_toolname': 'Reference to toolname'
}

traceability_attribute_to_string = {
    'rtype': 'Requirement type',
    'value': 'Value',
    'asil': 'ASIL',
    'status': 'Status',
    'uid': 'UID',
    'component': 'Component',
}

traceability_attributes = {
    'value': '^.*$',
    'asil': '^(QM|[ABCD])$',
    'status': '^.*$',
    'uid': '^.*$',
    'component': '^.*$',
    'rtype': '^(Functional|Non-Functional)$'
}

traceability_collapse_links = False

traceability_render_relationship_per_item = True
traceability_render_attributes_per_item = True


suppress_warnings = ["config.cache"]
