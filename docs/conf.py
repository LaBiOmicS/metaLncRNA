import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'metaLncRNA'
copyright = '2026, metaLncRNA Team'
author = 'metaLncRNA Team'
release = '1.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

html_theme = 'sphinx_rtd_theme'
