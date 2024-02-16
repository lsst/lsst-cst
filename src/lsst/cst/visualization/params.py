"""data science default parameters for plots."""

__all__ = ["PlotOptionsDefault"]


class PlotOptionsDefault:
    color = 'darkorange'
    cmap_color = 'Viridis'
    fontsize = {'title': 16,
                'xlabel': 14,
                'ylabel': 14,
                'ticks': 12}
    height = 600
    marker = 'circle'
    marker_color = 'darkorange'
    marker_size = 5
    show_grid = True
    toolbar_position = 'above'
    width = 700
    filter_colormap = {'u': '#56b4e9',
                       'g': '#008060',
                       'r': '#ff4000',
                       'i': '#850000',
                       'z': '#6600cc',
                       'y': '#000000'}
