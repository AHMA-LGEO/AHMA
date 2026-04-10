"""
Configuration file for dashboard constants and settings.
"""
import os
from pathlib import Path

# Database configuration
DB_DIR = Path(__file__).parent.parent.parent / "source"
DB_PATH = os.path.join(DB_DIR, "ahma.db")

# Province configuration
PROVINCE_CODE = 59
PROVINCE_NAME = "British Columbia"

# Map configuration
MAP_COLORS_WO_BLACK = [
    '#7480dd', '#1a3758', '#7480dd', '#b6657c', '#622637', '#80c2c0',
    '#78cb80', '#ffe6d6', '#e98098', '#a480bb', '#490076', '#008481', '#74d3f9'
]

MAP_COLORS_W_BLACK = [
    '#000000', '#1a3758', '#7480dd', '#b6657c', '#622637', '#80c2c0',
    '#78cb80', '#ffe6d6', '#e98098', '#a480bb', '#490076', '#008481', '#74d3f9'
]

MAP_COLORS_HIGHLIGHT = ['#37BB31', '#74D3F9']
MAP_COLORS_HIGHLIGHT_W_BLACK = ['#000000', '#37BB31', '#74D3F9']

OPACITY_VALUE = 0.2

# Modebar colors
MODEBAR_COLOR = '#099DD7'
MODEBAR_ACTIVECOLOR = '#044762'

# Default selection
DEFAULT_GEOGRAPHY = 'Vancouver CY (CSD, BC)'
DEFAULT_GEOCODE = 5915022  # Vancouver

# Plotly configuration
PLOT_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom', 'lasso2d', 'pan', 'select', 'autoScale', 'resetScale', 'resetViewMapbox']
}

# Page 2 - Table styling
TABLE_COLORS = {
    'geography': '#80875C',
    'headings': '#B5BA9A',
    'row_alt_1': '#E6E8DD',
    'row_alt_2': '#CDD0BB',
    'text': '#000000',
    'border': '#FFFFFF'
}

# Map data paths
MAP_DATA_DIR = Path(__file__).parent.parent.parent / "source" / "mapdata_simplified"
PROVINCE_SHAPEFILE = MAP_DATA_DIR / "province.shp"
REGION_DATA_DIR = MAP_DATA_DIR / "region_data"
SUBREGION_DATA_DIR = MAP_DATA_DIR / "subregion_data"