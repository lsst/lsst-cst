"""
data utils
"""
import numpy as np
import pandas as pd


def sort_dataframe(df: pd.DataFrame, sort_key: str, ascending: bool =False) -> pd.DataFrame:
    """
    Return a sorted copy of the dataframe by index,
    selecting the desired order (ascending or descending)
    using the ascending argument, it also exchanges the index
    of the dataframe for the sort_key.
    Parameters
    ----------
    df : `pd.DataFrame`
    sort_key: `str`
    ascending: `bool`, optional
    Returns
    -------
    result : `pd.DataFrame`
            A copy of the `~pandas.DataFrame` with the index sorted.
    """

    if sort_key not in df.columns:
        raise Exception(f"Index {sort_key} not existing in the dataframe")
    df = df.sort_values(sort_key, ascending=ascending)
    df.set_index(np.array(range(len(df))), inplace=True)
    return df