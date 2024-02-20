"""data science query tools"""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from bokeh.models import ColumnDataSource

from lsst.rsp import get_tap_service

_log = logging.getLogger(__name__)

__all__ = ["TAPService", "DataWrapper"]


class Band(Enum):
    """Exposure bands available."""

    g = 'g'
    i = 'i'
    r = 'r'
    u = 'u'
    y = 'y'
    z = 'z'


class DataHandler(ABC):
    """Interface to modify data inside a dataframa."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def handle_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Modifications to be done on a dataframe.

        Parameters
        ----------
        data: `pd.Dataframe`
            Data to be handled.

        Returns
        -------
        handled_data: `pd.Dataframe`
            Handled data.
        """
        raise NotImplementedError()


class ExposureDataHandler:
    """Standard actions to be done with a exposure data
    dataframe.
    """

    def __init__(self):
        super().__init__()

    def handle_data(self, data: pd.DataFrame):
        data["gmi"] = data["mag_g_cModel"] - data["mag_i_cModel"]
        data["rmi"] = data["mag_r_cModel"] - data["mag_i_cModel"]
        data["gmr"] = data["mag_g_cModel"] - data["mag_r_cModel"]
        data["shape_type"] = data["r_extendedness"].map(
            {0: "point", 1: "extended"}
        )
        data["objectId"] = np.array(data["objectId"]).astype("str")
        return data


class DataWrapper:
    """Data wrapper to facilitate most common operations over
    a pandas dataframe..

    Parameters
    ----------
    data: `pd.DataFrame`
        Exposure data information.
    """

    def __init__(self, data: pd.DataFrame):
        self._data = data
        self._column_data_source = None

    @classmethod
    def fromFile(cls, file_path: str):
        """Create a DataWrapper out from a dataframe saved
        on a csv file.

        Parameters
        ----------
        file_path: `str`
            Path to the csv file with data.
        """
        loaded_df = pd.read_csv(file_path)
        return DataWrapper(loaded_df)

    @property
    def index(self):
        """Get data index available.

        Returns
        -------
        index: `List[str]`
            Data index available.
        """
        return self._data.columns.tolist()

    @property
    def data(self):
        return self._data

    def get_column_data_source(self):
        """Create a bokeh ColumnDataSource.

        Returns
        -------
        data: `bokeh.models.ColumnDataSource`
            Underlying dataframe converted to
            a bokeh ColumnDataSource.
        """
        if self._column_data_source is None:
            self._column_data_source = ColumnDataSource(self._data)
        return self._column_data_source

    def filter_by_condition(
        self,
        column_name: str,
        condition: int | float | str,
        operator: str = "==",
    ):
        """Filter data by a given condition and
        returns in a new DataWrapper.

        Parameters
        ----------
        column_name: `str`
        condition: `int | float | str`
        operator: `str`

        Returns
        -------
        data: `DataWrapper`
            New DataWrapper with the rows that
            meet the condition.
        """
        operators = {"==": pd.Series.eq, ">": pd.Series.gt, "<": pd.Series.lt}
        assert operator in operators.values(), f"Non valid operator {operator}"
        data = self.data[
            operators[operator](self.data[column_name], condition)
        ]
        return DataWrapper(data)

    def handle_data(self, handler: DataHandler):
        """Modify underlying data using a DataHandler
        and return results in a new DataWrapper.

        Parameters
        ----------
        handler: `DataHandler`
            Data handler with modifications to be done
            in the underlying dataframe.

        Returns
        -------
        data: `DataWrapper`
            New DataWrapper with the modified DataFrame.
        """
        new_data = handler.handle_data(self._data)
        return DataWrapper(new_data)

    def reduce_data(self, frac: float = 1.0):
        """Reduce randomly underlying data and returns it
        in a DataWrapper.

        Parameters
        ----------
        frac: `float`
            Reduction factor, number between 0 and 1.

        Returns
        -------
        data: `DataWrapper`
            New DataWrapper with the reduced DataFrame.
        """
        assert 0.0 <= frac <= 1.0
        if frac == 1.0:
            return self
        data = self._data.sample(frac=frac, axis="index")
        return DataWrapper(data)

    def histogram(self, field: str):
        """Returns an histogram from the column selected.

        Parameters
        ----------
        field: `str`
            Selected column to create the histogram.

        Returns
        -------
        data: `np.array``
            Array containing the histogram data from the
            selected frame.
        """
        return np.histogram(self._data[field], bins="fd")

    def __getitem__(self, value):
        if value in self.index:
            return self.data[value]
        condition = value
        return DataWrapper(self.data[condition])

    def __setitem__(self, index, value):
        self.data[index] = value

    def __str__(self):
        return str(self.data)


