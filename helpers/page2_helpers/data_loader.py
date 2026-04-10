"""
Data loading utilities for page 2 tables.
"""
import pandas as pd
from sqlalchemy import create_engine
from helpers.config import DB_PATH


class Page2DataLoader:
    """Handles loading of table data for page 2."""

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{DB_PATH}')
        self._geocode_master = None
        self._table_cache = {}

    @property
    def geocode_master(self) -> pd.DataFrame:
        """Load geocode master data (cached)."""
        if self._geocode_master is None:
            self._geocode_master = pd.read_sql_table('geocode_master', self.engine)
        return self._geocode_master

    def get_table(self, table_name: str) -> pd.DataFrame:
        """
        Load table from database with caching.

        Args:
            table_name: Name of the table to load

        Returns:
            DataFrame with table data
        """
        if table_name not in self._table_cache:
            self._table_cache[table_name] = pd.read_sql_table(table_name, self.engine)
        return self._table_cache[table_name].copy()

    def get_geography_name(self, geocode: int) -> str:
        """Get geography name from geocode."""
        match = self.geocode_master[self.geocode_master['Geo_Code'] == str(geocode)]
        if not match.empty:
            return match['Geography'].iloc[0]
        return None

    def get_geocode(self, geography_name: str) -> int:
        """Get geocode from geography name."""
        match = self.geocode_master[self.geocode_master['Geography'] == geography_name]
        if not match.empty:
            return match['Geo_Code'].iloc[0]
        return None

    def get_region_geocode(self, geocode: int) -> int:
        """Get region code for a given geocode."""
        match = self.geocode_master[self.geocode_master['Geo_Code'] == str(geocode)]
        if not match.empty:
            return match['Region_Code'].iloc[0]
        return None

    def get_province_geocode(self, geocode: int) -> int:
        """Get province code for a given geocode."""
        match = self.geocode_master[self.geocode_master['Geo_Code'] == str(geocode)]
        if not match.empty:
            return match['Province_Code'].iloc[0]
        return None