import os
import pandas as pd
import unittest


from lsst.cst.visualization.data.displays import HoverTool
from lsst.cst.visualization.tools import save_plot_as_html, delete_plot
from lsst.cst.data.queries import DataWrapper
from lsst.cst.visualization.data.helper import (
    create_linked_plot_with_brushing, create_datashader_plot)

base_folder = os.path.dirname(os.path.abspath(__file__))


class TestDataPlot(unittest.TestCase):
    _DATA_PLOT_FILE_NAME = os.path.join(base_folder, "assets/linked_plot.html")

    def setUp(self):
        file_path = os.path.join(base_folder, 'assets/compressed_data.csv.gz')
        self._dataframe = pd.read_csv(file_path, compression='gzip')

    def tearDown(self):
        del self._dataframe
        import gc
        gc.collect()
        os.remove(TestDataPlot._DATA_PLOT_FILE_NAME)

    def testCreateLinkedPlot(self):
        raDecHover = HoverTool(
            tooltips=[
                ('ra,dec', '@coord_ra / @coord_dec'),
                ('rmag', '@mag_r_cModel'),
                ('type', '@shape_type'),
            ],
            formatters={
                'ra/dec': 'printf',
                'rmag': 'numeral',
                'type': 'printf',
            },
            point_policy="follow_mouse"
        )
        data = DataWrapper(self._dataframe)
        reduced_data = data.reduce_data(0.05)
        plot = create_linked_plot_with_brushing(reduced_data, hovertool=raDecHover)
        save_plot_as_html(plot, TestDataPlot._DATA_PLOT_FILE_NAME)
        delete_plot(plot)

    def testDatashaderPlot(self):
        data = DataWrapper(self._dataframe)
        plot = create_datashader_plot(data, ("gmr", "gmi"))
        save_plot_as_html(plot, TestDataPlot._DATA_PLOT_FILE_NAME)
        delete_plot(plot)
