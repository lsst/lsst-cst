import unittest

import matplotlib.pyplot as plt
import numpy as np

from lsst.cst.utilities import delete_plot


class TestMPLUtils(unittest.TestCase):
    """Test  matplotlib utils."""

    @unittest.SkipTest
    def testRemoveFigure(self) -> None:
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
