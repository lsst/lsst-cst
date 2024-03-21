"""package initialize tools"""

import logging
from enum import Enum

import holoviews as hv

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


class Extension(Enum):
    """Available extensions"""

    BOKEH = "bokeh"


_extension_set = None  # type: Extension
_extension_available = [Extension.BOKEH]


def get_extension():
    """Return extension used by Holovies framework.

    Returns
    -------
    extension: `Extension``
        Holoviews package used extension.
    """
    return _extension_set


def _set_extension(extension: Extension = Extension.BOKEH):
    """Function to set the extension used
    by the holoviews module.
    (Nowadays only 'bokeh' extension is available).
    """
    global _extension_set
    if _extension_set is not None:
        raise Exception("Extension already set")
    if extension not in _extension_available:
        raise Exception(f"Unknown extension: {extension}")
    hv.extension(extension.value)
    _extension_set = extension


# Load the extension automatically


_set_extension()
