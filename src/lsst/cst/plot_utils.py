"""plot science utils"""

import gc
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List
from pandas import Series

import holoviews as hv
from holoviews.operation.datashader import rasterize
from bokeh.models import HoverTool
import numpy as np

from lsst.afw.image._exposure import ExposureF
from data_utils import CalExpData

__all__ = ["Plot", "set_extension"]
_bokeh_extension_set = None
_extension_available = ["bokeh"]


def set_extension(extension: str):
    """Function to set the extension used
    by the holoviews module.
    (Nowadays only 'bokeh' extension is available)
    """
    global _bokeh_extension_set
    if _bokeh_extension_set is not None:
        raise Exception("Extension already set")
    if extension not in _extension_available:
        raise Exception(f"Unknown extension: {extension}")
    hv.extension(extension)
    _bokeh_extension_set = extension


class Options(ABC):
    """
    """
    @abstractmethod
    def to_dict(self):
        NotImplementedError()


class NoOptions(Options):
    """
    """
    def to_dict(self):
        return {}


def _get_options(options_type: str) -> Options:
    """
    Get options to modify the underlying Holoviews plot
    """
    if _bokeh_extension_set is None:
        raise Exception("Extension not set")
    if _bokeh_extension_set == "bokeh":
        if options_type == "image":
            return _BokehImageOptions
        elif options_type == "points":
            return _BokehPointsOptions
        elif options_type == "exposure_data":
            return _BokehExposureOptions
    return NoOptions


@dataclass(frozen=True)
class _BokehPointsOptions(Options):
    """.env"""
    fill_color: str
    size: int
    color: str


