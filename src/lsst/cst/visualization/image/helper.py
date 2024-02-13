"""data science helper functions for image plots."""
import pandas as pd
import holoviews as hv
from typing import Tuple, Optional
from lsst.afw.image._exposure import ExposureF
from lsst.cst.visualization.image import CalExpImageDisplay, HoverSources, ImageDisplay


def create_interactive_image(
    calexp: ExposureF,
    sources: Optional[Tuple[pd.Series]] = None,
    title: str = "Untitled",
    axes_label: Tuple[str, str] = ("X", "Y"),
    marker: str = 'circle',
    marker_color: str = 'orange'
):
    """
    Shows a interactive image from a butler image and its sources.

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


    """
    bounds = (0,
              0,
              calexp.getDimensions()[0],
              calexp.getDimensions()[1])
    image_options = CalExpImageDisplay.options()
    source_options = HoverSources.options(color=marker_color, marker=marker)
    cal_exp_plot = ImageDisplay.from_image_array(calexp.image.array,
                                                 bounds=bounds,
                                                 title=title,
                                                 xlabel=axes_label[0],
                                                 ylabel=axes_label[1],
                                                 image_options=image_options)
    if sources is None:
        return cal_exp_plot.show()
    h_sources = HoverSources(cal_exp_plot, sources, source_options)
    img = h_sources.show()
    return hv.Layout(img)
