import holoviews as hv

from lsst.cst.visualization.utils import ExposureData
from collections.abc import Sequence
from typing import Optional
from dataclasses import dataclass


@dataclass
class ScatterOptions:
    """Image plot options.

    Parameters
    ----------
    height: `int`
        Height of the plot in pixels.
    width: `int`
        Width of the plot in pixels.
    """
    height: int = 600
    width: int = 700

    def to_dict(self):
        return dict(
            height=self.height,
            width=self.width,
        )


class DataImageDisplay:

    def __init__(self, data: ExposureData):
        self._exposure_data = data

    def show_scatter(self,
                     columns: Optional[Sequence] = None,
                     frac: float = 1.0,
                     options: ScatterOptions = ScatterOptions()):
        data = self._exposure_data.get_data(frac)
        if columns is None:
            return hv.Scatter(data).options(**options.to_dict())
        index = self._exposure_data.index
        data_x = columns[0]
        data_y = columns[1]
        assert data_x in index, f"Selected data {data_x} for X "\
                                f"not available on exposure data"
        assert data_y in index, f"Selected data {data_y} for Y "\
                                f"not available on exposure data"
        return hv.Scatter(data, data_x, data_y).options(toolbar=None)
