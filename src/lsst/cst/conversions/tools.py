"""Tools for common conversions."""

import numpy as np
import json
import warnings

try:
    from lsst import geom
except ImportError:
    warnings.warn("Unable to import lsst.geom.")

from lsst.cst.utilities.queries import RaDecCoordinatesToTractPatch, TAPService


__all__ = [
    "ids_to_str",
    "data_id_to_str",
    "psf_size_at_pixel_xy",
    "nearest_patch_from_ra_dec",
]


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


def data_id_to_str(data_id: dict) -> str:
    """Converts a data identifier dictionary to a string.
    Will work on any dict, not specific to dataId format.

    Parameters
    ----------
    data_id: 'dict'
        Data identifier dictionary.

    Returns
    -------
    data_id_str: `str`
        Data identifier string.
    """
    data_id_str = json.dumps(data_id)
    return data_id_str


def psf_size_at_pixel_xy(psf, bbox, xy: tuple[int, int]) -> dict[str, float]:
    """Obtains the size of the PSF in an image
    at a given xy coordinate.

    Parameters
    ----------
    psf : `lsst.meas.extensions.psfex.PsfexPsf` or \
          `lsst.meas.algorithms.CoaddPsf`
        PSF object from a calexp or deepCoadd respectively; use .getPsf().
    bbox : `lsst.geom.Box2I`
        Bounding box for the calexp or deepCoadd; use .getBBox().
    xy : `tuple` [`int`, `int`]
        Pixel coordinates x and y where PSF size is to be evaluated.

    Returns
    -------
    psf_size: `dict`
        Size of the PSF in pixels; sigma and FWHM.
    """
    point2I = geom.Point2I(xy[0], xy[1])
    if bbox.contains(point2I):
        point2D = geom.Point2D(xy[0], xy[1])
        sigma = psf.computeShape(point2D).getDeterminantRadius()
        fwhm = sigma * 2.0 * np.sqrt(2.0 * np.log(2.0))
    else:
        raise Exception("Coordinates xy not contained by image boundaries.")
    psf_size = {'sigma': sigma, 'fwhm': fwhm}
    return psf_size


def nearest_patch_from_ra_dec(ra: float, dec: float) -> dict:
    """Return nearest deepCoadd skymap patch, and its tract,
    for a given RA and Dec.

    Parameters
    ----------
    ra: `np.float64`
        Right ascension, in decimal degrees.
    dec: `np.float64`
        Declination, in decimal degrees.

    Returns
    -------
    nearest_patch: `dict`
        Numerical identifiers for the nearest patch (and its tract),
        and the distance (in degrees) to its center from the input coordinates.
    """
    tap_launcher = TAPService()
    query = RaDecCoordinatesToTractPatch(ra, dec)
    tap_launcher.query = query
    data = tap_launcher.fetch()
    results = data._data
    if results.empty:
        raise Exception("No patch found for RA {}, Dec {}.".format(ra, dec))

    # for DP0, 4100 pixels * (0.2 arcsec / pixel) * (degree / 3600 arcsec) / 2
    patch_half_side = 4100 * 0.2 / 3600.0 / 2

    # include the cos dec term to get maximum distance in RA
    maxdist_ra = patch_half_side / np.cos(np.deg2rad(dec))

    # diagonal distance from patch center to corner
    maxdist = np.sqrt(patch_half_side**2 + maxdist_ra**2)

    if (results["distance"].iloc[0] >= maxdist_ra)\
       & (results["distance"].iloc[0] <= maxdist):
        warnings.warn("Large distance to nearest patch ({} deg). "
                      "RA {}, Dec {} might not be within nearest patch "
                      "boundary.".format(results["distance"].iloc[0], ra, dec))
    if results["distance"].iloc[0] > maxdist:
        raise Exception("Large distance to nearest patch ({} deg). "
                        "RA {}, Dec {} do not fall withinin nearest patch "
                        "boundary.".format(results["distance"].iloc[0],
                                           ra, dec))

    nearest_patch = {'tract': results["lsst_tract"].iloc[0],
                     'patch': results["lsst_patch"].iloc[0],
                     'distance in degrees': results["distance"].iloc[0]}
    return nearest_patch
