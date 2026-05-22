"""
Data loading utilities for all tables.
"""
import pandas as pd
from sqlalchemy import create_engine
from dashboard_helpers.config import DB_PATH


class DataLoader:
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

    def get_table(self, table_name: str, geocode: str = None, check_columns: list = None) -> pd.DataFrame:
        """Load table from database with caching.
        Args:
            table_name: Name of the table to load
            geocode: Optional geocode to filter by
            check_columns: Optional list of columns to check for empty/missing data.
                      If all values in these columns are missing/empty/N/A, returns empty DataFrame.
                      If None (default), no empty check is performed.
    
        Returns:
            Filtered DataFrame, or empty DataFrame if check_columns contains all missing values.
        """
        if table_name not in self._table_cache:
            self._table_cache[table_name] = pd.read_sql_table(table_name, self.engine)

        if geocode:
            mask = (self._table_cache[table_name]['Geocode'] == geocode
                    ) | (self._table_cache[table_name]['Geocode'] == int(geocode))
            df = self._table_cache[table_name][mask]
    
        else:
            df = self._table_cache[table_name].copy()

        # Check if specified columns are all empty/missing
        if check_columns:
            all_missing = (
                df[check_columns]
                .apply(
                    lambda col:
                        col.isna()
                        | (col.astype(str).str.strip() == '')
                        | (col.astype(str).str.strip().str.upper() == 'N/A')
                )
                .all(axis=1)
            )
            
            # Return empty DataFrame if all rows have missing data in check_columns
            if all_missing.all():
                return pd.DataFrame()
        
        return df

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
    

# Module-level dataloader
_shared_loader = None

def get_data_loader() -> DataLoader:
    """
    Return the shared DataLoader instance, creating it on first call.

    All Section Prep classes should use this instead of instantiating
    their own DataLoader so that the table and geocode caches are shared.
    """
    global _shared_loader
    if _shared_loader is None:
        _shared_loader = DataLoader()
    return _shared_loader
