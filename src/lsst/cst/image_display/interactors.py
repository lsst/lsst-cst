"""data science image interactors."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

import holoviews as hv
import pandas as pd
import panel as pn
from bokeh.models import HoverTool
from holoviews import streams

from .displays import ImageDisplay
from .options import PointsOptions

__all__ = ["HoverSources", "BoxInteract", "OnClickInteract"]


class InteractiveDisplay(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def show(self):
        """Show interactive display."""
        raise NotImplementedError()


class HoverSources(InteractiveDisplay):
    """Interactive display including the sources.

    Parameters
    ----------
    options: `PointsOptions`, Optional
        Display points options.
    """

    options = PointsOptions

    def __init__(
        self,
        image_display: ImageDisplay,
        sources: Tuple[pd.Series],
        options=PointsOptions(),
    ):
        super().__init__()
        assert isinstance(image_display, ImageDisplay), (
            f"Could not create an interactive display from:"
            f"{type(image_display)}"
        )
        self._image_display = image_display
        self._options = options
        self._sources = sources
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
        self._image_display.render()
        coords = self._sources.x, self._sources.y
        self._img = hv.Points(coords).opts(
            **self._options.to_dict(), tools=[self._hover_tool]
        )
        return self._image_display.rasterize() * self._img

    def layout(self):
        raise NotImplementedError()


@dataclass
class BoxInteractOptions:
    """Interactive display selectable box options.

    Parameters
    ----------
    color: `str`, Optional
        Box color.
    """

    color: str = "red"


class BoxInteract(InteractiveDisplay):
    """Interactive plot with a selectable box tool to show extra information.

    Parameters
    ----------
    options: `BoxInteractOptions`, Optional
        Box plot options.
    """

    options = BoxInteractOptions

    def __init__(
        self, image_display: ImageDisplay, options=BoxInteractOptions()
    ):
        super().__init__()
        assert isinstance(image_display, ImageDisplay), (
            f"Could not create an interactive image_display from:"
            f"{type(image_display)}"
        )
        self._boundsxy = (0, 0, 0, 0)
        self._box = streams.BoundsXY(bounds=self._boundsxy)
        self._image_display = image_display
        self._options = options
        self._text_area_input = pn.widgets.TextAreaInput(
            name="Selected box bounds:", disabled=True, rows=2, width=500
        )

    def _set_bounds(self, bounds):
        #  Helper function to use as callback when box is created.
        self._text_area_input.value = str(bounds)
        return hv.Bounds(bounds)

    def show(self):
        self._image_display.render()
        dynamic_map = hv.DynamicMap(
            self._set_bounds, streams=[self._box]
        ).opts(color="red")
        interactive_image_display = (
            self._image_display.rasterize().opts(tools=["box_select"])
            * dynamic_map
        )
        layout = pn.Row(interactive_image_display, self._text_area_input)
        return layout


@dataclass
class OnClickInteractOptions:
    """Onclick interact display options

    Parameters
    ----------
    color: `str`, Optional
        Marker color.
    marker: `str`, Optional
        Marker type.
    size: int, Optional
        Marker size.
    """

    color: str = "white"
    marker: str = "x"
    size: int = 20


class OnClickInteract(InteractiveDisplay):
    """Interactive display with a tap tool to show extra information.

    Parameters
    ----------
    options: `OnClickInteract`, Optional
        Interact display options.
    """

    options = OnClickInteractOptions

    def __init__(
        self, image_display: ImageDisplay, options=OnClickInteractOptions()
    ):
        super().__init__()
        assert isinstance(image_display, ImageDisplay), (
            f"Could not create an interactive image display from:"
            f"{type(image_display)}"
        )
        self._posxy = hv.streams.Tap(x=0, y=0)
        self._image_display = image_display
        self._options = options
        self._text_area_input = pn.widgets.TextAreaInput(
            name="Selected box bounds:", disabled=True, rows=2, width=500
        )

    def _set_x_y(self, x, y):
        #  Helper function to use as callback when image_display is clicked
        self._text_area_input.value = (
            f"The scaled/raw value at position ({x:.3f}, {y:.3f}) is:\n"
            f"{self._image_display.image[-int(y), int(x)]:.3f}/"
            f"{self._image_display.transformed_image[-int(y), int(x)]:.3f}"
        )
        return hv.Points([(x, y)])

    def show(self):
        self._image_display.render()
        marker = hv.DynamicMap(self._set_x_y, streams=[self._posxy])
        interactive_image_display = (
            self._image_display.rasterize()
            * marker.opts(
                color=self._options.color,
                marker=self._options.marker,
                size=self._options.size,
            )
        )
        layout = pn.Row(interactive_image_display, self._text_area_input)
        return layout
