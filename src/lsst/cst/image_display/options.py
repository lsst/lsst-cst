from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from lsst.cst.utilities.parameters import PlotOptionsDefault


class Options(ABC):
    """Interface with the indispensable methods of how an Option
    class should act like.
    """

    @abstractmethod
    def to_dict(self):
        """Returns a dictionary with the keys as option name and the values
        as the option value.
        """
        NotImplementedError()


class NoOptions(Options):
    """No Options."""

    def to_dict(self):
        return {}


@dataclass
class ImageOptions(Options):
    """Image plot options.

    Parameters
    ----------
    cmap: `str`
        sets the colormap of the image, for example:
        Greys_r, viridis, plasma, inferno, magma, cividis or rainbow.
    height: `int`
        Height of the plot in pixels.
    width: `int`
        Width of the plot in pixels.
    xaxis: `str`
        Position of the xaxis 'bottom', 'top'.
    yaxis: `str`
        Position of the yaxis.
    padding: `float`
        space around the plot.
    fontsize: `dict`
        Font size for axis labels, titles, and legend.
    toolbar: `str`
        toolbar position 'left', 'right', 'above', bellow'.
    show_grid: `bool`
        displays grid lines on the plot.
    tools: `list`
        List of Bokeh tools to include to the default ones.
    """

    cmap: Optional[str] = None
    height: int = PlotOptionsDefault.height
    padding: float = 0.01
    fontsize: Dict[str, str] = field(
        default_factory=lambda: PlotOptionsDefault.fontsize
    )
    toolbar_position: str = "right"
    show_grid: bool = PlotOptionsDefault.show_grid
    tools: List[str] = field(default_factory=lambda: [])
    width: int = PlotOptionsDefault.width
    xaxis: str = "bottom"
    yaxis: str = "left"

    def to_dict(self):
        ret_dict = dict(
            cmap=self.cmap,
            height=self.height,
            width=self.width,
            xaxis=self.xaxis,
            yaxis=self.yaxis,
            padding=self.padding,
            fontsize=self.fontsize,
            toolbar=self.toolbar_position,
            show_grid=self.show_grid,
            tools=self.tools,
        )
        filtered_dict = {
            key: value for key, value in ret_dict.items() if value is not None
        }
        return filtered_dict


@dataclass
class PointsOptions(Options):
    """Display points options.

    Parameters
    ----------
    fill_color: `str`
        Marker fill color.
    size: `int`
        Marker size
    color: `int`
        Marker color.
    marker: `str`
        Marker type.
    """

    fill_color: str = None
    size: int = 9
    color: str = "darkorange"
    marker: str = "circle"

    def to_dict(self):
        """Options as dictionary.

        Returns
        -------
        options: `dict`
            Selected options as a dictionary.
        """
        return dict(
            fill_color=self.fill_color,
            size=self.size,
            color=self.color,
            marker=self.marker,
        )
