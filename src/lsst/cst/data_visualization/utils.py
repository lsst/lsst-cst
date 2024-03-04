import pandas as pd
import panel as pn
from typing import List, Tuple

from bokeh.models import HoverTool  # noqa: F401
from lsst.cst.data_visualization import (
    GeometricPlots,
    PolygonOptions,
)
from lsst.cst.utilities.parameters import PlotOptionsDefault


def create_polygons_and_point_plot(
    df: pd.DataFrame,
    points: List[Tuple[float, float]]
):
    """Draw list of boxes in a dataframe and list of points.

    Parameters
    ----------
    df: `pd.DataFrame`
        Information of the polygons to draw. Should have next columns:
        llcra, ulcra, llcra, urcra,
        llcdec, ulcdec, llcdec, urcdev,
        band,
        ccdVisitId

    points: List[Tuple[float, float]]
        List of tuple of points that will be drawn at the plot.

    Returns
    -------
    plot: `pn.Row`
        Panel Row containing the polygons and points.
    """
    region_list = []
    for index, row in df.iterrows():
        r = {
            "x": [row["llcra"], row["ulcra"], row["urcra"], row["lrcra"]],
            "y": [row["llcdec"], row["ulcdec"], row["urcdec"], row["lrcdec"]],
            "v1": row["band"],
            "v2": row["ccdVisitId"],
        }
        region_list.append(r)
    tooltips = [("band", "@v1"), ("ccdVisitId", "@v2")]

    hover = HoverTool(tooltips=tooltips)
    boxes = GeometricPlots.polygons(
        region_list,
        kdims=["x", "y"],
        vdims=["v1", "v2"],
        options=PolygonOptions(
            cmap=PlotOptionsDefault.filter_colormap,
            line_color="v1",
            tools=[hover],
        ),
    )
    points = GeometricPlots.points(points)
    return pn.Row(boxes * points)
