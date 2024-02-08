import pandas as pd
import logging

from astropy.coordinates import SkyCoord
from holoviews.element.chart import Scatter
from lsst.cst.visualization.utils import QueryTAPExposureData, ExposureData
from lsst.cst.visualization.data.displays import (
    DataImageDisplay,
    HoverTool,
    HVScatterOptions,
    DataShadeOptions
)
from typing import Optional, Tuple, Union


_log = logging.getLogger(__name__)


def _create_scatter(
    data: ExposureData,
    column: Optional[Tuple[str, str]] = None,
    hovertool: HoverTool = None,
    datashade_options: DataShadeOptions = DataShadeOptions()
):
    # Helper function to create a Scatter data plot
    data_display = DataImageDisplay(data)
    if column is not None:
        data_display.create_axe(column[0])
        data_display.create_axe(column[1])
    _log.info("Creating Scatter")
    return data_display.show_scatter(
        datashade_options=datashade_options,
        options=HVScatterOptions(
            tools=[] if hovertool is None else [hovertool],
            marker="circle",
            xlabel=data.index[0],
            ylabel=data.index[1],
        )
    )


def _get_skycoord_data(coord: SkyCoord, reduction: float = 1.0):
    # Helper function to get SkyCoord data
    assert 0.0 < reduction < 1.0, \
        "Select a valid reduction value between 0 and 1"
    _log.info("Fetching data")
    tap_exposure_data = QueryTAPExposureData.from_sky_coord(coord, 1.0)
    tap_exposure_data.fetch()
    data = tap_exposure_data.data
    _log.info("Reducing data")
    data = data.reduce_data(reduction)
    return data


def create_skycoord_datashader_plot(
    coord: SkyCoord,
    columns: Optional[Tuple[str, str]] = None,
    reduction: float = 1.0,
    color_map: str = "Viridis"
):
    data = _get_skycoord_data(coord, reduction)
    create_datashader_plot(data)


def create_datashader_plot(
    data: Union[ExposureData, pd.array],
    columns: Optional[Tuple[str, str]] = None,
    color_map: str = "Viridis"
) -> Scatter:
    if isinstance(data, pd.DataFrame):
        data = ExposureData(data)
    datashade_options = DataShadeOptions(True, color_map)
    return _create_scatter(data=data, columns=columns, datashade_options=datashade_options)


def create_skycoord_linked_plot_with_brushing(
    coord: SkyCoord,
    columns: Optional[Tuple[str, str]] = None,
    reduction: float = 1.0,
    hovertool: HoverTool = None
):
    data = _get_skycoord_data(coord, reduction)
    return create_linked_plot_with_brushing(data, columns, hovertool)


def create_linked_plot_with_brushing(
    data: Union[ExposureData, pd.array],
    column: Optional[Tuple[str, str]] = None,
    hovertool: HoverTool = None
) -> Scatter:
    """Create a linked plot with brushing from a pd.DataFrame.
    The plot will be created the first two colums from the df

    Parameters
    ----------
    data: Union[ExposureData, pd.array]
        Data to be displayed in the plot

    hovertool: HoverTool
        Hovertool to be used when hovering the mouse
        over the plot points

    Return
    ------
    plot: `Scatter`
        Holoviews created scatter plot
    """
    if isinstance(data, pd.DataFrame):
        data = ExposureData(data)
    scatter = _create_scatter(data=data, column=column, hovertool=hovertool)
    return scatter.hist(
        dimension=[data.index[0], data.index[1]],
    )
