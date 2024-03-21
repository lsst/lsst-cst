"""Rubin LSST Community Science Tools"""

from importlib.metadata import PackageNotFoundError, version

from .tools import set_log_level

__all__ = ["__version__", "set_log_level"]


__version__: str
"""The version string of lsst
(PEP 440 / SemVer compatible).
"""

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "1.0.0"
