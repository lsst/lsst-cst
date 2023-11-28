import unittest

import pandas as pd

from lsst.cst.data_utils import sort_dataframe

class TestDataUtils(unittest.TestCase):
    """Test data utils."""

    def testSortDataFrameNonExistingKey(self) -> None:
        """
        """
        data = {'Prefecture': ['Tokyo', 'Osaka', 'Kanagawa', 'Aichi', 'Hokkaido'],
                'Population': [13929286, 8839469, 9126214, 7483128, 5386252]}
        df = pd.DataFrame(data)
        with self.assertRaises(Exception):
            sort_dataframe(df, sort_key='Residents')

    def testSortDescendingDataFrame(self) -> None:
        """
        """
        data = {'Prefecture': ['Tokyo', 'Osaka', 'Kanagawa', 'Aichi', 'Hokkaido'],
                'Population': [13929286, 8839469, 9126214, 7483128, 5386252]}

        df = pd.DataFrame(data)

        # Order the DataFrame by the 'Population' column using the function
        ordered_df = sort_dataframe(df, sort_key = 'Population')

        # Expected result after ordering by 'Population' in descending order and resetting the index
        expected_result = pd.DataFrame({
            'Prefecture': ['Tokyo', 'Kanagawa', 'Osaka', 'Aichi', 'Hokkaido'],
            'Population': [13929286, 9126214, 8839469, 7483128, 5386252]
        })

        # Check if the ordered DataFrame is equal to the expected result
        pd.testing.assert_frame_equal(ordered_df, expected_result, check_exact = True)

    def testSortAscendingDataFrame(self) -> None:
        """
        """
        data = {'Prefecture': ['Tokyo', 'Osaka', 'Kanagawa', 'Aichi', 'Hokkaido'],
                'Population': [13929286, 8839469, 9126214, 7483128, 5386252]}

        df = pd.DataFrame(data)

        # Order the DataFrame by the 'Population' column using the function
        ordered_df = sort_dataframe(df, sort_key = 'Population', ascending=True)

        # Expected result after ordering by 'Population' in descending order and resetting the index
        expected_result = pd.DataFrame({
             'Prefecture': ['Hokkaido', 'Aichi', 'Osaka', 'Kanagawa', 'Tokyo'],
             'Population': [5386252, 7483128, 8839469, 9126214, 13929286]
        })

        # Check if the ordered DataFrame is equal to the expected result
        pd.testing.assert_frame_equal(ordered_df, expected_result, check_exact = True)