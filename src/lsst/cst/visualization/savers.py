import os
from abc import ABC, abstractmethod

import holoviews as hv

from lsst.cst.visualization.image.interactors import _InteractiveDisplay
from lsst.cst.visualization.image.displays import ImageDisplay, get_extension

__all__ = "HTMLSaver"


class Saver(ABC):
    """Saver interface.
    """
    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__()
        self._output_dir = output_dir

    @abstractmethod
    def save(self):
        """
        """
        raise NotImplementedError()


class _ImageDisplaySaver(ABC):
    """
    """
    @abstractmethod
    def save(self):
        raise NotImplementedError()


class _HVHtmlImageDisplaySaver(_ImageDisplaySaver):
    """
    """
    def __init__(self, image_display: ImageDisplay):
        self._image_display = image_display

    def save(self, filename):
        img = self._image_display.rasterize()
        hv.save(img, filename, backend=get_extension().value)


class _PanelHtmlLayoutSaver(_ImageDisplaySaver):
    """Save panel as html file.
    """
    def __init__(self, interactive_display: _InteractiveDisplay):
        self._interactive_display = interactive_display

    def save(self, filename):
        self._interactive_display.show().save(filename, embed=True)


class HTMLSaver(Saver):
    """HTML plot saver
    """

    _extension = "html"

    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__(output_dir)

    def save(self, plot: ImageDisplay | _InteractiveDisplay, filename: str):
        """Save image as html in filename.

        Parameters
        ----------
        filename: `str`
            Name and path of the file where the image will be saved.
        """
        output_file_base_name = f"{filename}.{HTMLSaver._extension}"
        output_file = os.path.join(self._output_dir, output_file_base_name)
        if isinstance(plot, ImageDisplay):
            saver = _HVHtmlImageDisplaySaver(plot)
        elif isinstance(plot, _InteractiveDisplay):
            saver = _PanelHtmlLayoutSaver(plot)
        else:
            raise Exception("Unable to save plot of this type")
        saver.save(output_file)
        return output_file
