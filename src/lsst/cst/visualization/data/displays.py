import holoviews as hv

from lsst.cst.visualization.utils import ExposureData


class Scatter:

    def __init__(self, data: ExposureData):
        self._exposure_data = data

    def show_scatter(self, data_x: str, data_y: str, frac: float = 1.0):
        data = self._exposure_data.get_data(frac)
        index = self._exposure_data.index
        assert data_x in index, f"Selected data {data_x} for X "\
                                f"not available on exposure data"
        assert data_x in index, f"Selected data {data_y} for Y "\
                                f"not available on exposure data"
        return hv.Scatter(data, data_x, data_y).options(toolbar=None)