@dataclass(frozen=True)
class _BokehImageOptions(Options):
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
        toolbar position 'left', 'right', 'above', bellow'
    show_grid: `bool`
        displays grid lines on the plot.
    tools: `List[str]`
        List of Bokeh tools to include to the default ones
        []
    """

    cmap: str = "Greys_r"
    height: int = 600
    width: int = 700
    xaxis: str = "bottom"
    yaxis: str = "left"
    padding: float = 0.01
    font_size: Dict[str, str] = field(default_factory=lambda: {"title": "8pt"})
    colorbar: bool = True
    toolbar: str = "right"
    show_grid: bool = True
    tools: List[str] = field(default_factory=lambda: ["hover"])

    def to_dict(self):
        return dict(
            cmap=self.cmap,
            height=self.height,
            width=self.width,
            xaxis=self.xaxis,
            yaxis=self.yaxis,
            padding=self.padding,
            fontsize=self.font_size,
            colorbar=self.colorbar,
            toolbar=self.toolbar,
            show_grid=self.show_grid,
            tools=self.tools,
        )


class _BokehExposureOptions(_BokehImageOptions):
    """"""
    show_detections: bool = True


class Plot(ABC):
    """.env"""

    def __init__(self):
        super().__init__()
        self._img = None

    @abstractmethod
    def render(
        self,
        options: Options = NoOptions(),
    ):
        """.env"""
        raise NotImplementedError()

    @abstractmethod
    def show(self):
        """.env"""
        raise NotImplementedError()

    @abstractmethod
    def rasterize(self):
        """.env"""
        raise NotImplementedError()

    @abstractmethod
    def delete(self):
        """Delete underlying image"""
        assert self._img is not None
        del self._img
        gc.collect()

    @staticmethod
    def from_exposure(exposure: ExposureF, title: str = "No title",
                      xlabel: str = "X", ylabel: str = "Y"):
        """Create a basic plot class with an exposure as parameter

        Parameters
        ----------
        exposure: `exposureF`
            exposure instance returned from butler

        Returns
        -------
        results: `Plot`
            Plot instance with the array inside exposure as image data
        """
        return ImagePlot(exposure.image.array)

    @staticmethod
    def from_exposure_data(cal_exp_data: CalExpData, title: str = "No title",
                           xlabel: str = "X", ylabel: str = "Y"):
        """
        """
        return CalExpDataPlot(cal_exp_data)

    @staticmethod
    def from_points(sources: tuple[Series]):
        """
        """
        return PointsPlot(sources)


class PointsPlot(Plot):

    _options = None

    def __init__(self, points: tuple[Series]):
        super().__init__()
        self._points = points
        self._hover_tool = HoverTool(
            tooltips=[
                ('X', '@x{0.2f}'),
                ('Y', '@y{0.2f}'),
            ],
            formatters={
                'X': 'printf',
                'Y': 'printf',
            },
        )

    @staticmethod
    @property
    def options():
        """"""
        if PointsPlot._options is None:
            PointsPlot._options = _get_options("points")
        return PointsPlot._options

    @abstractmethod
    def render(
        self,
        options: _BokehPointsOptions = _BokehPointsOptions(),
    ):
        """.env"""
        self._img = hv.Points(self._points).opts(options.to_dict(), tools=[self._hover_tool])

    @abstractmethod
    def show(self):
        """.env"""
        return self._img

    @abstractmethod
    def rasterize(self):
        """.env"""
        raise NotImplementedError()


class ImagePlot(Plot):
    """
    Basic plot class
    Parameters
    ----------
    image_array: `np.ndarray`
        image array to be show in the plot

    """
    _options = None

    def __init__(self, image_array: np.ndarray, title: str = "No title",
                 xlabel: str = "X", ylabel: str = "Y"):
        self._image_array = image_array
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel

    @staticmethod
    @property
    def options():
        """"""
        if ImagePlot._options is None:
            ImagePlot._options = _get_options("image")
        return ImagePlot._options

    def render(
        self,
        options: _BokehImageOptions = _BokehImageOptions(),
    ):
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
        assert isinstance(options, _BokehImageOptions)
        assert self._img is None
        self._img = hv.Image(self._image_array, kdims=[self._xlabel, self._ylabel]).opts(
            title=self._title,
            xlabel=self._xlabel,
            ylabel=self._ylabel,
            **options.to_dict(),
        )

    def show(self):
        """.env"""
        assert self._img is not None
        return self._img

    def rasterize(self):
        """Show image into a notebook, the output_notebook must be enabled.
        The image is rasterized, in order to optimize the rendering of plots

        Returns
        -------
        results: `hv.DynamicMap`
        """
        assert self._img is not None
        return rasterize(self._img)

    def save_to_html(self, filename: str):
        """Save image as html in filename.

        Parameters
        ----------
        filename: `str``
            Name and path of the file where the image will be saved
        """
        assert self._img is not None
        output_dir = os.path.expanduser("~")
        output_file_base_name = f"{filename}.html"
        outputFile = os.path.join(output_dir, output_file_base_name)
        hv.save(self._img, outputFile, backend=_bokeh_extension_set())


class CalExpDataPlot(Plot):
    """"""

    _options = None

    def __init__(self, exposure_data: CalExpData, title: str = "No title",
                 xlabel: str = "X", ylabel: str = "Y",
                 source_options: _BokehPointsOptions = _BokehPointsOptions()):
        super.__init__()
        self._exposure_data = exposure_data
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._source_options = source_options
        self._img = None
        self._detections = None
        self._show_detections = False

    @staticmethod
    @property
    def options():
        """"""
        if CalExpDataPlot._options is None:
            CalExpDataPlot._options = _get_options("exposure_data")
        return CalExpDataPlot._options

    def render(
        self,
        options: _BokehExposureOptions = _BokehExposureOptions(),
    ):
        """"""
        assert isinstance(options, _BokehExposureOptions)
        self._show_detections = options.show_detections
        self._img = Plot.from_exposure(self._exposure_data.get_exposure())
        self._img.render(options)
        self._detections = Plot.from_points(self._exposure_data.get_sources())
        self._detections.render(self._source_options)

    def show(self):
        """"""
        if self._show_detections:
            return self._img.show() * self._detections.show()
        else:
            return self._img.show()

    def rasterize(self):
        """"""
        if self._show_detections:
            return self._img.show() * self._detections.show()
        else:
            return self._img.rasterize()

    def delete(self):
        """.env"""
        self._detections.delete()
        super().delete()
