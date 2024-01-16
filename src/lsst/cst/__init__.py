"""Rubin LSST Community Science Tools"""

import logging

from importlib.metadata import PackageNotFoundError, version


logger = logging.getLogger("lsst.cst")
logger.setLevel(logging.WARNING)


def set_log_level(level: int = logging.ERROR):
    """Initialize package logging

    Parameters
    ----------
    level: `int`, Optional
        logging level, should be one of next values:
            logging.CRITICAL
            logging.ERROR -> default level value
            logging.WARNING
            logging.INFO
            logging.DEBUG
    """
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
