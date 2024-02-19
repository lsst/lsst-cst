"""data science data tools."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import numpy as np
from astropy.visualization import AsinhStretch, ZScaleInterval
from lsst.cst.data.queries import Band, RaDecCoordinatesToTractPatch, TAPService
from lsst.geom import ExtendI

__all__ = [
    "Collection",
    "Configuration",
    "CalExpData",
    "CalExpId",
    "CalExpDataFactory",
    "ButlerCalExpDataFactory",
    "tract_patch_from_ra_dec"
]

_log = logging.getLogger(__name__)
_lsst_butler_ready = True

SIGMA_TO_FWHM = 2.0*np.sqrt(2.0*np.log(2.0))

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


def gauss(x, a, x0, sigma):
    # Helper function to define a one-dimensional Gaussian profile.
    return a*np.exp(-(x-x0)**2/(2*sigma**2))


@dataclass(frozen=True)
class PsfProperties:
    """Object with psf properties.

    Parameters
    ----------
    fwhm : `float`
        Full-width at half maximum: PSF determinant radius
        from SDSS adaptive moments matrix (sigma) times
        SIGMA_TO_FWHM.
    ap_flux : `float`
        PSF flux from aperture photometry weighted
        by a sinc function.
    peak : `float`
        Peak PSF value.
    dims : `lsst.geom.ExtendI`
        PSF postage stamp dimensions.
    """
    fwhm: float
    ap_flux: float
    peak: float
    dims: ExtendI


def get_psf_properties(psf, point):
    """Function to obtain PSF properties.

    Parameters
    ----------
    psf : `lsst.meas.extensions.psfex.PsfexPsf`
        PSF object.
    point : `lsst.geom.Point2D`
        Coordinate where the PSF is being evaluated.

    Returns
    -------
    psf_values: `PsfProperties`
        PsfProperties object containing psf properties:
        fhwm, ap_flux, peak and dims.
    """
    sigma = psf.computeShape(point).getDeterminantRadius()
    fwhm = sigma * SIGMA_TO_FWHM
    ap_flux = psf.computeApertureFlux(radius=sigma, position=point)
    peak = psf.computePeak(position=point)
    dims = psf.computeImage(point).getDimensions()

    print(f"PSF FWHM: {fwhm:.4} pix \n"
          f"PSF flux from aperture photometry: {ap_flux:.4} \n"
          f"Peak PSF value: {peak:.4} \n"
          f"PSF postage stamp dimensions: {dims} \n")

    return PsfProperties(sigma, ap_flux, peak, dims)


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


class TractPatchInformation:
    """Tract patch information

    Parameters
    ----------
    patch: `int`
        Patch value.
    tract: `int`
        Tract value.
    """
    def __init__(self, tract: int, patch: int):
        self._tract = tract
        self._patch = patch

    @property
    def patch(self):
        """Patch value.

        Returns
        -------
        patch: `int`
            Patch value.
        """
        return self._patch

    @property
    def tract(self):
        """Patch value.

        Returns
        -------
        tract: `int`
            Tract value.
        """
        return self._tract

    def to_dict(self):
        """Dictionary containing
        Tract-patch information

        Returns
        -------
        values: `dict[str, int]`
            Dictionary with tract-patch information.
        """
        return dict(tract=self._tract, patch=self._patch)

    def __str__(self):
        return f"tract: {self._tract} patch: {self._patch}"

    def __repr__(self):
        return str(self)


def tract_patch_from_ra_dec(ra: float, dec: float):
    """Look for nearest tract-patch information from a
    coordinate.

    Parameters
    ----------
    ra: `np.float64`
        Coordinate ascension.
    dec: `np.float64`
        Coordinate declination.

    Returns
    -------
    value: `TractPatchInformation`
        Tract patch information
    """
    tap_exposure_data = TAPService()
    query = RaDecCoordinatesToTractPatch(ra, dec)
    tap_exposure_data.query = query
    data = tap_exposure_data.fetch()
    final_data = data._data
    if final_data.empty:
        raise Exception(f"No tract-patch info found"
                        f"for ra: {ra} dec: {dec}")
    return TractPatchInformation(final_data["lsst_tract"].iloc[0],
                                 final_data["lsst_patch"].iloc[0])
