import holoviews as hv

from lsst.cst.visualization.utils import ExposureData
from collections.abc import Sequence
from typing import Optional


class ScatterOptions:
    pass


class Scatter:

    def __init__(self, data: ExposureData):
        self._exposure_data = data

    def show_scatter(self,
                     columns: Optional[Sequence] = None,
                     frac: float = 1.0,
                     options: ScatterOptions = ScatterOptions()):
        data = self._exposure_data.get_data(frac)
        if columns is None:
            return hv.Scatter(data).options(toolbar=None)
        index = self._exposure_data.index
        data_x = columns[0]
        data_y = columns[1]
        assert data_x in index, f"Selected data {data_x} for X "\
                                f"not available on exposure data"
        assert data_y in index, f"Selected data {data_y} for Y "\
                                f"not available on exposure data"
        return hv.Scatter(data, data_x, data_y).options(toolbar=None)
