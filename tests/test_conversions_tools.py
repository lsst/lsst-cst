import pathlib
import unittest
import numpy as np
from lsst.cst.conversions import ids_to_str, nearest_patch_from_ra_dec


PATH = pathlib.Path(__file__).parent.absolute()


class TestDataUtils(unittest.TestCase):
    """Test data utility functions in conversions module."""

    def test_nearest_patch_from_ra_dec(self):
        ra = 55.745834
        dec = -32.269167
        result = nearest_patch_from_ra_dec(ra, dec)
        self.assertEqual(result['tract'], 4431)
        self.assertEqual(result['patch'], 17)

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
