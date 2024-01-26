
import os
import unittest
import numpy as np
import pandas as pd
import psutil

from lsst.cst.plot import ImagePlot, HoverSources, HTMLSaver
from lsst.cst.data import CalExpData, CalExpDataFactory, CalExpId, Band

base_folder = os.path.dirname(os.path.abspath(__file__))


class CalExpDataTestFactory(CalExpDataFactory):

    def __init__(self):
        super().__init__()

    def get_cal_exp_data(self, calexp_id: CalExpId):
        return CalExpDataTest(calexp_id,
                              "assets/image.npy",
                              "assets/sources_data.csv",
                              (0, 0, 4072, 4000))


def get_memory_in_use_mb():
    # Get information about system memory
    memory_info = psutil.virtual_memory()
    used_memory_mb = memory_info.used / (1024 ** 2)
    return used_memory_mb


def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    """
    return os.path.getsize(file_path)


class CalExpDataTest(CalExpData):

    def __init__(self,
                 cal_exp_id: CalExpId,
                 image_path: str,
                 sources_path: str,
                 bounds: tuple[float]):
        self._cal_exp_id = cal_exp_id
        self._image_path = image_path
        self._sources_path = sources_path
        self._bounds = bounds

    def get_image(self):
        file_path = os.path.join(base_folder, self._image_path)
        data_array = np.load(file_path)
        return data_array

    def get_sources(self):
        file_path = os.path.join(base_folder, self._sources_path)
        df = pd.read_csv(file_path)
        return df

    def get_image_bounds(self):
        return self._bounds

    @property
    def cal_exp_id(self):
        return str(self._cal_exp_id)


class TestImagePlot(unittest.TestCase):

    def setUp(self):
        cal_exp_factory = CalExpDataTestFactory()
        cal_exp_id = CalExpId(visit=192350, detector=175, band=Band.i)
        self._cal_exp_data = cal_exp_factory.get_cal_exp_data(cal_exp_id)

    def tearDown(self):
        pass

    def test_image_with_sources(self):
        cal_exp_plot = ImagePlot.from_cal_exp_data(self._cal_exp_data)
        hover_sources = HoverSources(cal_exp_plot)
        html_saver = HTMLSaver()
        created_plot_filename = os.path.join(base_folder, "assets/created_plot")
        created_file = html_saver.save(hover_sources, created_plot_filename)
        # Calculate MD5 hash
        file_size = get_file_size(created_file)
        saved_file_size = get_file_size(os.path.join(base_folder, "assets/image_plot.html"))
        os.remove(created_file)
        assert saved_file_size == file_size

    def test_delete_image(self):
        cal_exp_plot = ImagePlot.from_cal_exp_data(self._cal_exp_data)
        initial_memory = get_memory_in_use_mb()
        cal_exp_plot.render()
        after_render_memory = get_memory_in_use_mb()
        cal_exp_plot.delete()
        after_deleted_memory = get_memory_in_use_mb()
        lost_memory = after_render_memory - initial_memory
        won_memory = after_render_memory - after_deleted_memory
        np.testing.assert_allclose(lost_memory, won_memory, rtol=0.1, atol=1e-9)
