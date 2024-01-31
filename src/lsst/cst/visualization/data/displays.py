import holoviews as hv

from lsst.cst.visualization.utils import ExposureData


class Scatter:

    def __init__(self, data: ExposureData):
        self._exposure_data = data

    def show_scatter(self, data_x: str, data_y: str, frac: float = 1.0):
        data = self._exposure_data.get_data(frac)
        return hv.Scatter(data).options(toolbar=None)
