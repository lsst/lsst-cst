"""Rubin LSST Community Science Tools"""

from importlib.metadata import PackageNotFoundError, version

from .mpl_utils import remove_figure

__version__: str
"""The version string of lsst
(PEP 440 / SemVer compatible).
"""


__all__ = ["__version__", "remove_figure"]


try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
