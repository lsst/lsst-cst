import pathlib
import unittest
import matplotlib.pyplot as plt
import numpy as np
from lsst.cst.utilities import ids_to_str
from lsst.cst.utilities import delete_plot

PATH = pathlib.Path(__file__).parent.absolute()


class TestUtilities(unittest.TestCase):
    """Test utility functions in utilities module."""

    def test_ids_to_str(self) -> None:
        # test ids to string functionality
        data_ids = np.array(
            [
                1249537790362809267,
                1252528461990360512,
                1248772530269893180,
                1251728017525343554,
                1251710425339299404,
                1250030371572068167,
                1253443255664678173,
                1251807182362538413,
                1252607626827575504,
                1249784080967440401,
                1253065023664713612,
                1325835101237446771,
            ]
        )

        data_id_str = ids_to_str(data_ids)

        result = (
            "(1249537790362809267, 1252528461990360512, 1248772530269893180, "
            "1251728017525343554, 1251710425339299404, 1250030371572068167, "
            "1253443255664678173, 1251807182362538413, 1252607626827575504, "
            "1249784080967440401, 1253065023664713612, 1325835101237446771)"
        )

        self.assertEqual(data_id_str, result)


    @unittest.SkipTest
    def test_delete_plot(self) -> None:
        """Create a figure and test that the remove_figure function
        removes it as expected."""

        # Data for plotting
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)

        fig, ax = plt.subplots()
        ax.plot(t, s)

        ax.set(
            xlabel="time (s)",
            ylabel="voltage (mV)",
            title="A simple test plot",
        )
        ax.grid()
        self.assertIsNotNone(fig)

        # Remove figure using utility function
        delete_plot(fig)
