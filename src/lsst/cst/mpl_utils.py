"""Matplotlib science utils"""

import gc

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def remove_figure(fig: Figure) -> None:
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
