import pandas as pd
import logging

from astropy.coordinates import SkyCoord
from holoviews.element.chart import Scatter
from lsst.cst.visualization.utils import QueryTAPExposureData, ExposureData
from lsst.cst.visualization.data.displays import DataImageDisplay, HoverTool, HVScatterOptions
from typing import Union

_log = logging.getLogger(__name__)


def create_skycoord_linked_plot_with_brushing(
    coord: SkyCoord,
    reduction: float = 1.0
):
    assert 0.0 < reduction < 1.0, \
        "Select a valid reduction value between 0 and 1"
    _log.info("Fetching data")
    tap_exposure_data = QueryTAPExposureData.from_sky_coord(coord, 1.0)
    tap_exposure_data.fetch()
    data = tap_exposure_data.data
    _log.info("Reducing data")
    data = data.reduce_data(reduction)


def create_linked_plot_with_brushing(
    data: Union[ExposureData, pd.array],
    hovertool: HoverTool = None
) -> Scatter:
    """.env"""
    if isinstance(data, pd.DataFrame):
        data = ExposureData(data)
    data_display = DataImageDisplay(data)
    _log.info("Creating Scatter")
    return data_display.show_scatter(
        options=HVScatterOptions(
            tools=[] if hovertool is None else [hovertool],
            marker="circle"
        )
    ).hist(
        dimension=[data.index[0], data.index[1]],
    )
