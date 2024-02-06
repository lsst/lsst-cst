import holoviews as hv

from bokeh.io import show
from bokeh.models import HoverTool  # noqa: F401
from bokeh.plotting import figure, gridplot
from dataclasses import dataclass, field
from lsst.cst.visualization.utils import ExposureData
from typing import List, Optional, Union, Tuple


@dataclass
class FigureOptions:
    """Image plot options.

    Parameters
    ----------
    height: `int`
        Height of the plot in pixels.
    width: `int`
        Width of the plot in pixels.
    """
    height: int = 600
    # toolbar: str = 'above'
    tools: List = field(default_factory=lambda: [])
    # "pan,box_zoom,box_select,lasso_select,reset,help"
    width: int = 700
    xlabel: str = "X"
    ylabel: str = "Y"
    # x_range: None
    # y_range: None

    def to_dict(self):
        ret_dict = dict(height=self.height,
                        # toolbar=self.toolbar,
                        tools=self.tools,
                        width=self.width,
                        x_axis_label=self.xlabel,
                        y_axis_label=self.ylabel,
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


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
    marker: str = 'x'
    size: int | str = None

    def to_dict(self):
        ret_dict = dict(alpha=self.alpha,
                        color=self.color,
                        marker=self.marker,
                        size=self.size,
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
    ylabel: str = 'Y'

    def to_dict(self):
        ret_dict = dict(color=self.color,
                        height=self.height,
                        fontscale=self.fontscale,
                        title=self.title,
                        xlabel=self.xlabel,
                        width=self.width,
                        ylabel=self.ylabel
                        )
        filtered_dict = {key: value for key, value in ret_dict.items() if value is not None}
        return filtered_dict


class DataFigure:
    """
    """
    def __init__(self,
                 figure_id: str,
                 data: ExposureData,
                 options: FigureOptions = FigureOptions()):
        self._figure_id = figure_id
        self._exposure_data = data
        self._figure = figure(**options.to_dict())

    def add_scatter(self,
                    x_data: str,
                    y_data: str,
                    x_identifier: None | str = None,
                    options: ScatterOptions = ScatterOptions()):
        index = self._exposure_data.index
        assert x_data in index, f"Selected data {x_data}"\
                                f"not available on exposure data"
        assert y_data in index, f"Selected data {y_data}"\
                                f"not available on exposure data"
        data_x = self._exposure_data[x_data]
        data_y = self._exposure_data[y_data]
        self._figure.scatter(data_x, data_y, **options.to_dict())

    def add_histogram(self):
        pass

    @property
    def figure(self):
        return figure


class DataImageDisplay:

    def __init__(self, data: ExposureData):
        self._exposure_data = data
        self._figures = {}  # type: dict[str, DataFigure]

    def get_figure(self, figure_identifier: str):
        figure = self._figures.get(figure_identifier, None)
        assert figure is not None, f"Figure {figure_identifier} doesnt exists"
        return figure

    def create_figure(self, identifier: str, figure_options: FigureOptions = FigureOptions()):
        new_figure = DataFigure(identifier, self._exposure_data, figure_options)
        assert identifier not in self._figures.keys(), \
            f"Figure {identifier} already exists"
        self._figures[identifier] = new_figure
        return new_figure

    def _exchange_figures(
        self,
        layout: List[Union[str, List[...]]],
        new_layout: List[Union[figure, List[...]]]
    ):
        for item in layout:
            if isinstance(item, list):
                aux_layout = []
                self._exchange_figures(item, aux_layout)
                layout.append(aux_layout)
            else:
                new_layout.append(self._figures[item])

    def show(self, layout: List[Union[str, List[...]]] = []):
        new_layout = []
        self._exchange_figures(layout, new_layout)
        return show(gridplot(new_layout))

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
