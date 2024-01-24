import os

from abc import ABC, abstractmethod
from lsst.cst.plot.plotting import Plot, get_extension
import holoviews as hv


class PlotSaver(ABC):

    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__()
        self._output_dir = output_dir

    @abstractmethod
    def save(self):
        raise NotImplementedError()


class HTMLSaver(PlotSaver):
    """HTML plot saver
    """

    def __init__(self, output_dir: str = os.path.expanduser("~")):
        super().__init__(output_dir)

    def save(self, plot: Plot, filename: str):
        """Save image as html in filename.

        Parameters
        ----------
        filename: `str`
            Name and path of the file where the image will be saved.
        """
        img = plot.rasterize()
        output_file_base_name = f"{filename}.html"
        outputFile = os.path.join(self._output_dir, output_file_base_name)
        hv.save(img, outputFile, backend=get_extension().value)
