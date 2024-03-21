"""lsst.cst data science plot display utilities."""

import logging
from collections.abc import Sequence
from typing import List, Optional, Tuple, TypedDict, Union

import holoviews as hv
from bokeh.io import show
from bokeh.models import HoverTool  # noqa: F401
from bokeh.models import BooleanFilter, CDSView
from bokeh.plotting import figure, gridplot
from holoviews.operation.datashader import datashade, dynspread

from lsst.cst.utilities.queries import DataWrapper

from .options import (
    DataShadeOptions,
    FigureOptions,
    HistogramOptions,
    HVScatterOptions,
    PointsOptions,
    PolygonOptions,
    ScatterOptions,
)

_log = logging.getLogger(__name__)


__all__ = [
    "DataImageDisplay",
    "GeometricPlots",
]


class DataFigure:
    """Figure class used to add different Scatter plots in it.

    Parameters
    ----------
    figure_id: `str``
        Figure string identifier.
    data: `DataWrapper`
        Data used to create plots inside the figure.
    options: `FigureOptions``
        Figure options.
    """

    def __init__(
        self,
        figure_id: str,
        data: DataWrapper,
        options: FigureOptions = FigureOptions(),
    ):
        self._figure_id = figure_id
        self._exposure_data = data
        self._figure = figure(**options.to_dict())

    def add_scatter(
        self,
        x_data: str,
        y_data: str,
        hover_tool: None | HoverTool = None,
        filter: None | Sequence[bool] = None,
        options: ScatterOptions = ScatterOptions(),
    ):
        """Add scatter plot to the figure.

        Parameters
        ----------
        x_data: `str`
            Identifier of the column from
            data to get as plot X values.
        y_data: `str`
            Identifier of the column from data
            to get as plot Y values.
        hover_tool: `HoverTool`, optional
            Hover tool to show when mouse is over data.
        filter: `Sequence`, optional
            Sequence with boolean values sized as
            the figure data, meaning the filter
            applied to the data, only rows with
            True will be applied.
        options: `ScatterOptions`
            Scatter plot options.
        """
        assert isinstance(
            options, ScatterOptions
        ), "Not valid options type, should be ScatterOptions"
        index = self._exposure_data.index
        assert x_data in index, (
            f"Selected data {x_data}" f"not available on exposure data"
        )
        assert y_data in index, (
            f"Selected data {y_data}" f"not available on exposure data"
        )
        view = CDSView()
        if filter is not None:
            view.filter = BooleanFilter(filter)
        glyph = self._figure.scatter(
            x_data,
            y_data,
            source=self._exposure_data.get_column_data_source(),
            view=view,
            **options.to_dict(),
        )
        if hover_tool is not None:
            # hover_tool.renderers.append(glyph)
            nhover_tool = HoverTool(
                renderers=[glyph],
                tooltips=hover_tool.tooltips,
                formatters=hover_tool.formatters,
            )
            self._figure.add_tools(nhover_tool)

    def add_histogram(self):
        pass

    @property
    def figure(self):
        return self._figure


