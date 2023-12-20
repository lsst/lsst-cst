"""plot science utils"""

import gc
import numpy as np
import holoviews as hv
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from holoviews.operation.datashader import rasterize
from typing import Dict, List

from lsst.afw.image._exposure import ExposureF

__all__ = ["get_options", "Plot", "set_extension"]
_bokeh_extension_set = None
_extension_available = ['bokeh']


def set_extension(extension: str):
    """Function to set the extension used
    by the holoviews module.
    (Nowadays only 'bokeh' extension is available)
    """
    global _bokeh_extension_set
    if extension is not None:
        raise Exception("Extension already set")
    if extension not in _extension_available:
        raise Exception(f"Unknown extension: {extension}")
    hv.extension(extension)
    _bokeh_extension_set = extension


class Options(ABC):

    @abstractmethod
    def to_dict(self):
        NotImplementedError()


class NoOptions(Options):

    def to_dict(self):
        return {}


def get_options() -> Options:
    """
    Get options to modify the underlying Holoviews plot
    """
    if _bokeh_extension_set is None:
        raise Exception("Extension not set")
    if _bokeh_extension_set == 'bokeh':
        return _BokehOptions
    return NoOptions()


@dataclass(frozen=True)
class _BokehOptions(Options):
    """Image options class
    Parameters
    ----------
    cmap: `str`
        sets the colormap of the image, for example:
        Greys_r, viridis, plasma, inferno, magma, cividis or rainbow
    height: `int`
        Height of the plot in pixels
    width: `int``
        Width of the plot in pixels
    xaxis: `str`
        Position of the xaxis 'bottom', 'top'
    yaxis: `str`
        Position of the yaxis
    padding: `float`
        space around the plot
    font_size: `dict`
        Font size for axis labels, titles, and legend
    colorbar: `bool`
        adds a colorbar to the plot
    toolbar: `str``
        toolbar position 'left´, 'right', 'above', bellow'
    show_grid: `bool`
        displays grid lines on the plot.
    tools: `List[str]`
        List of Bokeh tools to include to the default ones
        ['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save']
    """
    cmap: str = "Greys_r"
    height: int = 600
    width: int = 700
    xaxis: str = "bottom"
    yaxis: str = "left"
    padding: float = 0.01
    font_size: Dict[str, str] = field(default_factory=lambda: {'title': '8pt'})
    colorbar: bool = True
    toolbar: str = 'right'
    show_grid: bool = True
    tools: List[str] = field(default_factory=lambda: ['hover'])

    def to_dict(self):
        return dict(cmap=self.cmap, height=self.height,
                    width=self.width, xaxis=self.xaxis, yaxis=self.yaxis,
                    padding=self.padding, fontsize=self.font_size,
                    colorbar=self.colorbar, toolbar=self.toolbar,
                    show_grid=self.show_grid, tools=self.tools)


class Plot:
    """
    Basic plot class
    Parameters
    ----------
    image_array: `np.ndarray`
        image array to be show in the plot

    """
    def __init__(self, image_array: np.ndarray):
        self._img = None
        self._image_array = image_array

    @classmethod
    def from_exposure(cls, exposure: ExposureF):
        """Create a basic plot class with an exposure as parameter

        Parameters
        ----------
        exposure: `exposureF`
            exposure instance returned from butler

        Returns
        -------
        results: `Plot``
            Plot instance with the array inside exposure as image data
        """
        return cls(exposure.image.array)

    def render(self, title, xlabel: str = 'X', ylabel: str = 'Y', options: Options = Options()):
        """Renders the array converting the array data into an holoviews Image
        Parameters
        ----------
        title: `str`
            title of the plot
        xlabel: `str`
            label for the x coordinates
        ylabel: `str`
            label for the y coordinates
        options: `Options`
            Options for the underlying plot object
        """
        assert self._img is None
        self._img = hv.Image(self._image_array, kdims=[xlabel, ylabel]).opts(
            xlabel=xlabel, ylabel=ylabel, title=title, **options.to_dict,
        )

    def show(self):
        """Show image into a notebook, the output_notebook must be enabled.
        The image is rasterized, in order to optimize the rendering of plots

        Returns
        -------
        results: `hv.DynamicMap`
        """
        assert self._img is not None
        return rasterize(self._img)

    def save(self, filename: str):
        """Save image as png in filename.

        Parameters
        ----------
        filename: `str``
            Name and path of the file where the image will be saved
        """
        assert self._img is not None
        hv.save(self._img, filename, fmt="png")

    def delete(self):
        """Delete underlying image
        """
        del self._img
        gc.collect()
