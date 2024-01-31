import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from astropy.visualization import AsinhStretch, ZScaleInterval
from astropy.coordinates import SkyCoord
from lsst.rsp import get_tap_service

__all__ = [
    "Collection",
    "Configuration",
    "CalExpData",
    "CalExpId",
    "Band",
    "CalExpDataFactory",
    "ButlerCalExpDataFactory",
]

_log = logging.getLogger(__name__)
_lsst_butler_ready = True

try:
    from lsst.daf.butler import Butler, DatasetExistence
except ImportError:
    _lsst_butler_ready = False
    _log.warning("Unable to import lsst.daf.butler")


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


class Band(Enum):
    """Exposure bands available."""

    i = "i"


@dataclass
class CalExpId:
    """Calexp information.

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
        """Plot image .

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
        return exp_sources.x, exp_sources.y

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


class ImageTransform(ABC):
    """Interface to make modifications on an image
    before rendering into a plot.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def transform(self, image_array: np.ndarray):
        """Transform an image executing a series of actions over it.

        Parameters
        ----------
        image_array: `np.array`
            Array to be transformed

        Return
        ------
        transformed_image_array: `np.array`
            Array modified after all transformation has been applied.
        """
        raise NotImplementedError


class NoImageTransform(ImageTransform):
    """No transformation class, mainly used when no transformation
    is wanted on the image array.
    """

    def __init__(self):
        super().__init__()

    def transform(self, image_array: np.ndarray) -> np.ndarray:
        """Do no transformation on image_array.

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
    fliped vertically and dynamic range will be reduced.
    """

    def __init__(self):
        super().__init__()
        self._transformation = [self._scale_image, self._flip_columns]

    def transform(self, image_array: np.ndarray) -> np.ndarray:
        """Transform an image executing vertical flip
        and dynamic range reduction.

        Parameters
        ----------
        image_array: `np.array`
            Array to be transformed.

        Returns
        -------
        transformed_image_array: `np.array`
            Array modified after all transformation has been applied.
        """
        for transformation_function in self._transformation:
            image_array = transformation_function(image_array)
        return image_array

    def _flip_columns(self, image_array: np.ndarray) -> None:
        """Flips vertically an image array.

        Parameters
        ----------
        image_array: `np.ndarray`
            Array to be vertically flip.

        Returns
        -------
        transformed_image_array: `np.array`
            Array vertically flipped.
        """
        return np.flipud(image_array)

    def _scale_image(self, image_array: np.ndarray) -> None:
        """Reduce dynamic range of an image array.

        Parameters
        ----------
        image_array: `np.ndarray`
            Array to reduce dynamic range.

        Returns
        -------
        transformed_image_array: `np.array`
            Array with dynamic range reduced
        """
        transform = AsinhStretch() + ZScaleInterval()
        return transform(image_array)


class ExposureData:

    def __init__(self, data: pd.Dataframe):
        self._data = data

    @property
    def data(self, frac: float = 1.0):
        if frac == 1.0:
            return self._data
        data = self._data.sample(frac=frac, axis='index')
        return data

    def get_data(self, frac: float = 1.0):
        if frac == 1.0:
            return self._data
        data = self._data.sample(frac=frac, axis='index')
        return data

    def index(self):
        self._data.columns.tolist()


class QueryExposureData(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def query(self):
        pass


class DataHandler(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def handle(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError()


class StandardDataHandler:

    def handle(self, data: pd.DataFrame):
        data['gmi'] = data['mag_g_cModel'] - data['mag_i_cModel']
        data['rmi'] = data['mag_r_cModel'] - data['mag_i_cModel']
        data['gmr'] = data['mag_g_cModel'] - data['mag_r_cModel']
        data['shape_type'] = data['r_extendedness'].map({0: 'point', 1: 'extended'})
        data['objectId'] = np.array(data['objectId']).astype('str')
        return data


class QueryTAPExposureData:
    _QUERY = "SELECT coord_ra, coord_dec, objectId, r_extendedness, "\
        "scisql_nanojanskyToAbMag(g_cModelFlux) AS mag_g_cModel, "\
        "scisql_nanojanskyToAbMag(r_cModelFlux) AS mag_r_cModel, "\
        "scisql_nanojanskyToAbMag(i_cModelFlux) AS mag_i_cModel "\
        "FROM dp02_dc2_catalogs.Object "\
        "WHERE CONTAINS(POINT('ICRS', coord_ra, coord_dec),"\
        "CIRCLE('ICRS', {} , {} , {} )) = 1 " \
        "AND detect_isPrimary = 1 "\
        "AND scisql_nanojanskyToAbMag(r_cModelFlux) < 27.0 "\
        "AND r_extendedness IS NOT NULL"

    def __init__(self, ra: np.float64, dec: np.float64, radius: np.float64):
        self._ra = ra
        self._dec = dec
        self._radius = radius
        self._query = QueryTAPExposureData._QUERY.format(ra, dec, radius)
        self._data = pd.DataFrame()
        self._data_handler = StandardDataHandler()

    def _set_data_handler(self, data_handler):
        self._data_handler = data_handler

    @classmethod
    def from_sky_coord(cls, coord: SkyCoord, radius: np.float64):
        """
        """
        return cls(coord.ra.value, coord.dec.value, radius)

    def __len__(self):
        return len(self._data)

    def has_data(self):
        """
        """
        return not self._data.empty

    def fetch(self):
        """"""
        data = self._launch_tap_fetch()
        self._data = self._data_handler.handle(data)

    def _launch_tap_fetch(self):
        # Helper function to launch tap query
        service = get_tap_service("tap")
        assert service is not None
        _log.info("Fetching Data")
        job = service.submit_job(self._query)
        job.run()
        job.wait(phases=['COMPLETED', 'ERROR'])
        self._check_status(job.phase)
        _log.info("Converting result to Dataframe")
        return job.fetch_result().to_table().to_pandas()

    def _check_status(self, job_state: str):
        # Helper function to check status
        if job_state == 'COMPLETED':
            _log.info("Job phase COMPLETED")
        elif job_state == 'ERROR':
            _log.error("Job phase finished with ERROR")
        else:
            _log.info(f"Job phase finished with status {job_state}")

    @property
    def query(self):
        """"""
        return self._query

    @property
    def data(self, frac: float = 1.0):
        assert self.has_data(), "Data is empty"
        return ExposureData(self._data)

    data_handler = property(None, _set_data_handler, None, None)