class DataImageDisplay:
    """Scatter plots and figures creation management.

    Parameters
    ----------
    data: `DataWrapper`
        Data used to create plots.
    """

    def __init__(self, data: DataWrapper):
        self._exposure_data = data
        self._figures = {}  # type: dict[str, DataFigure]

    def get_figure(self, figure_identifier: str):
        """Returns previously created figure
           identified by the figure_identifier.

        Parameters
        ----------
        figure_identifier: `str`
            Unique identifier for a figure.

        Returns
        -------
        figure: `DataFigure`
            Figure identified by figure_identifier string.

        Raises
        ------
        AssertionError: Figure id is not found
        """
        figure = self._figures.get(figure_identifier, None)
        assert figure is not None, f"Figure {figure_identifier} doesnt exists"
        return figure

    def create_figure(
        self, identifier: str, options: FigureOptions = FigureOptions()
    ):
        """Creates a new figure and save the reference for future use.

        Parameters
        ----------
        identifier: `str`
            Figure identifier, used to use it as figure reference.
        figure_options: `FigureOptions`, optional
            Created figure options.

        Returns
        -------
        figure: `DataFigure`
            Data figure instance class.

        Raises
        ------
        AssertionError: Identifier already taken by another figure.
        """
        assert isinstance(
            options, FigureOptions
        ), "Not valid options type, should be ScatterOptions"
        new_figure = DataFigure(identifier, self._exposure_data, options)
        assert (
            identifier not in self._figures.keys()
        ), f"Figure {identifier} already exists"
        self._figures[identifier] = new_figure
        return new_figure

    def _exchange_figures(
        self,
        layout: List[Union[str, List[...]]],
        new_layout: List[Union[figure, List[...]]],
    ):
        # Helper function to exchange list of figure identifier
        # and exchange it for its equivalent created figure.
        for item in layout:
            if isinstance(item, list):
                aux_layout = []
                self._exchange_figures(item, aux_layout)
                new_layout.append(aux_layout)
            else:
                new_layout.append(self._figures[item].figure)

    def show(
        self,
        layout: List[Union[str, List[...]]],
        tools_position: str = "above",
    ):
        """Show selected figures already created and configured.

        Parameters
        ----------
        layout: `list`
            List containing the figures to be shown.

        tools_position: `str`
            Selected position for the toolbar.

        """
        new_layout = []
        self._exchange_figures(layout, new_layout)
        show(
            gridplot(new_layout),
            tools_position=tools_position,
            notebook_handle=True,
        )

    def create_axe(
        self,
        data_identifier: str,
        label: Optional[str] = None,
        range: Optional[Tuple[float, float]] = None,
        unit: str = "N/A",
    ):
        """Create Axe information to be used on scatter plots.

        Parameters
        ----------
        data_identifier: `str`
            Column indentifier from data used to draw the plot.
        label: `str`, optional
            Axe label.
        range: `Tuple[float, float]`, optional
            Axe range.
        unit: `str`, optional
            Axe units.

        Returns
        -------
        axe_information: `hv.Dimension`
            Axe information to be used in a scatter plot.
        """
        if label is None:
            label = data_identifier
        index = self._exposure_data.index
        assert data_identifier in index, (
            f"Selected data {data_identifier}"
            f"not available on exposure data"
        )
        return hv.Dimension(
            data_identifier, label=label, range=(None, None), unit=unit
        )

    def show_scatter(
        self,
        columns: Optional[
            Tuple[hv.Dimension | str, hv.Dimension | str]
        ] = None,
        options: HVScatterOptions = HVScatterOptions(),
    ):
        """Creates scatter plot using selected columns from data.

        Parameters
        ----------
        columns: `Tuple[hv.Dimension | str, hv.Dimension | str]`, optional
            Data columns to create the scatter plot, if non columns are passed
            the two first columns from data will be used.

        options: ScatterOptions, optional
            Scatter plot options.

        Returns
        -------
        plot: `hv.Scatter`
            Scatter plot.
        """
        assert isinstance(
            options, HVScatterOptions
        ), "Not valid options type, should be ScatterOptions"
        data = self._exposure_data.data
        if columns is None:
            scatter = hv.Scatter(data).options(**options.to_dict())
        else:
            index = self._exposure_data.index
            data_x = columns[0]
            data_y = columns[1]
            if isinstance(data_x, str):
                assert data_x in index, (
                    f"Selected data {data_x} for X "
                    f"not available on exposure data"
                )
            if isinstance(data_y, str):
                assert data_y in index, (
                    f"Selected data {data_y} for Y "
                    f"not available on exposure data"
                )
            scatter = hv.Scatter(data, data_x, data_y).options(
                **options.to_dict()
            )
        return scatter

    def show_data_shade(
        self,
        columns: Optional[
            Tuple[hv.Dimension | str, hv.Dimension | str]
        ] = None,
        options: DataShadeOptions = DataShadeOptions(),
    ):
        """Creates datashader plot using selected columns from data.

        Parameters
        ----------
        columns: `Tuple[hv.Dimension | str, hv.Dimension | str]`, optional
            Data columns selected to create the datashader plot,
            if non columns are passed the two first columns from
            data will be used.

        options: DataShadeOptions, optional
            Scatter plot options.

        Returns
        -------
        plot: `holoviews.core.spaces.DynamicMap`
            Datashader plot.
        """
        _log.debug("Applying datashade to data image.")
        assert isinstance(
            options, DataShadeOptions
        ), "Not valid options type, should be DataShadeOptions"
        scatter = self.show_scatter(columns)
        scatter = dynspread(datashade(scatter, cmap=options.cmap))
        scatter.opts(**options.to_dict())
        return scatter

    def show_histogram(
        self, field: "str", options: HistogramOptions = HistogramOptions()
    ):
        """Creates histogram plot using selected columns from data.

        Parameters
        ----------
        field: `str`
            Data column selected to create the histogram plot.
        options: HistogramOptions, optional
            Histogram plot options.

        Returns
        -------
        plot: `hv.Histogram`
            Histogram plot.
        """
        assert isinstance(
            options, HistogramOptions
        ), "Not valid options type, should be HistogramOptions"
        bin, count = self._exposure_data.histogram(field)
        return hv.Histogram((bin, count)).opts(**options.to_dict())


class PolygonInformation(TypedDict):
    x: Tuple[float, float, float, float]
    y: Tuple[float, float, float, float]
    v1: str
    v2: str


class GeometricPlots:
    """Static functions to create HV plots
    with geometric figures.
    """

    @staticmethod
    def points(
        points: List[Tuple[float, float]],
        options: PointsOptions = PointsOptions(),
    ):
        """Create a plot with the selected points on it.

        Parameters
        ----------
        points: `List[Tuple[float, float]]`
            Points to be plot.
        options: `PointsOptions`
            Points plot options.

        Returns
        -------
        plot: `hv.Points`
            Plot with the points draw on it.
        """
        assert isinstance(
            options, PointsOptions
        ), "Not valid options type, should be PointsOptions"
        points = hv.Points(points).opts(**options.to_dict())
        return points

    @staticmethod
    def polygons(
        region_data: list[PolygonInformation],
        kdims: Optional[Tuple[str, str]] = None,
        vdims: Optional[Tuple[str, str]] = None,
        tooltips: Optional[List[Tuple[str, str]]] = None,
        options: PolygonOptions = PolygonOptions(),
    ):
        """Create a plot with the selected polygons on it.

        Parameters
        ----------
        polygon_information: `list[PolygonInformation]`
            Polygon information, including the vertex
            and other data to be shown.
        kdims: `Optional[Tuple[str, str]]`
            X and Y vertex points values.
        vdims: `Optional[Tuple[str, str]]`
            Other column information to be shown.
        tooltipls: `Optional[List[Tuple[str, str]]]`
            On hoover text information.
        options: `PointsOptions`
            Polygon plot options.

        Returns
        -------
        plot: `hv.Points`
            Plot with the polygons draw on it.
        """
        assert isinstance(
            options, PolygonOptions
        ), "Not valid options type, should be PolygonOptions"
        region_poly = hv.Polygons(region_data, kdims=kdims, vdims=vdims).opts(
            **options.to_dict()
        )
        return region_poly
