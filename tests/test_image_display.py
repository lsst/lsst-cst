import os
import unittest

import numpy as np
import pandas as pd

from lsst.cst.data.queries import Band
from lsst.cst.data.tools import CalExpDataFactory, CalExpId
from lsst.cst.visualization.image.helper import create_interactive_image
from lsst.cst.visualization.tools import delete_plot, save_plot_as_html

base_folder = os.path.dirname(os.path.abspath(__file__))


class CalExpDataTestFactory(CalExpDataFactory):
    def __init__(self):
        super().__init__()

    def get_cal_exp_data(self, calexp_id: CalExpId):
        return CalExpDataTest(
            calexp_id,
            "assets/image.npy",
            "assets/sources_data.csv",
            (4072, 4000),
        )


class Image:
    def __init__(self, array: np.array):
        self._array = array

    @property
    def array(self):
        return self._array


class CalExpDataTest:
    def __init__(
        self,
        cal_exp_id: CalExpId,
        image_path: str,
        sources_path: str,
        dimensions: tuple[int, int],
    ):
        self._cal_exp_id = cal_exp_id
        self._image_path = image_path
        self._sources_path = sources_path
        self._dimensions = dimensions

    @property
    def image(self):
        file_path = os.path.join(base_folder, self._image_path)
        data_array = np.load(file_path)
        return Image(data_array)

    @property
    def sources(self):
        file_path = os.path.join(base_folder, self._sources_path)
        df = pd.read_csv(file_path)
        df = df.reset_index(drop=True)
        return df

    def getDimensions(self):
        return self._dimensions

    @property
    def cal_exp_id(self):
        return str(self._cal_exp_id)


class TestImagePlot(unittest.TestCase):
    _FILE_NAME = os.path.join(base_folder, "assets/image_plot.html")

    def setUp(self):
        cal_exp_factory = CalExpDataTestFactory()
        cal_exp_id = CalExpId(visit=192350, detector=175, band=Band.i)
        self._cal_exp_data = cal_exp_factory.get_cal_exp_data(cal_exp_id)

    def tearDown(self):
        os.remove(TestImagePlot._FILE_NAME)

    def testCreateImageWithSourcesAndDeleteItAfter(self):
        plot = create_interactive_image(
            self._cal_exp_data,
            self._cal_exp_data.sources,
            title=self._cal_exp_data.cal_exp_id,
        )
        save_plot_as_html(plot, TestImagePlot._FILE_NAME)
        delete_plot(plot)
