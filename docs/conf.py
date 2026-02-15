# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
project = 'OpenRig'
copyright = '2026, Iván Cuenca Ruiz & Luis de Campos'
author = 'Iván Cuenca Ruiz & Luis de Campos'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Core library for html generation from docstrings
    'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',     # Add links to highlighted source code
    'sphinx.ext.githubpages',  # Create .nojekyll file to publish the doc on GitHub Pages
    'myst_parser',             # Support for Markdown files (.md)
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Read the Docs theme
html_static_path = ['_static']

# -- Options for Napoleon (Google Style Docstrings) --------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for Autodoc -----------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# -- Auto-generate API documentation -----------------------------------------
def run_apidoc(_):
    """Runs sphinx-apidoc automatically when building docs."""
    from sphinx.ext.apidoc import main
    
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    output_path = cur_dir
    module_path = os.path.abspath(os.path.join(cur_dir, '..', 'src', 'openrig'))
    
    # -f: Force overwrite (so it updates with new files)
    # -e: Put each module on its own page (cleaner structure)
    # -M: Put module documentation before submodule documentation
    main(['-f', '-e', '-M', '-o', output_path, module_path])

def setup(app):
    app.connect('builder-inited', run_apidoc)
