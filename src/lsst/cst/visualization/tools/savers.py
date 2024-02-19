"""data science saver plot tools."""
import os
from abc import ABC, abstractmethod

import holoviews as hv
from panel.layout.base import Panel

from lsst.cst.visualization.image.displays import ImageDisplay, get_extension
from lsst.cst.visualization.image.interactors import _InteractiveDisplay

__all__ = ["save_plot_as_html"]


def save_plot_as_html(plot: Panel, filename: str):
    """Function to save a plot created with
    helper functions as an html file

    Parameters
    ----------
    plot: `hv.Layout`
        Plot to be saved.
    filename: `str`
        Name of the file where plot will be saved,
        including path and extension.
    """
    if isinstance(plot, Panel):
        plot.save(filename)
    else:
        raise Exception(
            f"Unable to save plot type:" f"{type(plot)} using this function"
        )


class Saver(ABC):
    """Saver interface."""

    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__()
        self._output_dir = output_dir

    @abstractmethod
    def save(self):
        """Save Image display"""
        raise NotImplementedError()


class _ImageDisplaySaver(ABC):
    """Image display saver"""

    @abstractmethod
    def save(self):
        raise NotImplementedError()


class _HVHtmlImageDisplaySaver(_ImageDisplaySaver):
    """Image display saver"""

    def __init__(self, image_display: ImageDisplay):
        self._image_display = image_display

    def save(self, filename):
        img = self._image_display.rasterize()
        hv.save(img, filename, backend=get_extension().value)


class _PanelHtmlLayoutSaver(_ImageDisplaySaver):
    """Save panel as html file."""

    def __init__(self, interactive_display: _InteractiveDisplay):
        self._interactive_display = interactive_display

    def save(self, filename):
        self._interactive_display.show().save(filename, embed=True)


class HTMLSaver(Saver):
    """HTML plot saver"""

    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__(output_dir)

    def save(self, plot: ImageDisplay | _InteractiveDisplay, filename: str):
        """Save image as html in filename.

        Parameters
        ----------
        filename: `str`
            Name and path of the file where the image will be saved.
        """
        output_file_base_name = f"{filename}"
        output_file = os.path.join(self._output_dir, output_file_base_name)
        if isinstance(plot, ImageDisplay):
            saver = _HVHtmlImageDisplaySaver(plot)
        elif isinstance(plot, _InteractiveDisplay):
            saver = _PanelHtmlLayoutSaver(plot)
        else:
            raise Exception("Unable to save plot of this type")
        saver.save(output_file)
        return output_file
