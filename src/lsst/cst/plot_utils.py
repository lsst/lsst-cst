"""Plot science utils."""

import gc
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

import holoviews as hv
from bokeh.models import HoverTool
from holoviews.operation.datashader import rasterize
from pandas import Series

from lsst.afw.image._exposure import ExposureF
from lsst.cst.data_utils import (
    CalExpData,
    ImageTransform,
    NoImageTransform,
    StandardImageTransform,
)

_log = logging.getLogger(__name__)


__all__ = ["Plot", "CalExpPlot", "ExposurePlot", "ImageOptions", "PointsOptions", "Options"]


class Extension(Enum):
    BOKEH = "bokeh"


_extension_set = None  # type: Extension
_extension_available = [Extension.BOKEH]


def _set_extension(extension: Extension = Extension.BOKEH):
    """Function to set the extension used
    by the holoviews module.
    (Nowadays only 'bokeh' extension is available).
    """
    global _extension_set
    if _extension_set is not None:
        raise Exception("Extension already set")
    if extension not in _extension_available:
        raise Exception(f"Unknown extension: {extension}")
    hv.extension(extension.value)
    _extension_set = extension


_set_extension()


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


def _get_options(options_type: str) -> Options:
    # Helper function to get options type
    if _extension_set is None:
        raise Exception("Extension not set")
    if _extension_set == Extension.BOKEH:
        if options_type == "image":
            return ImageOptions
        elif options_type == "points":
            return PointsOptions
    return NoOptions


