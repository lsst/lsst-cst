import logging
import pandas as pd
import numpy as np

from abc import ABC, abstractmethod
from astropy.coordinates import SkyCoord
from bokeh.models import ColumnDataSource
from lsst.rsp import get_tap_service
from typing import Optional

_log = logging.getLogger(__name__)

__all__ = ["TAPService", "DataWrapper"]


class DataHandler(ABC):
    """
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def handle_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Action to be taken after the query has been
           launched and data has been retrieved.

        Parameters
        ----------
        data: `pd.Dataframe`
            Exposure data to be handled.

        Returns
        -------
        handled_data: `pd.Dataframe`
            Handled exposure data.
        """
        raise NotImplementedError()


class ExposureDataHandler():
    """Standard actions to be done with a queried
    exposure data fetched from the TAP Service.
    """
    def __init__(self):
        super().__init__()

    def handle_data(self, data: pd.DataFrame):
        data['gmi'] = data['mag_g_cModel'] - data['mag_i_cModel']
        data['rmi'] = data['mag_r_cModel'] - data['mag_i_cModel']
        data['gmr'] = data['mag_g_cModel'] - data['mag_r_cModel']
        data['shape_type'] = data['r_extendedness'].map({0: 'point', 1: 'extended'})
        data['objectId'] = np.array(data['objectId']).astype('str')
        return data


class DataWrapper:
    """Wrapper .

    Parameters
    ----------
    data: `pd.DataFrame`
        Exposure data information.
    """

    def __init__(self, data: pd.DataFrame):
        self._data = data
        self._column_data_source = None

    @property
    def index(self):
        return self._data.columns.tolist()

    @property
    def data(self):
        return self._data

    @classmethod
    def fromFile(cls, file_path: str):
        loaded_df = pd.read_csv(file_path)
        return DataWrapper(loaded_df)

    def get_column_data_source(self):
        if self._column_data_source is None:
            self._column_data_source = ColumnDataSource(self._data)
        return self._column_data_source

    def filter_by_condition(self, column_name, condition, operator='=='):
        operators = {'==': pd.Series.eq,
                     '>': pd.Series.gt,
                     '<': pd.Series.lt}
        assert operator in operators.values(), f"Non valid operator {operator}"

        data = self.data[operators[operator](self.data[column_name], condition)]
        return DataWrapper(data)

    def handle_data(self, handler: DataHandler):
        new_data = handler.handle_data(self._data)
        return DataWrapper(new_data)

    def reduce_data(self, frac: float = 1.0):
        if frac == 1.0:
            return self
        data = self._data.sample(frac=frac, axis='index')
        return DataWrapper(data)

    def histogram(self, field: str):
        return np.histogram(self._data[field], bins='fd')

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

    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def query(self):
        raise NotImplementedError()

    @abstractmethod
    def post_query_actions(self, data: pd.DataFrame):
        pass


class BasicQuery(ABC):

    def __init__(self, query: str):
        super().__init__()
        self._query = query

    @property
    def query(self):
        return self._query

    def post_query_actions(self, data: pd.DataFrame):
        return data


class QueryExposureData(Query):
    _QUERY = "SELECT coord_ra, coord_dec, objectId, r_extendedness, "\
        "scisql_nanojanskyToAbMag(g_cModelFlux) AS mag_g_cModel, "\
        "scisql_nanojanskyToAbMag(r_cModelFlux) AS mag_r_cModel, "\
        "scisql_nanojanskyToAbMag(i_cModelFlux) AS mag_i_cModel "\
        "FROM dp02_dc2_catalogs.Object "\
        "WHERE CONTAINS(POINT('ICRS', coord_ra, coord_dec),"\
        "CIRCLE('ICRS', {} , {} , {} )) = 1 " \
        "AND detect_isPrimary = 1 "\
        "AND scisql_nanojanskyToAbMag(r_cModelFlux) < 27.0 "\
        "AND r_extendedness IS NOT NULL"

    def __init__(self, ra: np.float64, dec: np.float64, radius: np.float64):
        super().__init__()
        self._ra = ra
        self._dec = dec
        self._radius = radius
        self._query = QueryExposureData._QUERY.format(ra, dec, radius)
        self._data_handler = ExposureDataHandler()

    @classmethod
    def from_sky_coord(cls, coord: SkyCoord, radius: np.float64):
        """
        """
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

    _QUERY = "SELECT coadd.lsst_tract, coadd.lsst_patch, "\
             "DISTANCE(POINT('ICRS GEOCENTER',{},{}), "\
             "POINT('ICRS GEOCENTER',coadd.s_ra, coadd.s_dec)) as distance "\
             "FROM dp02_dc2_catalogs.CoaddPatches as coadd "\
             "ORDER BY distance LIMIT {}"

    def __init__(self, ra: float, dec: float, limit: int = 1):
        self._ra = ra
        self._dec = dec
        self._limit = limit
        self._query = RaDecCoordinatesToTractPatch._QUERY.format(ra, dec, limit)

    @property
    def query(self):
        return self._query

    def post_query_actions(self, data: pd.DataFrame):
        return data


class TAPService:

    def __init__(self, query: Optional[str] = None):
        self._query = query  # type: Optional[Query]

    def has_data(self):
        """
        """
        return not self._data.empty

    @property
    def query(self):
        """"""
        return self._query

    @query.setter
    def query(self, query: str | Query):
        """"""
        if isinstance(query, str):
            query = Query(str)
        self._query = query

    def fetch(self):
        """
        """
        data = self._launch_tap_fetch()
        data = self._query.post_query_actions(data)
        return DataWrapper(data)

    def _launch_tap_fetch(self):
        # Helper function to launch tap query
        service = get_tap_service("tap")
        assert service is not None
        _log.info("Fetching Data")
        job = service.submit_job(self._query)
        job.run()
        job.wait(phases=['COMPLETED', 'ERROR'])
        job.raise_if_error()
        self._check_status(job.phase)
        _log.info("Converting result to Dataframe")
        return job.fetch_result().to_table().to_pandas()

    def _check_status(self, job_state: str):
        # Helper function to check status
        if job_state == 'COMPLETED':
            _log.info("Job phase COMPLETED")
        elif job_state == 'ERROR':
            _log.error("Job phase finished with ERROR")
        else:
            _log.info(f"Job phase finished with status {job_state}")

    @property
    def query(self):
        """"""
        return self._query