class Query(ABC):
    """Interface of a Query to be
    used by TAPService
    """

    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def query(self):
        """Query string.

        Returns
        -------
        query: `str`
            Query being launched.
        """
        raise NotImplementedError()

    def post_query_actions(self, data: pd.DataFrame):
        """Actions to be taken after data is retrieved.

        Parameters
        ----------
        data: `pandas.dataframe`
            Queried data in dataframe.

        Returns
        -------
        data: `pandas.dataframe`
            Modified dataframe.
        """
        return data


class BasicQuery(Query):
    """Simple string data query."""

    def __init__(self, query: str):
        super().__init__()
        self._query = query

    @property
    def query(self):
        return self._query


class QueryPsFlux(Query):
    """Query to get psDiffFlux and psfDiffFluxErr

    Parameters
    ----------
    dia_object_id: `int`
        Object identifier.
    band: `str`
        Selected band.
    """

    _QUERY = (
        "SELECT fsodo.coord_ra, fsodo.coord_dec, "
        "fsodo.diaObjectId, fsodo.ccdVisitId, fsodo.band, "
        "fsodo.psfFlux, fsodo.psfDiffFlux, "
        "fsodo.psfDiffFluxErr, cv.expMidptMJD "
        "FROM dp02_dc2_catalogs.ForcedSourceOnDiaObject as fsodo "
        "JOIN dp02_dc2_catalogs.CcdVisit as cv "
        "ON cv.ccdVisitId = fsodo.ccdVisitId "
        "WHERE fsodo.diaObjectId = {} "
        "AND fsodo.band = '{}'"
    )

    def __init__(self, dia_object_id: int, band: Band):
        super().__init__()
        self._dia_object_id = dia_object_id
        self._band = band
        self._query = QueryPsFlux._QUERY.format(dia_object_id, band)

    @property
    def query(self):
        return self._query


class QueryCoordinateBoundingBox(Query):
    """Query to get calexp information overlapping
    a point between to dates.

    Parameters
    ----------
    ra: `np.float64`
        Coordinate ascension.
    dec: `np.float64`
        Coordinate declination.
    mjd_begin:
        Begin time.
    mjd_end:
        End time.
    """

    _QUERY = (
        "SELECT ra, decl, band, ccdVisitId, expMidptMJD, "
        "llcra, llcdec, ulcra, ulcdec, urcra, urcdec, lrcra, lrcdec "
        "FROM dp02_dc2_catalogs.CcdVisit "
        "WHERE CONTAINS(POINT('ICRS', {}, {}), "
        "POLYGON('ICRS', llcra, llcdec, ulcra, ulcdec, "
        "urcra, urcdec, lrcra, lrcdec)) = 1 "
        "AND expMidptMJD >= {} AND expMidptMJD <= {}"
    )

    def __init__(
        self,
        ra: np.float64,
        dec: np.float64,
        mjd_begin: np.int64,
        mjd_end: np.int64,
    ):
        self._ra = ra
        self._dec = dec
        self._mjd_begin = mjd_begin
        self._mjd_end = mjd_end
        self._query = QueryCoordinateBoundingBox._QUERY.format(
            ra, dec, mjd_begin, mjd_end
        )

    @classmethod
    def from_sky_coord(
        cls, coord: SkyCoord, mjd_begin: np.int64, mjd_end: np.int64
    ):
        """Instantiates a QueryCoordinateBoundingBox
        from a astropy SkyCoord instance.

        Parameters
        ----------
        coord: `astropy.coordinated.SkyCoord`
            Point coordinates.
        mjd_begin:
            Begin time.
        mjd_end:
            End time.
        """
        return cls(coord.ra.value, coord.dec.value, mjd_begin, mjd_end)

    @property
    def query(self):
        return self._query


