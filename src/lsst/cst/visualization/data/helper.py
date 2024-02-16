"""data science helper functions for data plots."""
import pandas as pd
import logging
import panel as pn

from astropy.coordinates import SkyCoord
from holoviews.element.chart import Scatter
from lsst.cst.data.queries import (
    TAPService,
    DataWrapper,
    QueryExposureData,
    QueryCoordinateBoundingBox
)
from lsst.cst.visualization.params import PlotOptionsDefault

from lsst.cst.visualization.data.displays import (
    DataImageDisplay,
    HoverTool,
    HVScatterOptions,
    DataShadeOptions,
    PolygonOptions,
    GeometricPlots
)
from typing import Optional, Tuple, Union


_log = logging.getLogger(__name__)


def _get_skycoord_data(coord: SkyCoord, reduction: float = 1.0):
    # Helper function to get SkyCoord data
    assert 0.0 < reduction < 1.0, \
        "Select a valid reduction value between 0 and 1"
    _log.info("Fetching data")
    tap_exposure_data = TAPService()
    query = QueryExposureData.from_sky_coord(coord, 1.0)
    tap_exposure_data.query = query
    data = tap_exposure_data.fetch()
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

    Parameters
    ----------
    coord: `astropy.coordinates.SkyCoord`
        Coordinates of the TAP data to look for.
    columns: Tuple[str, str], optional
        Columns from data that will be used to create the plot.
    reduction: `float`, optional
        Reduction to be applied to the data retrieves.

    Returns
    -------
    plot: `hv.Layout`
        holoviews layout with the scatter image inside of it.
    """
    data = _get_skycoord_data(coord, reduction)
    return create_datashader_plot(data, columns)


def create_datashader_plot(
    data: Union[DataWrapper, pd.DataFrame],
    columns: Optional[Tuple[str, str]] = None
) -> Scatter:
    """Create a datashader plot out of a pd.DataFrame, note
    that any data column can be selected to be used as the
    plot scatter data, if none column is selected, then two
    first columns will be used.

    Parameters
    ----------
    coord: `astropy.coordinates.SkyCoord`
        Coordinates of the TAP data to look for.
    columns: Tuple[str, str], optional
        Columns from data that will be used to create the plot.
    reduction: `float`, optional
        Reduction to be applied to the data retrieves

    Returns
    -------
    plot: `hv.Layout`
        holoviews layout with the scatter image inside of it.
    """
    if isinstance(data, pd.DataFrame):
        data = DataWrapper(data)
    data_display = DataImageDisplay(data)
    if columns is not None:
        axes = (data_display.create_axe(columns[0]),
                data_display.create_axe(columns[1]))
        hvalues = list(columns)
        columns = axes
    else:
        hvalues = [data.index[0], data.index[1]]
        columns = axes
    data_shade = data_display.show_data_shade(
        columns,
        DataShadeOptions(
            xlabel=hvalues[0],
            ylabel=hvalues[1],))
    return pn.Row(data_shade)


def create_skycoord_linked_plot_with_brushing(
    coord: SkyCoord,
    columns: Optional[Tuple[str, str]] = None,
    reduction: float = 1.0,
    hovertool: HoverTool = None
):
    """Create a linked plot with brushing from out of
    a SkyCoord coordinates. The plot will be created
    the first two colums from the df

    Parameters
    ----------
    coord: SkyCoord,
        Coordinates of the data to be plotted.
    columns: Tuple[str, str], optional
        Columns selected from the dataframe to be used in the plot.
    hovertool: HoverTool, optional
        Hovertool to be used when hovering the mouse
        over the plot points.

    Returns
    -------
    plot: `hv.Layout`
        Holoviews layout containing scatter plot with histograms.
    """
    data = _get_skycoord_data(coord, reduction)
    return create_linked_plot_with_brushing(data, columns, hovertool)


def create_linked_plot_with_brushing(
    data: Union[DataWrapper, pd.DataFrame],
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

    Returns
    -------
    plot: `hv.Layout`
        Holoviews layout containing scatter plot with histograms.
    """
    if isinstance(data, pd.DataFrame):
        data = DataWrapper(data)
    data_display = DataImageDisplay(data)
    if columns is not None:
        axes = (data_display.create_axe(columns[0]),
                data_display.create_axe(columns[1]))
        hvalues = list(columns)
        columns = axes
    else:
        hvalues = [data.index[0], data.index[1]]
    _log.info("Creating Scatter")
    scatter = data_display.show_scatter(
        columns=columns,
        options=HVScatterOptions(
            tools=[] if hovertool is None else [hovertool],
            marker="circle",
            xlabel=hvalues[0],
            ylabel=hvalues[1],
        )).hist(dimension=hvalues)
    return pn.Row(scatter)


def create_bounding_boxes_calexps_overlapping_a_point_plot(
    coord: SkyCoord,
    mjd_range: Tuple[int],

):
    """"""
    _log.info("Retrieving data")
    tap_exposure_data = TAPService()
    mjd1 = str(mjd_range[0])
    mjd2 = str(mjd_range[1])
    query = QueryCoordinateBoundingBox.from_sky_coord(coord, mjd1, mjd2)
    tap_exposure_data.query = query
    data = tap_exposure_data.fetch()
    df = data._data
    region_list = []
    _log.debug("Creating bounding boxes")
    for index, row in df.iterrows():
        r = {'x': [row['llcra'], row['ulcra'], row['urcra'], row['lrcra']],
             'y': [row['llcdec'], row['ulcdec'], row['urcdec'], row['lrcdec']],
             'v1': row['band'],
             'v2': row['ccdVisitId']}
        region_list.append(r)
    tooltips = [
        ('band', '@v1'),
        ('ccdVisitId', '@v2')
    ]

    hover = HoverTool(tooltips=tooltips)
    boxes = GeometricPlots.polygons(region_list,
                                    kdims=['x', 'y'],
                                    vdims=['v1', 'v2'],
                                    options=PolygonOptions(cmap=PlotOptionsDefault.filter_colormap,
                                                           line_color='v1',
                                                           tools=[hover])
                                    )
    _log.debug("Creating point")
    points = GeometricPlots.points((coord.ra.deg, coord.dec.deg))
    return pn.Row(boxes*points)