@dataclass
class PointsOptions(Options):
    """Points plot options

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

    fill_color: str = None  # "this is it"
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
    font_size: `dict`
        Font size for axis labels, titles, and legend.
    colorbar: `bool`
        adds a colorbar to the plot.
    toolbar: `str`
        toolbar position 'left', 'right', 'above', bellow'.
    show_grid: `bool`
        displays grid lines on the plot.
    tools: `list`
        List of Bokeh tools to include to the default ones.
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
    tools: List[str] = field(default_factory=lambda: [])

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


class Plot(ABC):
    """Plot interface image.
    """

    def __init__(self):
        super().__init__()
        self._img = None

    @abstractmethod
    def render(self):
        """Render the image.
        """
        raise NotImplementedError()

    @abstractmethod
    def show(self):
        """Show the image.
        """
        raise NotImplementedError()

    @abstractmethod
    def rasterize(self):
        """Rasterize the image.
        """
        raise NotImplementedError()

    def delete(self):
        """Delete underlying image.
        """
        assert self._img is not None
        del self._img
        gc.collect()

    @staticmethod
    def from_exposure(
        exposure: ExposureF,
        title: str = "No title",
        xlabel: str = "X",
        ylabel: str = "Y",
        image_options: ImageOptions = ImageOptions(),
    ):
        """Create a Plot class for the exposureF image.

        Parameters
        ----------
        exposure: `~lsst.afw.image._exposure.ExposureF`
            exposure instance returned from butler.
        title: `str`
            title of the plot.
        xlabel: `str`
            label for the x coordinates.
        ylabel: `str`
            label for the y coordinates.
        image_options: `ImageOptions`
            Options for the underlying plot object.

        Returns
        -------
        results: `Plot`
            Plot instance for the exposureF
        """
        return ExposurePlot(exposure, title, xlabel, ylabel, image_options)

    @staticmethod
    def from_cal_exp_data(
        cal_exp_data: CalExpData,
        title: str = None,
        xlabel: str = "X",
        ylabel: str = "Y",
        show_detections: bool = True,
        image_options: ImageOptions = ImageOptions(),
        sources_options: PointsOptions = PointsOptions(),
    ):
        """Create a Plot class for CalExpData.

        Parameters
        ----------
        exposure: `~lsst.afw.image._exposure.ExposureF`
            exposure instance returned from butler.
        title: `str`
            title of the plot.
        xlabel: `str`
            label for the x coordinates.
        ylabel: `str`
            label for the y coordinates.
        image_options: `ImageOptions`
            Options for the underlying plot object.
        sources_options: `PointsOptions`
            Options for the underlying sources plot object.

        Returns
        -------
        results: `Plot`
            Plot instance for the exposureF including sources.
        """
        return CalExpPlot(
            cal_exp_data,
            title,
            xlabel,
            ylabel,
            show_detections,
            image_options,
            sources_options,
        )

    @staticmethod
    def from_points(
        sources: tuple[Series], options: PointsOptions = PointsOptions()
    ):
        """Create a Plot for the sources

        Parameters
        ----------
        sources: `tuple`
            Points to be plotted.
        options: `PointsOptions`
            Options for the points to be plotted.

        Returns
        -------
        results: `Plot`
            Plot of the points.
        """
        return PointsPlot(sources, options)


class PointsPlot(Plot):
    """Plot for selected points

    Parameters
    ----------
    points: `tuple[Series]`
        Points to be add to the plot.
    options: `PointsOptions`, Optional
        Points plot options
    """

    options = PointsOptions

    def __init__(
        self, points: tuple[Series], options: PointsOptions = PointsOptions()
    ):
        super().__init__()
        self._points = points
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

    def render(self):
        self._img = hv.Points(self._points).opts(
            **self._options.to_dict(), tools=[self._hover_tool]
        )

    def show(self):
        return self._img

    def rasterize(self):
        raise NotImplementedError()


class ExposurePlot(Plot):
    """Plot for an ExposureF

    Parameters
    ----------
    image_array: `numpy.ndarray`
        image array to be show in the plot.
    title: `str`
        title of the plot.
    xlabel: `str`
        label for the x coordinates.
    ylabel: `str`
        label for the y coordinates.
    options: `Options`
        Options for the underlying plot object.
    """

    _options = ImageOptions

    def __init__(
        self,
        exposure: ExposureF,
        title: str = None,
        xlabel: str = "X",
        ylabel: str = "Y",
        options: ImageOptions = ImageOptions(),
    ):
        self._exposure = exposure
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._img = None
        self._options = options
        self._image_transform = NoImageTransform()
        self._image_bounds = None

    def _set_image_transform(self, image_transform: ImageTransform):
        """Setter to change the image transformer before rendering the image.

        Parameters
        ----------
        image_transform: `ImageTransform`
            New image transformation image to be applied when
            rendering the plot
        """
        assert isinstance(image_transform, ImageTransform), ""
        self._image_transform = image_transform

    def render(self):
        assert self._img is None
        if self._image_bounds is None:
            self._image_bounds = (
                0,
                0,
                self._exposure.getDimensions()[0],
                self._exposure.getDimensions()[1],
            )
        array = self._image_transform.transform(self._exposure.image.array)
        self._img = hv.Image(
            array,
            bounds=self._image_bounds,
            kdims=[self._xlabel, self._ylabel],
        ).opts(
            title=self._title,
            xlabel=self._xlabel,
            ylabel=self._ylabel,
            **self._options.to_dict(),
        )

    def show(self):
        assert self._img is not None
        return self._img

    def rasterize(self):
        assert self._img is not None
        return rasterize(self._img)

    image_transform = property(fget=None, fset=_set_image_transform)


class CalExpPlot(Plot):
    """Plot using Calexp data, includes the image and also the sources.

    Parameters
    ----------
    cal_exp_data: `CalExpData`
        cal exp data to be plot
    title: `str`, Optional
        Plot title. Default value: CalExpId information.
    xlabel: `str`, Optional
        Plot xlabel. Default value: 'X'.
    ylabel: `str`, Optional
        Plot ylabel. Default value: 'Y'.
    show_detections: `bool`, Optional
        True if detections should be added to the plot. Default value: True.
    image_options: `ImageOptions`, Optional
        Image options.
    source_options: `PointsOptions`, Optional
        Source options.
    """

    options = ImageOptions
    detect_options = PointsOptions

    def __init__(
        self,
        cal_exp_data: CalExpData,
        title: str = None,
        xlabel: str = "X",
        ylabel: str = "Y",
        show_detections: bool = True,
        image_options: ImageOptions = ImageOptions(),
        source_options: PointsOptions = PointsOptions(),
    ):
        super().__init__()
        self._cal_exp_data = cal_exp_data
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._source_options = source_options
        self._image_options = image_options
        self._detections = None
        self._show_detections = show_detections

    def render(self):
        assert self._img is None
        assert self._detections is None
        if self._title is None:
            self._title = self._cal_exp_data.cal_exp_id
        self._img = Plot.from_exposure(
            exposure=self._cal_exp_data.get_calexp(),
            title=self._title,
            xlabel=self._xlabel,
            ylabel=self._ylabel,
            image_options=self._image_options,
        )
        self._img.image_transform = StandardImageTransform()
        self._img.render()
        if self._show_detections:
            self._detections = Plot.from_points(
                self._cal_exp_data.get_sources(), self._source_options
            )
            self._detections.render()

    def show(self):
        assert self._img is not None
        if self._show_detections:
            assert self._detections is not None
            return self._img.show() * self._detections.show()
        else:
            return self._img.show()

    def rasterize(self):
        assert self._img is not None
        if self._show_detections:
            assert self._detections is not None
            return self._img.rasterize() * self._detections.show()
        else:
            return self._img.rasterize()

    def delete(self):
        if self._detections is not None:
            self._detections.delete()
        super().delete()


class PlotSaver(ABC):

    def __init__(self):
        super().__init__(output_dir: str = os.path.expanduser("~"))
        self._output_dir = output_dir

    @abstractmethod
    def save(self):
        raise NotImplementedError()


class HTMLSaver(PlotSaver):

    def __init__(self):
        super().__init__()


    def save(self, plot: Plot, filename: str):
        """Save image as html in filename.

        Parameters
        ----------
        filename: `str`
            Name and path of the file where the image will be saved.
        """
        img = plot._img.rasterize()
        output_file_base_name = f"{filename}.html"
        outputFile = os.path.join(self._output_dir, output_file_base_name)
        hv.save(img, outputFile, backend=_extension_set)
