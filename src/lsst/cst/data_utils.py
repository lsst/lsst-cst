import numpy as np
import logging
from astropy.visualization import AsinhStretch, ZScaleInterval
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


_log = logging.getLogger(__name__)
_lsst_butler_ready = True

try:
    from lsst.daf.butler import Butler, DatasetExistence
except ImportError:
    _lsst_butler_ready = False
    _log.warning("Unable to import lsst.daf.butler")


class Collection(Enum):
    """Collections available:
        - i22: 2.2i/runs/DP0.2
    """
    i22 = '2.2i/runs/DP0.2'


class Configuration(Enum):
    """ Butler configurations available
        - DP02: dp02
    """
    DP02 = {'name': 'dp02', 'collections_available': [Collection.i22]}


class Band(Enum):
    """Exposure bands available"""
    i = 'i'


@dataclass
class CalExpId:
    """Calexp information

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
    """Interface to get information from a Calexp
    """

    @abstractmethod
    def get_calexp(self, calexp_id: CalExpId):
        """
        Exposure calexp data

        Returns
        -------
        calexp: `ExposureF`
            Exposure data from calexp
        """
        raise NotImplementedError()

    @abstractmethod
    def get_sources(self, calexp_id: CalExpId):
        """Calexp sources
        
        Returns
        -------
        sources: `pandas.DataFrame`
            Sources from the calexp
        """
        raise NotImplementedError()

    @abstractmethod
    def get_image_bounds(self):
        """Exposure Image bounds

        Returns
        -------
        image_bounds: `tuple[float]`
            Bounds of the cal exp image
        """
        raise NotImplementedError()


class ButlerExposureFactory:
    """Factory of calexp from a Butler

    Parameters
    ----------
    configuration: `Configuration`
        Configuration available for a butler
    collection: `Collection``
        Collection to be searched (in order) when reading datasets.
    """
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

    def get_exposure(self, calexp_id: CalExpId):
        """Using the exposure_id argument check for the exposure using butler
        and returns a handler to get information from that exposure

        Parameters
        ----------
        exposure_id: `ExposureId`
            Exposure information to search for

        Raises
        ------
        ValueError: 
            When the Exposure could not be found inside the butler collection
        Returns
        -------
        exposure_data: `CalExpData`
            Instance of a CalExpData which can be used to obtain exposure data
        """
        if self._butler.exists('calexp', calexp_id.as_dict() == DatasetExistence.RECORDED.VERIFIED):
            raise ValueError(f"Unrecognized Exposure: {calexp_id}")
        return _ButlerCalExpData(self._butler, calexp_id)


class _ButlerCalExpData(CalExpData):
    """Wrapp class to retrieve information from an exposure,
       for example the calexp, the sources or the image bounds
    """
    def __init__(self, butler: Butler, calexp_id: CalExpId):
        super().__init__()
        self._calexp_id = calexp_id
        self._butler = butler
        self._calexp = None

    def get_calexp(self):
        """
        Exposure calexp data

        Returns
        -------
        calexp: `ExposureF`
            Exposure data from calexp
        """
        _log.debug(f"Getting CalExp from {self._calexp_id}")
        if self._calexp is None:
            self._calexp = self._butler.get('calexp', dataId=self._calexp_id.as_dict())
        _log.debug(f"Found CalExp {self._calexp_id}")
        return self._calexp

    def get_sources(self):
        """Calexp sources

        Returns
        -------
        sources: `pandas.DataFrame`
            Sources from the calexp
        """
        _log.debug(f"Getting Sources from {self._calexp_id}")
        exp_sources = self._butler.get('sourceTable', dataId=self._calexp_id.as_dict())
        _log.debug(f"Found Sources from {self._calexp_id}")
        return exp_sources.x, exp_sources.y

    def get_image_bounds(self):
        """Exposure Image bounds

        Returns
        -------
        image_bounds: `tuple[float]`
            Bounds of the cal exp image
        """
        if self._calexp is None:
            self.get_calexp()
        return (0, 0, self._calexp.getDimensions()[0], self._calexp.getDimensions()[1])

    @property
    def cal_exp_id(self):
        """Exposure Identifier

        Returns
        -------
        exposure_id: `ExposureId`
            Information of the exposure
        """
        return str(self._calexp_id)

    def __str__(self):
        return f'''Butler exposure data {self._exposure_id}'''

    def __repr__(self):
        return self.__str__()


class ImageTransform(ABC):
    """Interface to make modifications on an image before rendering into a plot
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def transform(self, image_array: np.ndarray):
        """Transform an image executing a series of actions over it

        Parameters
        ----------
        image_array: `np.array`
            Array to be transformed
        
        Return
        ------
        transformed_image_array: `np.array`
            Array modified after all transformation has been applied
        """
        raise NotImplementedError


class NoImageTransform(ImageTransform):
    """No transformation class, mainly used when no transformation
    is wanted on the image array
    """
    def __init__(self):
        super().__init__()

    def transform(self, image_array: np.ndarray) -> np.ndarray:
        """Do no transformation on image_array

        Parameters
        ----------
        image_array: `np.ndarray`
            array to no transform

        Returns
        -------
        image_array: `np.array`
            Same array passaed as argument
        """
        return image_array


class StandardImageTransform(ImageTransform):
    """Standard Image modificacions. When executing transform the image will be
    fliped vertically and dynamic range will be reduced
    """
    def __init__(self):
        super().__init__()
        self._transformation = [self._scale_image, self._flip_columns]

    def transform(self, image_array: np.ndarray) -> np.ndarray:
        """Transform an image executing vertical flip
        and dynamic range reduction

        Parameters
        ----------
        image_array: `np.array`
            Array to be transformed
        
        Returns
        ------
        transformed_image_array: `np.array`
            Array modified after all transformation has been applied
        """
        for transformation_function in self._transformation:
            image_array = transformation_function(image_array)
        return image_array

    def _flip_columns(self, image_array: np.ndarray) -> None:
        """Flips vertically an image array

        Parameters
        ----------
        image_array: `np.ndarray`
            Array to be vertically flip

        Returns
        -------
        transformed_image_array: `np.array`
            Array vertically flipped
        """
        return np.flipud(image_array)

    def _scale_image(self, image_array: np.ndarray) -> None:
        """Reduce dynamic range of an image array

        Parameters
        ----------
        image_array: `np.ndarray`
            Array to reduce dynamic range

        Returns
        -------
        transformed_image_array: `np.array`
            Array with dynamic range reduced
        """
        transform = AsinhStretch() + ZScaleInterval()
        return transform(image_array)
