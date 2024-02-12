import pandas as pd
import logging

from astropy.coordinates import SkyCoord
from holoviews.element.chart import Scatter
from lsst.cst.data.tools import QueryTAPExposureData, ExposureData
from lsst.cst.visualization.data.displays import (
    DataImageDisplay,
    HoverTool,
    HVScatterOptions,
    DataShadeOptions
)
from typing import Optional, Tuple, Union


_log = logging.getLogger(__name__)


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
    reduction: float = 1.0
):
    """Create a datashader plot out of a skycoord object.
    Object data will be retrieved using the TAP Service, note
    that any data column can be selected to be used as the
    plot scatter data, if none column is selected, then two
    first columns will be used.
    A reduction number is also accepted to be able to reduce
    data if too many rows in the select are expected.

    Parameters:
    -----------
    coord: `astropy.coordinates.SkyCoord`
        Coordinates of the TAP data to look for.
    columns: Tuple[str, str], optional
        Columns from data that will be used to create the plot.
    reduction: `float`, optional
        Reduction to be applied to the data retrieves
    Returns:
    -------
    plot: `holoviews.core.layout.AdjointLayout`
        Scatter image with histogram information on both axes.    

    """
    data = _get_skycoord_data(coord, reduction)
    return create_datashader_plot(data, columns)


def create_datashader_plot(
    data: Union[ExposureData, pd.DataFrame],
    columns: Optional[Tuple[str, str]] = None
) -> Scatter:
    """Create a datashader plot out of a pd.DataFrame, note
    that any data column can be selected to be used as the
    plot scatter data, if none column is selected, then two
    first columns will be used.

    Parameters:
    -----------
    coord: `astropy.coordinates.SkyCoord`
        Coordinates of the TAP data to look for.
    columns: Tuple[str, str], optional
        Columns from data that will be used to create the plot.
    reduction: `float`, optional
        Reduction to be applied to the data retrieves
    Returns:
    -------
    plot: `holoviews.core.layout.AdjointLayout`
        Scatter image with histogram information on both axes.

    """
    if isinstance(data, pd.DataFrame):
        data = ExposureData(data)
    data_display = DataImageDisplay(data)
    if columns is not None:
        axes = (data_display.create_axe(columns[0]),
                data_display.create_axe(columns[1]))
        hvalues = list(columns)
        columns = axes
    else:
        hvalues = [data.index[0], data.index[1]]
        columns = axes
    return data_display.show_data_shade(
        columns,
        DataShadeOptions(
            xlabel=hvalues[0],
            ylabel=hvalues[1],))


def create_skycoord_linked_plot_with_brushing(
    coord: SkyCoord,
    columns: Optional[Tuple[str, str]] = None,
    reduction: float = 1.0,
    hovertool: HoverTool = None
):
    """Create a linked plot with brushing from out of a SkyCoord
    coordinates. The plot will be created the first two colums from the df

    Parameters
    ----------
    coord: SkyCoord,
        Coordinates of the data to be plotted.
    columns: Tuple[str, str], optional
        Columns selected from the dataframe to be used in the plot.
    hovertool: HoverTool, optional
        Hovertool to be used when hovering the mouse
        over the plot points.

    Return
    ------
    plot: `Scatter`
        Holoviews created scatter plot with histograms.
    """
    data = _get_skycoord_data(coord, reduction)
    return create_linked_plot_with_brushing(data, columns, hovertool)


def create_linked_plot_with_brushing(
    data: Union[ExposureData, pd.DataFrame],
    columns: Optional[Tuple[str, str]] = None,
    hovertool: HoverTool = None
) -> Scatter:
    """Create a linked plot with brushing from a pd.DataFrame.
    The plot will be created the first two colums from the df if 
    no columns are explicitely selected.

    Parameters
    ----------
    data: pd.Series
        Pd series containing data to be plotted.
    columns: Tuple[str, str], optional
        Columns selected from the dataframe to be used in the plot.
    hovertool: HoverTool, optional
        Hovertool to be used when hovering the mouse
        over the plot points.

    Return
    ------
    plot: `Scatter`
        Holoviews created scatter plot with histograms.
    """
    if isinstance(data, pd.DataFrame):
        data = ExposureData(data)
    data_display = DataImageDisplay(data)
    if columns is not None:
        axes = (data_display.create_axe(columns[0]),
                data_display.create_axe(columns[1]))
        hvalues = list(columns)
        columns = axes
    else:
        hvalues = [data.index[0], data.index[1]]
    _log.info("Creating Scatter")
    return data_display.show_scatter(
        columns=columns,
        options=HVScatterOptions(
            tools=[] if hovertool is None else [hovertool],
            marker="circle",
            xlabel=hvalues[0],
            ylabel=hvalues[1],
        )).hist(dimension=hvalues)
