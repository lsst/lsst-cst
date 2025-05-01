"""Utility functions for tutorial notebooks."""

import numpy as np
import json
import warnings
import gc
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from panel.layout.base import Panel
from lsst import geom

__all__ = [
    "ids_to_str",
    "data_id_to_str",
    "psf_size_at_pixel_xy",
    "delete_plot"
]


def ids_to_str(data_ids: np.ndarray) -> str:
    """Transform a numpy array of object identifiers
    (long integers) to a string of comma-separated values
    enclosed in parentheses. This is the format required for
    a WHERE ... IN ... statement in a TAP query.

    Parameters
    ----------
    data_ids: `numpy.ndarray`
        Array of object IDs (long int).

    Returns
    -------
    result: `str`
        String of comma-separated IDs, in parentheses.
    """
    return "(" + ", ".join(str(value) for value in data_ids) + ")"


def data_id_to_str(data_id: dict) -> str:
    """Converts a data identifier dictionary to a string.
    Will work on any dict and is not specific to the dataId format.

    Parameters
    ----------
    data_id: `dict`
        Data identifier dictionary.

    Returns
    -------
    data_id_str: `str`
        Data identifier string.
    """
    data_id_str = json.dumps(data_id)
    return data_id_str


def sregion_to_vertices(sregion: str):
    """Convert the s_region from the ObsCore table into two
    arrays containing the x and y vertices, in order to plot
    boxes using matplotlib.

    Parameters
    ----------
    str_polygon: `str`
        String formatted with 10 space-separated items, e.g.,
        the "s_region" column from the ObsCore table which has
        the words "POLYGON ICRS" followed by 8 numbers:
        "POLYGON ICRS # # # # # # # #".

    Returns
    -------
    x_vertices: `np.ndarray`
        The array of x-vertices.
    y_vertices: `np.ndarray`
        The array of y-vertices.
    """
    temp = sregion.split(' ')
    xvertices = []
    yvertices = []
    ix = 2
    iy = 3
    for c in range(4):
        xvertices.append(float(temp[ix]))
        yvertices.append(float(temp[iy]))
        ix += 2
        iy += 2
    xvertices.append(xvertices[0])
    yvertices.append(yvertices[0])
    return xvertices, yvertices


def psf_size_at_pixel_xy(psf, bbox, xy: tuple[int, int]) -> dict[str, float]:
    """Obtains the size of the PSF in an image
    at a given xy coordinate.

    Parameters
    ----------
    psf : `lsst.meas.extensions.psfex.PsfexPsf` or
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


def delete_plot(plot: Panel | Figure) -> None:
    """Delete selected plot.

    Parameters
    ----------
    plot: 'Panel | Figure'
       Plot to be deleted.
    """
    if isinstance(plot, Figure):
        _remove_figure(plot)
    elif isinstance(plot, Panel):
        plot.clear()
        del plot
        import gc

        gc.collect()
    else:
        raise Exception(f"Unknown instance to delete {type(plot)}")


def _remove_figure(fig: Figure):
    """Remove a figure to reduce memory footprint.

    Parameters
    ----------
    fig : `matplotlib.figure.Figure`
        Figure to be removed.
    """
    # Get the axes and clear their images
    for ax in fig.get_axes():
        for im in ax.get_images():
            im.remove()
    # Clear the figure
    fig.clf()
    # Close the figure
    plt.close(fig)
    # Call the garbage collector
    gc.collect()
