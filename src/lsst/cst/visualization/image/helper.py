import pandas as pd

from typing import Tuple, Optional
from lsst.afw.image._exposure import ExposureF
from lsst.cst.visualization.image import CalExpImageDisplay, HoverSources, ImageDisplay


def create_interactive_image(
    image: ExposureF,
    sources: Tuple[pd.Series],
    label: Optional[str] = None,
    axe_labels: Tuple[str, str] = ("X", "Y"),
    font_size: int = 18,
    marker: str = 'circle',
    marker_color: str = 'orange'
):
    """
    Shows a interactive image from a butler image and its sources.

    Parameters
    ----------

    Returns
    -------

    """
    image_options = CalExpImageDisplay.options(font_size=font_size)
    source_options = HoverSources.options(marker_color=marker_color, marker=marker)
    cal_exp_plot = ImageDisplay.from_image_array(image.array,
                                                 title=label,
                                                 xlabel=axe_labels[0],
                                                 ylabel=axe_labels[1],
                                                 image_options=image_options)
    h_sources = HoverSources(cal_exp_plot, source_options)
    return h_sources.show()
