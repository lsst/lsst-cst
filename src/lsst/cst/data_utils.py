import numpy as np
import logging
from astropy.visualization import AsinhStretch, ZScaleInterval
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


_log = logging.getLogger(__name__)
_lsst_butler_ready = True

try:
    from lsst.daf.butler import Butler
except ImportError:
    _lsst_butler_ready = False
    _log.warning("Unable to import lsst.daf.butler")


class Collection(Enum):
    """"""
    i22 = '2.2i/runs/DP0.2'


class Configuration(Enum):
    """"""
    DP02 = {'name': 'dp02', 'collections_available': [Collection.i22]}


class Band(Enum):
    """"""
    i = 'i'


@dataclass
class ExposureId:
    """Exposition information

    Parameters
    ----------
    visit: `int`
    detector: `int`
    band: `Band`
    """
    def __init__(self, visit: int, detector: int, band: Band):
        self._visit = visit
        self._detector = detector
        self._band = band

    def as_dict(self):
        """"""
        return {'visit': self._visit, 'detector': self._detector, 'band': self._band.value}

    def __str__(self):
        """"""
        return f"visit: {self._visit} detector: {self._detector} band: {self._band.value}"

    def __repr__(self):
        """"""
        return self.__str__


class CalExpData(ABC):
    """"""

    @abstractmethod
    def get_calexp(self, exposure_id: ExposureId):
        """"""
        raise NotImplementedError()

    @abstractmethod
    def get_sources(self, exposure_id: ExposureId):
        """"""
        raise NotImplementedError()


class ButlerExposureFactory:
    """"""
    def __init__(self, configuration: Configuration, collection: Collection):
        if not _lsst_butler_ready:
            raise Exception("Unable to instantiate class ButlerCalExpData")
        _configuration = configuration.value
        if collection not in _configuration['collections_available']:
            raise Exception(f'''Collection {collection} not compatible with configuration:
                            {_configuration['name']}''')
        self._configuration = _configuration['name']
        self._collection = collection.value
        self._butler = Butler(self._configuration, collections=self._collection)

    def get_exposure(self, exposure_id: ExposureId):
        return ButlerCalExpData(self._butler, exposure_id)


class ButlerCalExpData(CalExpData):
    """"""
    def __init__(self, butler: Butler, exposure_id: ExposureId):
        super().__init__()
        self._exposure_id = exposure_id
        self._butler = butler

    def get_calexp(self):
        """"""
        calexp = self._butler.get('calexp', dataId=self._exposure_id.as_dict())
        return calexp

    def get_sources(self):
        """"""
        exp_sources = self._butler.get('sourceTable', dataId=self._exposure_id.as_dict())
        return exp_sources

    @property
    def exposure_id(self):
        """.env"""
        return self._exposure_id

    def __str__(self):
        """"""
        return f'''Butler exposure data {self._exposure_id}.\
                Configuration: {self._configuration} collection: {self._collection}'''

    def __repr__(self):
        """"""
        return self.__str__()


def flip_columns(array: np.ndarray) -> np.array:
    """"""
    return np.flipup(array)


def scale_image(array: np.ndarray) -> np.array:
    """"""
    transform = AsinhStretch() + ZScaleInterval()
    scaled_image = transform(array)
    return scaled_image