class QueryExposureData(Query):
    """Exposure data query. Returns
       information from all the exposures
       inside the circumpherence defined
       by a coordinate and a radius.

    Parameters
    ----------
    ra: `np.float64`
        Coordinate ascension.
    dec: `np.float64`
        Coordinate declination.
    radius: `np.float64`
        Circumpherence radius.
    """

    _QUERY = (
        "SELECT coord_ra, coord_dec, objectId, r_extendedness, "
        "scisql_nanojanskyToAbMag(g_cModelFlux) AS mag_g_cModel, "
        "scisql_nanojanskyToAbMag(r_cModelFlux) AS mag_r_cModel, "
        "scisql_nanojanskyToAbMag(i_cModelFlux) AS mag_i_cModel "
        "FROM dp02_dc2_catalogs.Object "
        "WHERE CONTAINS(POINT('ICRS', coord_ra, coord_dec),"
        "CIRCLE('ICRS', {} , {} , {} )) = 1 "
        "AND detect_isPrimary = 1 "
        "AND scisql_nanojanskyToAbMag(r_cModelFlux) < 27.0 "
        "AND r_extendedness IS NOT NULL"
    )

    def __init__(self, ra: np.float64, dec: np.float64, radius: np.float64):
        super().__init__()
        self._ra = ra
        self._dec = dec
        self._radius = radius
        self._query = QueryExposureData._QUERY.format(ra, dec, radius)
        self._data_handler = ExposureDataHandler()

    @classmethod
    def from_sky_coord(cls, coord: SkyCoord, radius: np.float64):
        """Creates a exposure data query"""
        return cls(coord.ra.value, coord.dec.value, radius)

    @property
    def query(self):
        return self._query

    def post_query_actions(self, data: pd.DataFrame):
        return self._data_handler.handle_data(data)

    def _set_data_handler(self, data_handler):
        self._data_handler = data_handler

    data_handler = property(None, _set_data_handler, None, None)


class RaDecCoordinatesToTractPatch(Query):
    """Query to retrieve tract and patch closest to
    the selected coordinate.
    """

    _QUERY = (
        "SELECT coadd.lsst_tract, coadd.lsst_patch, "
        "DISTANCE(POINT('ICRS GEOCENTER',{},{}), "
        "POINT('ICRS GEOCENTER',coadd.s_ra, coadd.s_dec)) as distance "
        "FROM dp02_dc2_catalogs.CoaddPatches as coadd "
        "ORDER BY distance LIMIT {}"
    )

    def __init__(self, ra: float, dec: float, limit: int = 1):
        self._ra = ra
        self._dec = dec
        self._limit = limit
        self._query = RaDecCoordinatesToTractPatch._QUERY.format(
            ra, dec, limit
        )

    @property
    def query(self):
        return self._query

    def post_query_actions(self, data: pd.DataFrame):
        return data


class TAPService:
    """Facade of the TAP service

    Parameters
    ----------
    query: `Optional [str | Query]`
        Query to be launched

    """

    def __init__(self, query: Optional[str | Query] = None):
        self._query = query  # type: Optional[Query]

    @property
    def query(self):
        """Loaded query on the tap service.
        Is the query loaded if fetch method is call.

        Returns
        -------
        query: `Query`
            Query information.

        """
        return self._query

    @query.setter
    def query(self, query: str | Query):
        """Query setter.

        Parameters
        ----------
        query: `str | Query`
            Update query used by the TapService.
        """
        if isinstance(query, str):
            query = Query(str)
        self._query = query

    def fetch(self):
        """Use the tap service to launch the query,
        handle the result, if needed, and return a
        DataWrapper with the retrieved data.

        Returns
        -------
        data: `DataWrapper`
            Result of the query.
        """
        data = self._launch_tap_fetch()
        data = self._query.post_query_actions(data)
        return DataWrapper(data)

    def _launch_tap_fetch(self):
        # Helper function to launch tap query
        service = get_tap_service("tap")
        assert service is not None
        _log.info(f"Fetching Data from query: {self._query.query}")
        job = service.submit_job(self._query.query)
        job.run()
        job.wait(phases=["COMPLETED", "ERROR"])
        job.raise_if_error()
        self._check_status(job.phase)
        _log.info("Converting result to Dataframe")
        return job.fetch_result().to_table().to_pandas()

    def _check_status(self, job_state: str):
        # Helper function to check status
        if job_state == "COMPLETED":
            _log.info("Job phase COMPLETED")
        elif job_state == "ERROR":
            _log.error("Job phase finished with ERROR")
        else:
            _log.info(f"Job phase finished with status {job_state}")
