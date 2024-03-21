"""data science utilities for plotting data and images."""
import logging
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from lsst.cst.utilities.parameters import Band

_log = logging.getLogger(__name__)
_lsst_butler_ready = True
_lsst_stack_ready = True

try:
    from lsst.daf.butler import Butler, DatasetExistence
except ImportError:
    _lsst_butler_ready = False
    warnings.warn("Unable to import lsst.daf.butler")


__all__ = [
    "Collection",
    "Configuration",
    "CalExpData",
    "CalExpId",
    "CalExpDataFactory",
    "ButlerCalExpDataFactory",
]


class Collection(Enum):
    """Collections available:
    - i22: 2.2i/runs/DP0.2 .
    """

    i22 = "2.2i/runs/DP0.2"


class Configuration(Enum):
    """Butler configurations available
    - DP02: dp02.
    """

    DP02 = {"name": "dp02", "collections_available": [Collection.i22]}


@dataclass
class CalExpId:
    """Calexp information.

    Parameters
    ----------
    visit: `int`
    detector: `int`
    band: str | `Band`
    """

    def __init__(self, visit: int, detector: int, band: str | Band):
        self._visit = visit
        self._detector = detector
        self._band = Band(band) if isinstance(band, str) else band

    def as_dict(self):
        """Return CalExpId as a dictionary

        Returns
        -------
        cal_exp_id: `dict`
            CalExpId information as a dictionary
        """
        return {
            "visit": self._visit,
            "detector": self._detector,
            "band": self._band.value,
        }

    def __str__(self):
        return (
            f"visit: {self._visit}"
            f" detector: {self._detector}"
            f" band: {self._band.value}"
        )

    def __repr__(self):
        return self.__str__


class CalExpData(ABC):
    """Interface to get information from a Calexp."""

    @abstractmethod
    def get_image(self):
        """Exposition image .

        Returns
        -------
        calexp: `numpy.ndarray`
            Exposure data from calexp.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_sources(self):
        """Calexp sources.

        Returns
        -------
        sources: `pandas.DataFrame`
            Sources from the calexp.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_image_bounds(self):
        """Exposure Image bounds.

        Returns
        -------
        image_bounds: Tuple[int]
            Bounds of the cal_exp Exposure.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def cal_exp_id(self):
        """Exposure Identifier

        Returns
        -------
        exposure_id: `ExposureId`
            Information of the exposure.
        """
        raise NotImplementedError()


class CalExpDataFactory:
    """Interface for the CalExp Factories"""

    def __init__(self):
        super().__init__()

    def get_cal_exp_data(self, calexp_id: CalExpId):
        """Check for the exposure and returns a handler to
        get exposure information.

        Parameters
        ----------
        calexp_id: `CalExpId`
            CalExp information to search for.

        Raises
        ------
        ValueError:
            When the CalExp data could not be found.

        Returns
        -------
        exposure_data: `CalExpData`
            Instance of a CalExpData which can be used to obtain exposure data.
        """
        raise NotImplementedError()


class ButlerCalExpDataFactory(CalExpDataFactory):
    """Factory of calexp from a Butler.

    Parameters
    ----------
    configuration: `Configuration`
        Configuration available for a butler.
    collection: `Collection`
        Collection to be searched (in order) when reading datasets.
    """

    def __init__(self, configuration: Configuration, collection: Collection):
        super().__init__()
        if not _lsst_butler_ready:
            raise Exception("Unable to instantiate class ButlerCalExpData")
        _configuration = configuration.value
        if collection not in _configuration["collections_available"]:
            raise Exception(
                f"""Collection {collection} not compatible with configuration:
                            {_configuration['name']}"""
            )
        self._configuration = _configuration["name"]
        self._collection = collection.value
        self._butler = Butler(
            self._configuration, collections=self._collection
        )

    def get_cal_exp_data(self, calexp_id: CalExpId):
        """Check for the exposure in the Butler collection and returns
        a handler to get exposure information.

        Parameters
        ----------
        calexp_id: `CalExpId`
            CalExp information to search for.

        Raises
        ------
        ValueError
            When the Exposure could not be found inside the butler collection.

        Returns
        -------
        exposure_data: `CalExpData`
            Instance of a CalExpData which can be used to obtain exposure data.
        """
        if (
            self._butler.exists("calexp", calexp_id.as_dict())
            != DatasetExistence.RECORDED.VERIFIED
        ):
            raise ValueError(f"Unrecognized Exposure: {calexp_id}")
        return _ButlerCalExpData(self._butler, calexp_id)


class _ButlerCalExpData(CalExpData):
    """Wrap to retrieve information from an exposure,
    for example the calexp, the sources or the image bounds.
    """

    def __init__(self, butler: "Butler", calexp_id: CalExpId):
        super().__init__()
        self._calexp_id = calexp_id
        self._butler = butler
        self._calexp = None

    def _get_calexp(self):
        # Helper function that returns exposure calexp data.
        _log.debug(f"Getting CalExp from {self._calexp_id}")
        if self._calexp is None:
            self._calexp = self._butler.get(
                "calexp", dataId=self._calexp_id.as_dict()
            )
        _log.debug(f"Found CalExp {self._calexp_id}")
        return self._calexp

    def get_image(self):
        if self._calexp is None:
            self._get_calexp()
        return self._calexp.image.array

    def get_sources(self):
        _log.debug(f"Getting Sources from {self._calexp_id}")
        exp_sources = self._butler.get(
            "sourceTable", dataId=self._calexp_id.as_dict()
        )
        _log.debug(f"Found Sources from {self._calexp_id}")
        return exp_sources

    def get_image_bounds(self):
        if self._calexp is None:
            self._get_calexp()
        return (
            0,
            0,
            self._calexp.getDimensions()[0],
            self._calexp.getDimensions()[1],
        )

    @property
    def cal_exp_id(self):
        return str(self._calexp_id)

    def __str__(self):
        return f"""Butler exposure data {self._exposure_id}"""

    def __repr__(self):
        return self.__str__()
