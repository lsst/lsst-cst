"""data science format utils."""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from lsst.cst.utilities.image import CalExpId
from lsst.cst.utilities.queries import RaDecCoordinatesToTractPatch, TAPService

__all__ = [
    "data_id_to_str",
    "ids_to_str",
    "shuffle_dataframe",
    "sort_dataframe",
    "TractPatchInformation",
    "tract_patch_from_ra_dec",
    "get_psf_properties",
]


SIGMA_TO_FWHM = 2.0 * np.sqrt(2.0 * np.log(2.0))


def ids_to_str(data_ids: np.ndarray) -> str:
    """Transform a numpy array of ids (long int)
        to a comma-separated values string

    Parameters
    ----------
    data_ids: `numpy.ndarray`
        numpy array with objects id

    Returns
    -------
    result: `str`
        String with separated by comma-separated values
        from the data_ids
    """
    return "(" + ", ".join(str(value) for value in data_ids) + ")"


def data_id_to_str(data_id: dict):
    """Returns a data identifier dictionary to a string

    Parameters
    ----------
    data_id: 'dict'
        Data identifier dictionary.

    Returns
    -------
    data_id_str: `str`
        Data identifier string
    """
    cal_exp_id = CalExpId(**data_id)
    return str(cal_exp_id)


def sort_dataframe(
    df: pd.DataFrame,
    sort_key: str,
    ascending: bool = False,
    set_index: bool = True,
) -> pd.DataFrame:
    """Return a sorted copy of the dataframe 'df' by index,
    selecting the desired order (ascending or descending)
    using the ascending argument, it also exchanges the index
    of the dataframe for the sort_key if set_index parameter
    is True (default).

    Parameters
    ----------
    df : `pandas.DataFrame`
        dataframe to be sorted
    sort_key: `str`
        column key used to sort the dataframe
    ascending: `bool`, optional
        ascending/descending sorting
    set_index: `bool`, optional
        set sorted key as the dataframe index

    Returns
    -------
    result : `pandas.DataFrame`
        Copy of the `~pandas.DataFrame` sorted using the selected column.
    """
    if sort_key not in df.columns:
        raise Exception(f"Index {sort_key} not existing in the dataframe")
    df = df.sort_values(sort_key, ascending=ascending)
    if set_index:
        df.set_index(np.array(range(len(df))), inplace=True)
    return df


def shuffle_dataframe(df: pd.DataFrame, random_state: int = 0) -> pd.DataFrame:
    """Return a copy of the dataframe df shuffled, random_state
    argument may be used to reproduce same shuffling.

    Parameters
    ----------
    df: `pandas.DataFrame`
        dataframe to be shuffled

    random_state: `int`
        number to reproduce same randomness

    Returns
    -------
    result: `pandas.DataFrame`
        shuffled dataframe
    """
    df_randomized = df.sample(frac=1, random_state=random_state)
    return df_randomized


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
    coordinate ra-dec.

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
        raise Exception(
            f"No tract-patch info found" f"for ra: {ra} dec: {dec}"
        )
    return TractPatchInformation(
        final_data["lsst_tract"].iloc[0], final_data["lsst_patch"].iloc[0]
    )


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
    dims : `Tuple[int, int]`
        PSF postage stamp dimensions.
    """

    fwhm: float
    ap_flux: float
    peak: float
    dims: (int, int)

    def __str__(self):
        return (
            f"PSF FWHM: {self.fwhm:.4} pix \n"
            f"PSF flux from aperture photometry: {self.ap_flux:.4} \n"
            f"Peak PSF value: {self.peak:.4} \n"
            f"PSF postage stamp dimensions: {self.dims} \n"
        )

    def __repr__(self):
        return self.__str__()


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
    return PsfProperties(fwhm, ap_flux, peak, (dims[0], dims[1]))


def gauss(x, a, x0, sigma):
    # Helper function to define a one-dimensional Gaussian profile.
    return a * np.exp(-((x - x0) ** 2) / (2 * sigma**2))
