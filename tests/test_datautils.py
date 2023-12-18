import unittest

import numpy as np
import pandas as pd

from lsst.cst.data_utils import (
    data_id_to_str,
    ids_to_str,
    shuffle_dataframe,
    sort_dataframe,
)


class TestDataUtils(unittest.TestCase):
    """Test data utils."""

    def testSortDataFrameNonExistingKey(self) -> None:
        """ """
        data = {
            "Prefecture": ["Tokyo", "Osaka", "Kanagawa", "Aichi", "Hokkaido"],
            "Population": [13929286, 8839469, 9126214, 7483128, 5386252],
        }
        df = pd.DataFrame(data)
        with self.assertRaises(Exception):
            sort_dataframe(df, sort_key="Residents")

    def testSortDescendingDataFrameSettingIndex(self) -> None:
        """ """
        data = {
            "Prefecture": ["Tokyo", "Osaka", "Kanagawa", "Aichi", "Hokkaido"],
            "Population": [13929286, 8839469, 9126214, 7483128, 5386252],
        }

        df = pd.DataFrame(data)

        # Order the DataFrame by the 'Population' column using the function
        ordered_df = sort_dataframe(df, sort_key="Population")

        # Expected result after ordering by 'Population' in
        # descending order and resetting the index
        expected_result = pd.DataFrame(
            {
                "Prefecture": [
                    "Tokyo",
                    "Kanagawa",
                    "Osaka",
                    "Aichi",
                    "Hokkaido",
                ],
                "Population": [13929286, 9126214, 8839469, 7483128, 5386252],
            }
        )

        # Check if the ordered DataFrame is equal to the expected result
        pd.testing.assert_frame_equal(
            ordered_df, expected_result, check_exact=True
        )

    def testSortAscendingDataFrameNoSettingIndex(self) -> None:
        """ """
        data = {
            "Prefecture": ["Aichi", "Hokkaido", "Kanagawa", "Osaka", "Tokyo"],
            "Population": [7483128, 5386252, 9126214, 8839469, 13929286],
        }

        df = pd.DataFrame(data)

        # Order the DataFrame by the 'Population' column using the function
        ordered_df = sort_dataframe(
            df, sort_key="Population", ascending=True, set_index=False
        )

        # Expected result after ordering by 'Population' in descending
        # order and resetting the index
        expected_result = pd.DataFrame(
            {
                "Prefecture": [
                    "Hokkaido",
                    "Aichi",
                    "Osaka",
                    "Kanagawa",
                    "Tokyo",
                ],
                "Population": [5386252, 7483128, 8839469, 9126214, 13929286],
            },
            index=[1, 0, 3, 2, 4],
        )

        # Check if the ordered DataFrame is equal to the expected result
        pd.testing.assert_frame_equal(
            ordered_df, expected_result, check_exact=True
        )

    def testShuffleDataframe(self) -> None:
        """ """
        data = {
            "Prefecture": ["Tokyo", "Osaka", "Kanagawa", "Aichi", "Hokkaido"],
            "Population": [13929286, 8839469, 9126214, 7483128, 5386252],
        }
        df = pd.DataFrame(data)
        shuffled_df = shuffle_dataframe(df, random_state=42)
        data = {
            "Prefecture": ["Osaka", "Hokkaido", "Kanagawa", "Tokyo", "Aichi"],
            "Population": [8839469, 5386252, 9126214, 13929286, 7483128],
        }

        # Index column
        index_column = [1, 4, 2, 0, 3]

        # Create DataFrame
        expected_result = pd.DataFrame(data, index=index_column)
        pd.testing.assert_frame_equal(
            shuffled_df, expected_result, check_exact=True
        )

    def testDataIdToString(self) -> None:
        """ """
        data_id = {"visit": 192350, "detector": 175, "band": "i"}
        data_id_str = data_id_to_str(data_id)

        result = "visit: 192350, detector: 175, band: i"

        self.assertEquals(data_id_str, result)

    def testIdsToString(self) -> None:
        """ """
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

        self.assertEquals(data_id_str, result)
