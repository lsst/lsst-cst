"""Custom plotting functions for tutorial notebooks."""

from bokeh.io import reset_output, output_notebook, show, output_file

__all__ = [
    "show_bokeh_inline",
    "show_bokeh_to_file",
]


def show_bokeh_inline(p):
    """To avert a 'Models must be owned by only a single document'
    error (see, e.g., https://github.com/bokeh/bokeh/issues/8579),
    use this function to display Bokeh plots in a notebook.

    Parameters
    ----------
    p: `bokeh.models.plots.GridPlot`
        A Bokeh GridPlot.
    
    """
    try:
        reset_output()
        output_notebook()
        show(p)
    except:
        output_notebook()
        show(p)


def show_bokeh_to_file(p, output_file):
    """To avert a 'Models must be owned by only a single document'
    error (see, e.g., https://github.com/bokeh/bokeh/issues/8579),
    use this function to save Bokeh plots as interactive html.

    Parameters
    ----------
    p: `bokeh.models.plots.GridPlot`
        A Bokeh GridPlot.

    output_file: `str`
        Filename with an .html suffix.
    
    """
    try:
        reset_output()
        output_file(outputFile)
        show(p)
    except:
        output_file(outputFile)
        show(p)
