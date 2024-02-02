import holoviews as hv

from bokeh.models import HoverTool
from dataclasses import dataclass, field
from lsst.cst.visualization.utils import ExposureData
from typing import List, Optional, Tuple


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
    alpha: float = 1.0
    color: str = None
    invert_xaxis: bool = False
    invert_yaxis: bool = False
    height: int = 600
    marker: str = 'x'
    size: int | str = None
    toolbar: str = 'above'
    tools: List = field(default_factory=list)
    width: int = 700
    xlabel: str = "X"
    xticks: int = 5
    ylabel: str = "Y"
    yticks: int = 5

    def to_dict(self):
        ret_dict = dict(alpha=self.alpha,
                        color=self.color,
                        height=self.height,
                        invert_xaxis=self.invert_xaxis,
                        invert_yaxis=self.invert_yaxis,
                        marker=self.marker,
                        size=self.size,
                        toolbar=self.toolbar,
                        tools=self.tools,
                        width=self.width,
                        xlabel=self.xlabel,
                        xticks=self.xticks,
                        ylabel=self.ylabel,
                        yticks=self.yticks
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
    width: int = 700

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

    def create_axe(self,
                   data_identifier: str,
                   label: str,
                   range: Tuple[Optional[float], Optional[float]] = (None, None),
                   unit: str = "N/A"):
        index = self._exposure_data.index
        assert data_identifier in index, f"Selected data {data_identifier} for X "\
                                         f"not available on exposure data"
        return hv.Dimension(data_identifier, label=label, range=range, unit=unit)

    def show_scatter(self,
                     columns: Optional[Tuple[hv.Dimension | str, hv.Dimension | str]] = None,
                     options: ScatterOptions = ScatterOptions()):
        data = self._exposure_data.data
        if columns is None:
            return hv.Scatter(data).options(**options.to_dict())
        index = self._exposure_data.index
        data_x = columns[0]
        data_y = columns[1]
        if isinstance(data_x, str):
            assert data_x in index, f"Selected data {data_x} for X "\
                                    f"not available on exposure data"
        if isinstance(data_y, str):
            assert data_y in index, f"Selected data {data_y} for Y "\
                                    f"not available on exposure data"
        return hv.Scatter(data, data_x, data_y).options(**options.to_dict())

    def show_histogram(self, field: 'str', options: HistogramOptions = HistogramOptions()):
        bin, count = self._exposure_data.histogram(field)
        return hv.Histogram((bin, count)).opts(**options.to_dict())
