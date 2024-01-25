import holoviews as hv
from holoviews import streams
from abc import ABC, abstractmethod
import panel as pn
from dataclasses import dataclass

from bokeh.models import HoverTool
from lsst.cst.plot import Plot, Options


__all__ = ["HoverSources", "BoxInteract", "TapInteract"]


class _InteractivePlot(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def show(self):
        """Show interactive plot.
        """
        raise NotImplementedError()


@dataclass
class PointsOptions(Options):
    """Points plot options.

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
    marker: str = "o"

    def to_dict(self):
        """Points options as dictionary.

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


class HoverSources(_InteractivePlot):
    """Interactive plot including the sources over the plot.

    Parameters
    ----------
    options: `PointsOptions`, Optional
        Points plot options.
    """

    options = PointsOptions

    def __init__(self, plot: Plot, options=PointsOptions()):
        super().__init__()
        self._plot = plot
        self._options = options
        self._hover_tool = HoverTool(
            tooltips=[
                ("X", "@x{0.2f}"),
                ("Y", "@y{0.2f}"),
            ],
            formatters={
                "X": "printf",
                "Y": "printf",
            },
        )

    def show(self):
        self._plot.render()
        points = self._plot.sources
        self._img = hv.Points(points).opts(
            **self._options.to_dict(), tools=[self._hover_tool]
        )
        return pn.Row(self._plot.rasterize() * self._img)

    def layout(self):
        raise NotImplementedError()


@dataclass
class BoxInteractOptions:
    """Interactive plot including the sources over the plot.

    Parameters
    ----------
    options: `PointsOptions`, Optional
        Points plot options.
    """

    color: str = 'red'


class BoxInteract(_InteractivePlot):
    """Interactive plot with a selectable box tool to show extra information.

    Parameters
    ----------
    options: `BoxInteractOptions`, Optional
        Box plot options
    """

    options = BoxInteractOptions

    def __init__(self, plot: Plot, options=BoxInteractOptions()):
        super().__init__()
        self._boundsxy = (0, 0, 0, 0)
        self._box = streams.BoundsXY(bounds=self._boundsxy)
        self._plot = plot
        self._options = options
        self._text_area_input = pn.widgets.TextAreaInput(name='Selected box bounds:',
                                                         disabled=True, rows=2, width=500)

    def _set_bounds(self, bounds):
        #  Helper function to use as callback when box is created.
        self._text_area_input.value = str(bounds)
        return hv.Bounds(bounds)

    def show(self):
        self._plot.render()
        dynamic_map = hv.DynamicMap(self._set_bounds, streams=[self._box]).opts(color='red')
        interactive_plot = self._plot.rasterize().opts(tools=['box_select']) * dynamic_map
        layout = pn.Row(interactive_plot, self._text_area_input)
        return layout


@dataclass
class TapInteractOptions:
    """
    """
    color: str = 'white'
    marker: str = 'x'
    size: int = 20


class TapInteract(_InteractivePlot):
    """Interactive plot with a tap tool to show extra information.

    Parameters
    ----------
    options: `BoxInteractOptions`, Optional
        Box plot options.
    """

    options = TapInteractOptions

    def __init__(self, plot: Plot, options=TapInteractOptions()):
        super().__init__()
        self._posxy = hv.streams.Tap(x=0, y=0)
        self._plot = plot
        self._options = options
        self._text_area_input = pn.widgets.TextAreaInput(name='Selected box bounds:',
                                                         disabled=True, rows=2, width=500)

    def _set_x_y(self, x, y):
        #  Helper function to use as callback when plot is tap
        self._text_area_input.value = f"The scaled/raw value at position ({x:.3f}, {y:.3f}) is:\n"\
                                      f"{self._plot.image[-int(y), int(x)]:.3f}/"\
                                      f"{self._plot.transformed_image[-int(y), int(x)]:.3f}"
        return hv.Points([(x, y)])

    def show(self):
        self._plot.render()
        marker = hv.DynamicMap(self._set_x_y, streams=[self._posxy])
        interactive_plot = self._plot.rasterize() * marker.opts(color=self._options.color,
                                                                marker=self._options.marker,
                                                                size=self._options.size)
        layout = pn.Row(interactive_plot, self._text_area_input)
        return layout
