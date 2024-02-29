from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from lsst.cst.utilities import PlotOptionsDefault

__all__ = [
    "HVScatterOptions",
    "DataShadeOptions",
    "FigureOptions",
    "ScatterOptions",
    "HistogramOptions",
    "PointsOptions",
    "PolygonOptions",
]


@dataclass
class HVScatterOptions:
    """Holoviews Scatter Options.

    Parameters
    ----------
    alpha: `float`, optional
        Plot points alpha value.
    color: `str,` optional
        Plot points color.
    fontsize: dict, optional
        dictionary selecting fontsize for different
        elements on the plot.
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
    """

    alpha: float = 1.0
    color: str = PlotOptionsDefault.marker_color
    fontsize: Dict[str, str] = field(
        default_factory=lambda: PlotOptionsDefault.fontsize
    )
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
        ret_dict = dict(
            alpha=self.alpha,
            color=self.color,
            fontsize=self.fontsize,
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
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }
        return filtered_dict


@dataclass
class DataShadeOptions:
    """Datashade options

    Parameters
    ----------
    cmap: `str`, optional
        color mapping to be applied
        to the Datashader plot.
    fontsize: dict[str, str], optional
        Size of the diferent elements in the plot: title,
        xlabel, ylabel, ticks.
    height: `int`, optional
        Height of the plot in pixels.
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

    cmap: str = "Viridis"
    fontsize: Dict[str, str] = field(
        default_factory=lambda: PlotOptionsDefault.fontsize
    )
    height: int = PlotOptionsDefault.height
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
        ret_dict = dict(
            fontsize=self.fontsize,
            height=self.height,
            padding=self.padding,
            show_grid=self.show_grid,
            tools=self.tools,
            width=self.width,
            xlabel=self.xlabel,
            xlim=self.xlim,
            ylabel=self.ylabel,
            ylim=self.ylim,
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }
        return filtered_dict


@dataclass
class FigureOptions:
    """Figure plot options.

    Parameters
    ----------
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

    height: int = PlotOptionsDefault.height
    tools: List = field(
        default_factory=lambda: [
            "pan,box_zoom,box_select,lasso_select,reset,help"
        ]
    )
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
        ret_dict = dict(
            fontsize=self.fontsize,
            height=self.height,
            tools=self.tools,
            width=self.width,
            x_axis_label=self.xlabel,
            y_axis_label=self.ylabel,
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }

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
        Plot points marker size.
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
        ret_dict = dict(
            alpha=self.alpha,
            color=self.color,
            marker=self.marker,
            size=self.size,
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }
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
        Plot title.
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
    xlabel: str = "X"
    width: int = PlotOptionsDefault.width
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
        ret_dict = dict(
            color=self.color,
            height=self.height,
            fontscale=self.fontscale,
            title=self.title,
            xlabel=self.xlabel,
            width=self.width,
            ylabel=self.ylabel,
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }
        return filtered_dict


@dataclass
class PolygonOptions:
    """Polygon plot options.

    Parameters
    ----------
    alpha: `float`, optional
        Polygons alpha value.
    cmap: `dict[str, str]`, optional
        Color map.
    color: `str`
        Polygon fill color.
    height: `int`, optional
        Height of the plot in pixels.
    tools: `List`, optional
        Plot tools available.
    hover_alpha: `float`, optional
        Polygon alpha value on hover.
    line_color: `List`, optional
        Polygon line color.
    line_alpha: `List`, optional
        Polygon line alpha value.
    title: str, optional
        Plot title.
    width: `int`, optional
        Width of the plot in pixels.
    xlabel: str, optional
        xlabel value.
    ylabel: `str`
        ylabel value.
    """

    alpha: float = 0.0
    cmap: dict[str, str] = None
    color: str = None
    height: int = PlotOptionsDefault.height
    tools: [] = None
    hover_alpha: float = 0.3
    line_color: str = "blue"
    line_alpha: float = 1.0
    title: Optional[str] = None
    width: int = PlotOptionsDefault.width
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None

    def to_dict(self):
        """Create and returns a dictionary from class attributes,
        where key is the name of the attribute and value its value.
        Instance attributes with None value will not be included.

        Returns
        -------
        options: `dict`
           Option key and values as dictionary.
        """
        ret_dict = dict(
            alpha=self.alpha,
            cmap=self.cmap,
            color=self.color,
            height=self.height,
            hover_alpha=self.hover_alpha,
            line_color=self.line_color,
            line_alpha=self.line_alpha,
            tools=self.tools,
            title=self.title,
            width=self.width,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }
        return filtered_dict


@dataclass
class PointsOptions:
    """Points plot options.

    Parameters
    ----------
    alpha: `float`, optional
        Plot points alpha value.
    color: `str`, optional
        Plot points color.
    fontsize: dict[str, str], optional
        Size of the diferent elements in the plot: title,
        xlabel, ylabel, ticks.
    height: `int`, optional
        Height of the plot in pixels.
    size: int, optional
        Points marker size.
    title: str, optional
        Plot title.
    width: `int`, optional
        Width of the plot in pixels.
    xlabel: str, optional
        xlabel value.
    ylabel: `str`
        ylabel value.
    """

    alpha: float = 1.0
    color: str = PlotOptionsDefault.marker_color
    fontsize: Dict[str, str] = field(
        default_factory=lambda: PlotOptionsDefault.fontsize
    )
    height: int = PlotOptionsDefault.height
    size: int | str = PlotOptionsDefault.marker_size
    title: Optional[str] = None
    width: int = PlotOptionsDefault.width
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None

    def to_dict(self):
        """Create and returns a dictionary from class attributes,
        where key is the name of the attribute and value its value.
        Instance attributes with None value will not be included.

        Returns
        -------
        options: `dict`
           Option key and values as dictionary.
        """
        ret_dict = dict(
            alpha=self.alpha,
            color=self.color,
            fontsize=self.fontsize,
            height=self.height,
            size=self.size,
            title=self.title,
            width=self.width,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }
        return filtered_dict
