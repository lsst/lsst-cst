"""General plot utils"""

import gc

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from typing import Any

# image deleters


def delete_plot(plot: Any) -> None:
    """Plot deleter function.

    Parameters:
    ----------
    plot: 'Any'
       Plot to be deleted. Nowadays this function will work
       with any python object, but the plan is to specialized
       for diferent plots and layouts.
    """
    del plot
    import gc
    gc.collect()


def _remove_figure(fig: Figure) -> None:
    """Remove a figure to reduce memory footprint.

    Parameters
    ----------
    fig : `matplotlib.figure.Figure`
        Figure to be removed.

    Returns
    -------
    None
    """
    # Get the axes and clear their images
    for ax in fig.get_axes():
        for im in ax.get_images():
            im.remove()
    # Clear the figure
    fig.clf()
    # Close the figure
    plt.close(fig)
    # Call the garbage collector
    gc.collect()
