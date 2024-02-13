"""data science format utils."""
import numpy as np
import pandas as pd

from lsst.cst.data.tools import CalExpId


__all__ = [
    "data_id_to_str",
    "ids_to_str",
    "shuffle_dataframe",
    "sort_dataframe"
]


def ids_to_str(data_ids: np.ndarray) -> str:
    """Transform a numpy array of ids (long int)
        to a comma-separated values string

    Parameters
    ----------
    data_ids: `numpy.ndarray`
        numpy array with objects id

    Returns
    -------
    result: `str`
        String with separated by comma-separated values
        from the data_ids
    """
    return "(" + ", ".join(str(value) for value in data_ids) + ")"


def data_id_to_str(data_id: dict):
    """Returns a data identifier dictionary to a string

    Parameters
    ----------
    data_id: 'dict'
        Data identifier dictionary.

    Returns
    -------
    data_id_str: `str`
        Data identifier string
    """
    cal_exp_id = CalExpId(**data_id)
    return str(cal_exp_id)


def sort_dataframe(
    df: pd.DataFrame,
    sort_key: str,
    ascending: bool = False,
    set_index: bool = True,
) -> pd.DataFrame:
    """Return a sorted copy of the dataframe 'df' by index,
    selecting the desired order (ascending or descending)
    using the ascending argument, it also exchanges the index
    of the dataframe for the sort_key if set_index parameter
    is True (default).

    Parameters
    ----------
    df : `pandas.DataFrame`
        dataframe to be sorted
    sort_key: `str`
        column key used to sort the dataframe
    ascending: `bool`, optional
        ascending/descending sorting
    set_index: `bool`, optional
        set sorted key as the dataframe index

    Returns
    -------
    result : `pandas.DataFrame`
        Copy of the `~pandas.DataFrame` sorted using the selected column.
    """
    if sort_key not in df.columns:
        raise Exception(f"Index {sort_key} not existing in the dataframe")
    df = df.sort_values(sort_key, ascending=ascending)
    if set_index:
        df.set_index(np.array(range(len(df))), inplace=True)
    return df


def shuffle_dataframe(df: pd.DataFrame, random_state: int = 0) -> pd.DataFrame:
    """Return a copy of the dataframe df shuffled, random_state
    argument may be used to reproduce same shuffling.

    Parameters
    ----------
    df: `pandas.DataFrame`
        dataframe to be shuffled

    random_state: `int`
        number to reproduce same randomness

    Returns
    -------
    result: `pandas.DataFrame`
        shuffled dataframe
    """
    df_randomized = df.sample(frac=1, random_state=random_state)
    return df_randomized
