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
    color: str = None
    height: int = 600
    size: str = None
    width: int = 700
    

    def to_dict(self):
        ret_dict = dict(color=self.color,
                        height=self.height,
                        size=self.size,
                        width=self.width,
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


@dataclass
class HistogramOptions:
    color: str = 'darkmagenta'
    fontscale: float = 1.2
    height: int = 600
    title: str = "No title"
    xlabel: str = 'X'
    width: int = 400

    def to_dict(self):
        ret_dict = dict(color=self.color,
                        height=self.height,
                        fontscale=self.fontscale,
                        title=self.title,
                        width=self.width,
                        xlabel=self.xlabel
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


class DataImageDisplay:

    def __init__(self, data: ExposureData):
        self._exposure_data = data

    def show_scatter(self,
                     columns: Optional[Sequence] = None,
                     options: ScatterOptions = ScatterOptions()):
        data = self._exposure_data.data
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

    def show_histogram(self, field: 'str', options: HistogramOptions = HistogramOptions()):
        bin, count = self._exposure_data.histogram(field)
        return hv.Histogram((bin, count)).opts(options)
