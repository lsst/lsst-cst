"""plot science utils"""


import holoviews as hv
from dataclasses import dataclass, field
from holoviews.operation.datashader import rasterize
from typing import Dict, List

from lsst.afw.image._exposure import ExposureF


@dataclass(frozen=True)
class Options:
    """Image options class
    Parameters
    ----------
    cmap: `str`

    height: `int`
        Height of the image
    width: `int``
        Width of the image
    xaxis: `str`
        Position of the xaxis
    padding: `float`
    font_size:
    colorbar: `bool`
    toolbar: `str``
    show_grid: `bool`
    tools: `List[str]`
    """
    cmap: str = "Greys_r"
    height: int = 600
    width: int = 700
    xaxis: str = "bottom"
    padding: float = 0.01
    font_size: Dict[str, str] = field(default_factory=lambda: {'title': '8pt'})
    colorbar: bool = True
    toolbar: str = 'right'
    show_grid: bool = True
    tools: List[str] = field(default_factory=lambda: ['hover'])

    def to_dict(self):
        return dict(cmap=self.cmap, height=self.height,
                    width=self.width, xaxis=self.xaxis,
                    padding=self.padding, fontsize=self.font_size,
                    colorbar=self.colorbar, toolbar=self.toolbar,
                    show_grid=self.show_grid, tools=self.tools)


class Plot:

    def __init__(self, exposure: ExposureF):
        self._img = None
        self._exposure = exposure

    def render(self, title, xlabel: str = 'X', ylabel: str = 'Y', options: Options = Options()):
        """"""
        assert self._img is None
        image_array = self._exposure.image.array
        self._img = hv.Image(image_array, kdims=[xlabel, ylabel]).opts(
            xlabel=xlabel, ylabel=ylabel, title=title, **options.to_dict,
        )

    def show(self):
        """"""
        assert self._img is not None
        return rasterize(self._img)
    
    def delete(self):
        """"""
        self._img.remove()
