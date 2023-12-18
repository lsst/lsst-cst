"""plot science utils"""


import holoviews as hv
from holoviews.operation.datashader import rasterize
from lsst.afw.image._exposure import ExposureF


class PlotViewer:

    def __init__(self, exposure: ExposureF):
        self._img = None
        self._exposure = exposure

    def render(self):
        """"""
        assert self._img is None
        image_array = self._exposure.image.array
        self._img = hv.Image(image_array).opts(
            cmap="Greys_r", xlabel='X', ylabel='Y',
            title='DC2 image dataId: "')

    def show(self):
        """"""
        assert self._img is not None
        rasterize(self._img)
