"""lsst.cst submodule with all the tools available
to manage the plotting of images and data.
Next modules are available:
- deleters: plot deleters.
- helpers: User friendly functions to create some
standarized plots.
- image: Image tools to abstract the access to the images.
- queries: Wrap around Tap Service to be able to do
queries more user friendly. Also contains standard queries used
in some standart plots.
- savers: plot savers.
- transform: Transform tools to handle image and data
before creating the image or plot.
- parameters: constant parameters and enum for plotting.
"""

from .deleters import delete_plot
from .parameters import Band, PlotOptionsDefault
from .savers import save_plot_as_html

__all__ = [
    "Band",
    "PlotOptionsDefault",
    "save_plot_as_html",
    "delete_plot",
    "create_interactive_image",
    "create_rgb_composite_image",
    "create_skycoord_datashader_plot",
    "create_datashader_plot",
    "create_skycoord_linked_plot_with_brushing",
    "create_linked_plot_with_brushing",
    "create_bounding_boxes_calexps_overlapping_a_point_plot",
    "create_psf_flux_plot",
]
