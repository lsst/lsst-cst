import os

from abc import ABC, abstractmethod
from lsst.cst.plot import Plot
from lsst.cst.plot import get_extension
from lsst.cst.plot.interactors import _InteractivePlot
import holoviews as hv

__all__ = "HTMLSaver"


class Saver(ABC):

    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__()
        self._output_dir = output_dir

    @abstractmethod
    def save(self):
        raise NotImplementedError()


class PlotSaver(ABC):

    @abstractmethod
    def save(self):
        raise NotImplementedError()


class HVHtmlPlotSaver(PlotSaver):

    def __init__(self, plot: Plot):
        self._plot = plot

    def save(self, filename):
        img = self._plot.rasterize()
        hv.save(img, filename, backend=get_extension().value)


class PanelHtmlLayoutSaver(PlotSaver):

    def __init__(self, interactive_plot: _InteractivePlot):
        self._interactive_plot = interactive_plot

    def save(self, filename):
        self._interactive_plot.show().save(filename, embed=True)


class HTMLSaver(Saver):
    """HTML plot saver
    """
    _extension = "html"

    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__(output_dir)

    def save(self, plot: Plot | _InteractivePlot, filename: str):
        """Save image as html in filename.

        Parameters
        ----------
        filename: `str`
            Name and path of the file where the image will be saved.
        """
        output_file_base_name = f"{filename}.{HTMLSaver._extension}"
        output_file = os.path.join(self._output_dir, output_file_base_name)
        if isinstance(plot, Plot):
            saver = HVHtmlPlotSaver(plot)
        elif isinstance(plot, _InteractivePlot):
            saver = PanelHtmlLayoutSaver(plot)
        else:
            raise Exception("Unable to save plot of this type")
        saver.save(output_file)
