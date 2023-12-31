import unittest

import matplotlib.pyplot as plt
import numpy as np

from lsst.cst.mpl_utils import remove_figure


class TestMPLUtils(unittest.TestCase):
    """Test  matplotlib utils."""

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
        remove_figure(fig)
