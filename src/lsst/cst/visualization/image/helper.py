"""data science helper functions for image plots."""
import logging
from collections.abc import Sequence
from typing import Optional, Tuple

import pandas as pd
import panel as pn

from lsst.cst.data.queries import Band
from lsst.cst.data.tools import create_rgb, cutout_coadd
from lsst.cst.visualization.image import (
    CalExpImageDisplay,
    HoverSources,
    ImageDisplay,
    RGBImageDisplay,
)

_log = logging.getLogger(__name__)

try:
    from lsst.afw.image import MultibandExposure
    from lsst.afw.image._exposure import ExposureF
except ImportError:
    _log.warning("Unable to import lsst.afw")

    _lsst_stack_ready = False


def create_interactive_image(
    calexp: "ExposureF",
    sources: Optional[Tuple[pd.Series]] = None,
    title: str = "Untitled",
    axes_label: Tuple[str, str] = ("X", "Y"),
    marker: str = "circle",
    marker_color: str = "orange",
):
    """Shows a interactive image from a butler image and its sources.

    Parameters
    ----------
    calexp: `lsst.afw.image._exposure.ExposureF`
        Exposure data.
    sources: `Tuple[pd.Series]`
        Exposure data sources.
    title: `str``
        Plot title.
    marker: `str`
        Marker type. for example:
            circle, square, triangle, cross, x, diamond...
    marker_color: `str`
        Marker color for the sources.

    Returns
    -------
    plot: `pn.Row`
        Panel Row containing the plot from the exposure
        with sources.

    """
    bounds = (0, 0, calexp.getDimensions()[0], calexp.getDimensions()[1])
    image_options = CalExpImageDisplay.options(cmap="Greys_r")
    source_options = HoverSources.options(color=marker_color, marker=marker)
    cal_exp_plot = ImageDisplay.from_image_array(
        calexp.image.array,
        bounds=bounds,
        title=title,
        xlabel=axes_label[0],
        ylabel=axes_label[1],
        image_options=image_options,
    )
    if sources is None:
        return cal_exp_plot.show()
    h_sources = HoverSources(cal_exp_plot, sources, source_options)
    img = h_sources.show()
    return pn.Row(img)


def create_rgb_composite_image(
    butler,
    ra: float,
    dec: float,
    bands: Sequence[Band] = (Band.g, Band.r, Band.i),
    cutout_side_length: int = 701,
    scale: Optional[Sequence[float]] = None,
    stretch: int = 1,
    Q: int = 10,
):
    """Create an RGB composite image from a location.

    Parameters
    ----------
    butler: `lsst.daf.persistence.Butler`
        Helper object providing access to a data repository.
    ra: `float`
        Right ascension of the center of the cutout, in degrees.
    dec: `float`
        Declination of the center of the cutout, in degrees.
    bands : `sequence`, optional
        A 3-element sequence of filter names (i.e., keys of the exps dict)
        indicating what band to use for each channel.
    cutout_side_length: `float`, optional
        Size of the cutout region in pixels.
    scale: `List[float]`, optional
        list of 3 floats, each less than 1.
        Re-scales the RGB channels.
    stretch: `int`, optional
        The linear stretch of the image.
    Q: `int`, optional
        The Asinh softening parameter.
    """
    band_values = [member.value for member in bands]
    cutout_image_g = cutout_coadd(
        butler,
        ra,
        dec,
        band=band_values[0],
        datasetType="deepCoadd",
        cutout_side_length=cutout_side_length,
    )
    cutout_image_r = cutout_coadd(
        butler,
        ra,
        dec,
        band=band_values[1],
        datasetType="deepCoadd",
        cutout_side_length=cutout_side_length,
    )
    cutout_image_i = cutout_coadd(
        butler,
        ra,
        dec,
        band=band_values[2],
        datasetType="deepCoadd",
        cutout_side_length=cutout_side_length,
    )
    coadds = [cutout_image_g, cutout_image_r, cutout_image_i]
    coadds = MultibandExposure.fromExposures(band_values, coadds)
    img = create_rgb(
        coadds.image, bgr=band_values, scale=scale, stretch=stretch, Q=Q
    )
    display = RGBImageDisplay(img)
    display.render()
    return display.show()
