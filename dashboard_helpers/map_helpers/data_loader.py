"""
Data loading utilities for dashboard.
"""
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from dashboard_helpers.config import (
    DB_PATH, PROVINCE_CODE, PROVINCE_SHAPEFILE, 
    REGION_DATA_DIR, SUBREGION_DATA_DIR
    )


class DataLoader:
    """Handles loading of geocode and spatial data."""

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{DB_PATH}')
        self._geocode_master = None
        self._province_gdf = None
        self._region_gdf_cache = {}
        self._subregion_gdf_cache = {}

    @property
    def geocode_master(self) -> pd.DataFrame:
        """Load geocode master data (cached)."""
        if self._geocode_master is None:
            self._geocode_master = pd.read_sql_table('geocode_master', self.engine)
            self._geocode_master = self._geocode_master[
                self._geocode_master['Province_Code'].astype(str) == str(PROVINCE_CODE)
                ]
        return self._geocode_master

    @property
    def geo_list(self) -> pd.DataFrame:
        """Get list of all geographies (CSD level)."""
        df = self.geocode_master[['Geo_Code', 'Geography']].copy()
        return df[df['Geo_Code'].astype(str).str.len() == 7]

    @property
    def region_list(self) -> pd.DataFrame:
        """Get list of regions (CD level)."""
        df = self.geocode_master[['Region_Code', 'Region']].copy()
        df = df.drop_duplicates(subset='Region_Code')
        df.columns = ['Geo_Code', 'Geography']
        return df[df['Geo_Code'].astype(str).str.len() == 4]

    @property
    def province_list(self) -> pd.DataFrame:
        """Get list of provinces."""
        df = self.geocode_master[['Province_Code', 'Province']].copy()
        df = df.drop_duplicates(subset='Province_Code')
        df.columns = ['Geo_Code', 'Geography']
        return df

    @property
    def dropdown_options(self) -> pd.DataFrame:
        """Get ordered list for dropdown"""
        df = self.geocode_master.copy()
        df['Geography'] = df['Geography'].str.replace(r'^([a-z])', lambda m: m.group(1).upper(), regex=True)
        # df = df.sort_values(by=['Province_Code', 'Region_Code', 'Geo_Code'])
        df = df.sort_values(by=['Geography'])
        
        return df

    @property
    def province_gdf(self) -> gpd.GeoDataFrame:
        """Load province shapefile (cached)."""
        if self._province_gdf is None:
            self._province_gdf = gpd.read_file(PROVINCE_SHAPEFILE)
            self._province_gdf = self._province_gdf[
                self._province_gdf['Geo_Code'] == PROVINCE_CODE
                ]
            self._province_gdf = self._province_gdf.set_index('Geo_Code')
        return self._province_gdf

    def load_region_gdf(self, province_code: int = None) -> gpd.GeoDataFrame:
        """Load region (CD) shapefile for a province (cached)."""
        if province_code is None:
            province_code = PROVINCE_CODE
        if province_code not in self._region_gdf_cache:
            filepath = REGION_DATA_DIR / f"{province_code}.shp"
            gdf = gpd.read_file(filepath, encoding='UTF-8')
            self._region_gdf_cache[province_code] = gdf.set_index('CDUID')
        return self._region_gdf_cache[province_code]

    def load_subregion_gdf(self, region_code: int) -> gpd.GeoDataFrame:
        """Load subregion (CSD) shapefile for a region (cached)."""
        if region_code in self._subregion_gdf_cache:
            return self._subregion_gdf_cache[region_code]
        try:
            filepath = SUBREGION_DATA_DIR / f"{region_code}.shp"
            gdf = gpd.read_file(filepath)
            result = gdf.set_index('CSDUID')
            result.geometry = result.geometry.simplify(tolerance=0.001, preserve_topology=True)
            self._subregion_gdf_cache[region_code] = result
            return result
        except Exception:
            self._subregion_gdf_cache[region_code] = None
            # Fallback to province level if subregion data not available
            return None

    def get_geography_info(self, geography_name: str) -> dict:
        """Get geocode information for a geography name."""
        match = self.geocode_master[self.geocode_master['Geography'] == geography_name]

        if match.empty:
            return None

        row = match.iloc[0]
        return {
            'geo_code': str(row['Geo_Code']),
            'region_code': str(row['Region_Code']),
            'province_code': str(row['Province_Code']),
            'geography': row['Geography'],
            'region': row['Region'],
            'province': row['Province'],
            'level': self._determine_level(str(row['Geo_Code']))
        }

    @staticmethod
    def _determine_level(geocode: str) -> str:
        """Determine geographic level from geocode."""
        if len(geocode) == 2:
            return 'province'
        elif len(geocode) == 4:
            return 'cd'
        elif len(geocode) == 7:
            return 'csd'
        return 'unknown'