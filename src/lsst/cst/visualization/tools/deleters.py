"""data science delete plot tools."""

import gc
import panel as pn
import matplotlib.pyplot as plt

from matplotlib.figure import Figure


# image deleters

__all__ = ["delete_plot"]


def delete_plot(plot: pn.Layout) -> None:
    """Delete selected plot.

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


def _remove_figure(fig: Figure):
    """Remove a figure to reduce memory footprint.

    Parameters
    ----------
    fig : `matplotlib.figure.Figure`
        Figure to be removed.
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
