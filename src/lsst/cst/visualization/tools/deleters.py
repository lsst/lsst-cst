"""data science delete plot tools."""

import gc

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from panel.layout.base import Panel

# image deleters

__all__ = ["delete_plot"]


def delete_plot(plot: Panel | Figure) -> None:
    """Delete selected plot.

    Parameters
    ----------
    plot: 'Any'
       Plot to be deleted.
    """
    if isinstance(plot, Figure):
        _remove_figure(plot)
    elif isinstance(plot, Panel):
        plot.clear()
        del plot
        import gc

        gc.collect()
    else:
        raise Exception(f"Unknown instance to delete {type(plot)}")


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
