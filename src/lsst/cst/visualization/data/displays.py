"""data science plot display utilities."""

import holoviews as hv
import logging

from bokeh.io import show
from bokeh.models import HoverTool  # noqa: F401
from bokeh.models import CDSView, BooleanFilter
from bokeh.plotting import figure, gridplot
from holoviews.operation.datashader import datashade, dynspread
from dataclasses import dataclass, field
from lsst.cst.visualization.params import PlotOptionsDefault
from lsst.cst.data.queries import DataWrapper
from typing import List, Optional, Union, Tuple
from collections.abc import Sequence

_log = logging.getLogger(__name__)


__all__ = ["HVScatterOptions",
           "DataShadeOptions",
           "FigureOptions",
           "ScatterOptions",
           "HistogramOptions"]


@dataclass
class HVScatterOptions:
    """Holoviews Scatter Options.

    Parameters
    ----------
    alpha: `float`, optional
        Plot points alpha value.
    color: `str,` optional
        Plot points color.
    invert_xaxis: `bool`, optional
        Invert xaxis of the plot.
    invert_yaxis: bool = False
        Invert xaxis of the plot.
    height: `int`, optional
        Height of the plot in pixels.
    marker: `str`, optional
        Plot points marker type.
    size: int, optional
        Plot points marker type.
    toolbar: `str`,  optional
        Toolbar position.
    tools: `List`, optional
        Plot tools available.
    width: `int`, optional
        Width of the plot in pixels.
    xlabel: str, optional
        xlabel value.
    ylabel: `str`
        ylabel value.
    fontsize: dict, optional
        dictionary selecting fontsize for different
        elements on the plot
    """
    alpha: float = 1.0
    color: str = PlotOptionsDefault.marker_color
    fontsize: dict[str, str] = field(default_factory=lambda: PlotOptionsDefault.fontsize)
    height: int = PlotOptionsDefault.height
    invert_xaxis: bool = False
    invert_yaxis: bool = False
    marker: str = PlotOptionsDefault.marker
    size: int | str = PlotOptionsDefault.marker_size
    title: Optional[str] = None
    toolbar_position: str = PlotOptionsDefault.toolbar_position
    tools: List = field(default_factory=list)
    width: int = PlotOptionsDefault.width
    xlabel: str = "X"
    ylabel: str = "Y"

    def to_dict(self):
        """Create and returns a dictionary from class attributes,
        where key is the name of the attribute and value its value.
        Instance attributes with None value will not be included.

        Returns
        -------
        options: `dict`
           Option key and values as dictionary.
        """
        ret_dict = dict(alpha=self.alpha,
                        color=self.color,
                        height=self.height,
                        invert_xaxis=self.invert_xaxis,
                        invert_yaxis=self.invert_yaxis,
                        marker=self.marker,
                        size=self.size,
                        title=self.title,
                        toolbar=self.toolbar_position,
                        tools=self.tools,
                        width=self.width,
                        xlabel=self.xlabel,
                        ylabel=self.ylabel,
                        fontsize=self.fontsize
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


@dataclass
class DataShadeOptions:
    """Datashade options

    Parameters
    ----------
    height: `int`, optional
        Height of the plot in pixels.
    cmap: `str`, optional
        color mapping to be applied
        to the Datashader plot.
    padding: `float`, optional
        Extra space is added around the data points in the plot.
    show_grid: `bool`, optional
        Show plot grid.
    xlabel: `str`, optional
        xlabel value.
    xlim: `Tuple[float, float]`, optional
        X axes limits.
    ylabel: `str`, optional
        ylabel value.
    ylim: `Tuple[float, float]`, optional
        Y axes limits.
    tools: List = field(default_factory=list)
        Plot tools available.
    width: `int`, optional
        Width of the plot in pixels.
    """
    height: int = PlotOptionsDefault.height
    cmap: str = "Viridis"
    padding: float = 0.05
    show_grid: bool = True
    xlabel: str = "X"
    xlim: Optional[Tuple[float, float]] = None
    ylabel: str = "Y"
    ylim: Optional[Tuple[float, float]] = None
    tools: List = field(default_factory=list)
    width: int = PlotOptionsDefault.width

    def to_dict(self):
        """Create and returns a dictionary from class attributes,
        where key is the name of the attribute and value its value.
        Instance attributes with None value will not be included.

        Returns
        -------
        options: `dict`
           Option key and values as dictionary.
        """
        ret_dict = dict(height=self.height,
                        padding=self.padding,
                        show_grid=self.show_grid,
                        tools=self.tools,
                        width=self.width,
                        xlabel=self.xlabel,
                        xlim=self.xlim,
                        ylabel=self.ylabel,
                        ylim=self.ylim
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


@dataclass
class FigureOptions:
    """Figure plot options.

    Parameters
    ----------
    fontsize: dict[str, str], optional
        Size of the diferent elements in the plot: title, xlabel, ylabel, ticks
    height: `int`, optional
        Height of the plot in pixels.
    tools: `List`, optional
        Figure tools available.
    width: `int`
        Width of the plot in pixels.
    xlabel: `str`, optional
        xlabel value.
    ylabel: `str`, optional
        ylabel value.
    """
    fontsize: dict[str, str] = field(default_factory=lambda: PlotOptionsDefault.fontsize)
    height: int = PlotOptionsDefault.height
    tools: List = field(default_factory=lambda:
                        ["pan,box_zoom,box_select,lasso_select,reset,help"])
    width: int = PlotOptionsDefault.width
    xlabel: str = "X"
    ylabel: str = "Y"

    def to_dict(self):
        """Create and returns a dictionary from class attributes,
        where key is the name of the attribute and value its value.
        Instance attributes with None value will not be included.

        Returns
        -------
        options: `dict`
           Option key and values as dictionary.
        """
        ret_dict = dict(fontsize=self.fontsize,
                        height=self.height,
                        tools=self.tools,
                        width=self.width,
                        x_axis_label=self.xlabel,
                        y_axis_label=self.ylabel,
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


@dataclass
class ScatterOptions:
    """Bokeh Scatter plot options.

    Parameters
    ----------
    alpha: `float`, optional
        Plot points alpha value.
    color: `str,` optional
        Plot points color.
    marker: `str`, optional
        Plot points marker type.
    size: int, optional
        Plot points marker type.
    """
    alpha: float = 1.0
    color: str = PlotOptionsDefault.marker_color
    marker: str = PlotOptionsDefault.marker
    size: int = PlotOptionsDefault.marker_size

    def to_dict(self):
        """Create and returns a dictionary from class attributes,
        where key is the name of the attribute and value its value.
        Instance attributes with None value will not be included.

        Returns
        -------
        options: `dict`
           Option key and values as dictionary.
        """
        ret_dict = dict(alpha=self.alpha,
                        color=self.color,
                        marker=self.marker,
                        size=self.size,
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


@dataclass
class HistogramOptions:
    """Plot histogram options

    Parameters
    ----------
    color: `str`, optional
        Histogram bars color.
    fontscale: `float`, optional
        Histogram labels fontsize.
    height: `int`, optional
        Height of the plot in pixels.
    title: str, optional
        Histogram title.
    xlabel: `str`, optional
        xlabel value.
    width: `int`, optional
        Width of the plot in pixels.
    ylabel: `str`, optional
        ylabel value.
    """
    color: str = PlotOptionsDefault.color
    fontscale: float = 1.2
    height: int = PlotOptionsDefault.height
    title: str = "No title"
    xlabel: str = 'X'
    width: int = PlotOptionsDefault.width
    ylabel: str = 'Y'

    def to_dict(self):
        """Create and returns a dictionary from class attributes,
        where key is the name of the attribute and value its value.
        Instance attributes with None value will not be included.

        Returns
        -------
        options: `dict`
           Option key and values as dictionary.
        """
        ret_dict = dict(color=self.color,
                        height=self.height,
                        fontscale=self.fontscale,
                        title=self.title,
                        xlabel=self.xlabel,
                        width=self.width,
                        ylabel=self.ylabel
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


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
    def __init__(self,
                 figure_id: str,
                 data: DataWrapper,
                 options: FigureOptions = FigureOptions()):
        self._figure_id = figure_id
        self._exposure_data = data
        self._figure = figure(**options.to_dict())

    def add_scatter(self,
                    x_data: str,
                    y_data: str,
                    hover_tool: None | HoverTool = None,
                    filter: None | Sequence[bool] = None,
                    options: ScatterOptions = ScatterOptions()
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
        index = self._exposure_data.index
        assert x_data in index, f"Selected data {x_data}"\
                                f"not available on exposure data"
        assert y_data in index, f"Selected data {y_data}"\
                                f"not available on exposure data"
        view = CDSView()
        if filter is not None:
            view.filter = BooleanFilter(filter)
        glyph = self._figure.scatter(
            x_data,
            y_data,
            source=self._exposure_data.get_column_data_source(),
            view=view,
            **options.to_dict()
        )
        if hover_tool is not None:
            # hover_tool.renderers.append(glyph)
            nhover_tool = HoverTool(
                renderers=[glyph],
                tooltips=hover_tool.tooltips,
                formatters=hover_tool.formatters
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
        self,
        identifier: str,
        figure_options: FigureOptions = FigureOptions()
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
        new_figure = DataFigure(identifier, self._exposure_data, figure_options)
        assert identifier not in self._figures.keys(), \
            f"Figure {identifier} already exists"
        self._figures[identifier] = new_figure
        return new_figure

    def _exchange_figures(
        self,
        layout: List[Union[str, List[...]]],
        new_layout: List[Union[figure, List[...]]]
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
        tools_position: str = "above"
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
        show(gridplot(new_layout), tools_position=tools_position, notebook_handle=True)

    def create_axe(
        self,
        data_identifier: str,
        label: Optional[str] = None,
        range: Optional[Tuple[float, float]] = None,
        unit: str = "N/A"
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
        assert data_identifier in index, f"Selected data {data_identifier}"\
                                         f"not available on exposure data"
        return hv.Dimension(data_identifier, label=label, range=(None, None), unit=unit)

    def show_scatter(
        self,
        columns: Optional[Tuple[hv.Dimension | str, hv.Dimension | str]] = None,
        options: ScatterOptions = ScatterOptions()
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
        data = self._exposure_data.data
        if columns is None:
            scatter = hv.Scatter(data).options(**options.to_dict())
        else:
            index = self._exposure_data.index
            data_x = columns[0]
            data_y = columns[1]
            if isinstance(data_x, str):
                assert data_x in index, f"Selected data {data_x} for X "\
                                        f"not available on exposure data"
            if isinstance(data_y, str):
                assert data_y in index, f"Selected data {data_y} for Y "\
                                        f"not available on exposure data"
            scatter = hv.Scatter(data, data_x, data_y).options(**options.to_dict())
        return scatter

    def show_data_shade(
        self,
        columns: Optional[Tuple[hv.Dimension | str, hv.Dimension | str]] = None,
        options: DataShadeOptions = DataShadeOptions()
    ):
        """Creates datashader plot using selected columns from data.

        Parameters
        ----------
        columns: `Tuple[hv.Dimension | str, hv.Dimension | str]`, optional
            Data columns selected to create the datashader plot,
            if non columns are passed the two first columns from 
            data will be used.

        options: ScatterOptions, optional
            Scatter plot options.

        Returns
        -------
        plot: `holoviews.core.spaces.DynamicMap`
            Datashader plot.
        """
        _log.debug("Applying datashade to data image.")
        scatter = self.show_scatter(columns)
        scatter = dynspread(datashade(scatter, cmap=options.cmap))
        scatter.opts(**options.to_dict())
        return scatter

    def show_histogram(self, field: 'str', options: HistogramOptions = HistogramOptions()):
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
        bin, count = self._exposure_data.histogram(field)
        return hv.Histogram((bin, count)).opts(**options.to_dict())
