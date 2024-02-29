"""data science constant values for plots."""
from enum import Enum

__all__ = ["Band", "PlotOptionsDefault"]


class Band(Enum):
    """Exposure bands available."""

    g = "g"
    i = "i"
    r = "r"
    u = "u"
    y = "y"
    z = "z"


class PlotOptionsDefault:
    """Scatic class to save all plotting
    aesthetic default values.
    """

    color = "darkorange"
    cmap_color = "Viridis"
    fontsize = {"title": 16, "xlabel": 14, "ylabel": 14, "ticks": 12}
    height = 600
    marker = "circle"
    marker_color = "darkorange"
    marker_size = 5
    show_grid = True
    toolbar_position = "above"
    width = 700
    filter_colormap = {
        Band.u.value: "#56b4e9",
        Band.g.value: "#008060",
        Band.r.value: "#ff4000",
        Band.i.value: "#850000",
        Band.z.value: "#6600cc",
        Band.y.value: "#000000",
    }
