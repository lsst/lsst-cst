"""Rubin LSST Community Science Tools"""

import logging

from importlib.metadata import PackageNotFoundError, version


def initialize_log(level: int):
    logger = logging.getLogger("lsst.cst")
    logger.setLevel(level)


__version__: str
"""The version string of lsst
(PEP 440 / SemVer compatible).
"""


__all__ = ["__version__"]


try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
