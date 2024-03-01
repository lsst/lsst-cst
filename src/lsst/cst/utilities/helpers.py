"""data science helper functions for
image and data plotting.
"""

import logging
from collections.abc import Sequence
from typing import Optional, Tuple, Union

import pandas as pd
import panel as pn
from astropy.coordinates import SkyCoord
from bokeh.models import HoverTool  # noqa: F401
from holoviews.element.chart import Scatter

from lsst.cst.data_visualization import (
    DataImageDisplay,
    DataShadeOptions,
    GeometricPlots,
    HVScatterOptions,
    PolygonOptions,
)
from lsst.cst.image_display import (
    CalExpImageDisplay,
    HoverSources,
    ImageDisplay,
    RGBImageDisplay,
)
from lsst.cst.utilities.data import create_rgb, cutout_coadd
from lsst.cst.utilities.parameters import Band, PlotOptionsDefault
from lsst.cst.utilities.queries import (
    DataWrapper,
    QueryCoordinateBoundingBox,
    QueryExposureData,
    QueryPsFlux,
    TAPService,
)

_log = logging.getLogger(__name__)


try:
    from lsst.afw.image import MultibandExposure
    from lsst.afw.image._exposure import ExposureF
except ImportError:
    _log.warning("Unable to import lsst.afw")

_lsst_stack_ready = False

__all__ = [
    "create_interactive_image",
    "create_rgb_composite_image",
    "create_skycoord_datashader_plot",
    "create_datashader_plot",
    "create_skycoord_linked_plot_with_brushing",
    "create_linked_plot_with_brushing",
    "create_bounding_boxes_calexps_overlapping_a_point_plot",
    "create_psf_flux_plot",
]


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
    title: `str`
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


def _get_skycoord_data(coord: SkyCoord, reduction: float = 1.0):
    # Helper function to get SkyCoord data
    assert (
        0.0 < reduction < 1.0
    ), "Select a valid reduction value between 0 and 1"
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
    reduction: float = 1.0,
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
        Panel Row with the scatter image inside of it.
    """
    data = _get_skycoord_data(coord, reduction)
    return create_datashader_plot(data, columns)


def create_datashader_plot(
    data: Union[DataWrapper, pd.DataFrame],
    columns: Optional[Tuple[str, str]] = None,
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
        Panel Row with the scatter image inside of it.
    """
    if isinstance(data, pd.DataFrame):
        data = DataWrapper(data)
    data_display = DataImageDisplay(data)
    if columns is not None:
        axes = (
            data_display.create_axe(columns[0]),
            data_display.create_axe(columns[1]),
        )
        hvalues = list(columns)
        columns = axes
    else:
        hvalues = [data.index[0], data.index[1]]
        columns = axes
    data_shade = data_display.show_data_shade(
        columns,
        DataShadeOptions(
            xlabel=hvalues[0],
            ylabel=hvalues[1],
        ),
    )
    return pn.Row(data_shade)


def create_skycoord_linked_plot_with_brushing(
    coord: SkyCoord,
    columns: Optional[Tuple[str, str]] = None,
    reduction: float = 1.0,
    hovertool: HoverTool = None,
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
        Panel Row containing scatter plot with histograms.
    """
    data = _get_skycoord_data(coord, reduction)
    return create_linked_plot_with_brushing(data, columns, hovertool)


def create_linked_plot_with_brushing(
    data: Union[DataWrapper, pd.DataFrame],
    columns: Optional[Tuple[str, str]] = None,
    hovertool: HoverTool = None,
    options: HVScatterOptions = HVScatterOptions(),
    show_histogram: bool = True,
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
    options: `HVScatterOptions`, optional
        Holoviews scatter options.
    show_histogram: `bool`, optional
        Attach histogram to plot.

    Returns
    -------
    plot: `hv.Layout`
        Panel Row containing scatter plot.
    """
    if isinstance(data, pd.DataFrame):
        data = DataWrapper(data)
    data_display = DataImageDisplay(data)
    if columns is not None:
        axes = (
            data_display.create_axe(columns[0]),
            data_display.create_axe(columns[1]),
        )
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
        ),
    )
    if show_histogram:
        scatter = scatter.hist(dimension=hvalues)
    return pn.Row(scatter)


def create_bounding_boxes_calexps_overlapping_a_point_plot(
    coord: SkyCoord, mjd_range: Tuple[int, int]
):
    """Draw bounding boxes of all calexps overlapping a point.

    Parameters
    ----------
    ra: `np.float64`
        Coordinate ascension.
    dec: `np.float64`
        Coordinate declination.
    mjd_range: `Tuple[int, int]`
       Time range to look for.

    Returns
    -------
    plot: `pn.Row`
        Panel Row containing bounding boxes ovelapping
        a point plot.
    """
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
        r = {
            "x": [row["llcra"], row["ulcra"], row["urcra"], row["lrcra"]],
            "y": [row["llcdec"], row["ulcdec"], row["urcdec"], row["lrcdec"]],
            "v1": row["band"],
            "v2": row["ccdVisitId"],
        }
        region_list.append(r)
    tooltips = [("band", "@v1"), ("ccdVisitId", "@v2")]

    hover = HoverTool(tooltips=tooltips)
    boxes = GeometricPlots.polygons(
        region_list,
        kdims=["x", "y"],
        vdims=["v1", "v2"],
        options=PolygonOptions(
            cmap=PlotOptionsDefault.filter_colormap,
            line_color="v1",
            tools=[hover],
        ),
    )
    _log.debug("Creating point")
    points = GeometricPlots.points((coord.ra.deg, coord.dec.deg))
    return pn.Row(boxes * points)


def create_psf_flux_plot(
    dia_object_id: int, band: Band, show: str = "psfFlux"
):
    """Create psf flux plot, psfFlux or psfDiffFlux values over time.

    Parameters
    ----------
    dia_object_id: `int`
        Object identifier.
    band: `Band`
        Selected band.
    show: `str`
        Selectable data to be plotted over time,
        psfFlux or psfDiffFlux.

    Returns
    -------
        Panel row containing psfFlux or psfDiffFlux value
        over time.
    """
    assert show in [
        "psfFlux",
        "psfDiffFlux",
    ], "No valid selected data to be shown, should be psfFlux or psfDiffFlux"

    _log.info(f"Retrieving data: Selected: {show}")
    tap_exposure_data = TAPService()
    query = QueryPsFlux(dia_object_id, band.value)
    tap_exposure_data.query = query
    data = tap_exposure_data.fetch()
    _log.info("Plotting data")
    options = HVScatterOptions()
    options.color = PlotOptionsDefault.filter_colormap[band.value]
    return create_linked_plot_with_brushing(
        data,
        columns=["expMidptMJD", show],
        options=options,
        show_histogram=False,
    )
