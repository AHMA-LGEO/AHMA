"""
Configuration file for dashboard constants and settings.
"""
import os
from pathlib import Path

# Database configuration
DB_DIR = Path(__file__).parent.parent / "source"
DB_PATH = os.path.join(DB_DIR, "ahma.db")

YEARS = ["2006", "2011", "2016", "2021"]
YEARS_MINUS_2011 = ["2006", "2016", "2021"]
YEARS_2016_2021 = ["2016", "2021"]
PIT_YEARS = ["2021", "2023", "2025"]
YEARS_2016_TO_2023 = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
YEARLY_INTERVALS_2016_TO_2023 = ["2016-2017", "2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023"]

COMMUNITIES = ['First Nations', 'Métis', 'Inuit']

# Province configuration
PROVINCE_CODE = 59
PROVINCE_NAME = "British Columbia"

# Default selection
DEFAULT_GEOGRAPHY = 'Saanich (CSD, BC)'
DEFAULT_GEOCODE = 5917021  # Saanich

# Map configuration
MAP_COLORS_WO_BLACK = [
    '#7480dd', '#1a3758', '#7480dd', '#b6657c', '#622637', '#80c2c0',
    '#78cb80', '#ffe6d6', '#e98098', '#a480bb', '#490076', '#008481', '#74d3f9'
]

MAP_COLORS_W_BLACK = [
    '#000000', '#1a3758', '#7480dd', '#b6657c', '#622637', '#80c2c0',
    '#78cb80', '#ffe6d6', '#e98098', '#a480bb', '#490076', '#008481', '#74d3f9'
]

MAP_COLORS_HIGHLIGHT = ['#80875C', '#D89A86']
MAP_COLORS_HIGHLIGHT_W_BLACK = ['#000000', '#80875C', '#D89A86']

OPACITY_VALUE = 0.2

# Modebar colors
MODEBAR_COLOR = '#099DD7'
MODEBAR_ACTIVECOLOR = '#044762'

# Plotly configuration
PLOT_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom', 'lasso2d', 'pan', 'select', 'autoScale', 'resetScale', 'resetViewMapbox']
}

# Page 2 - Table styling
TABLE_COLORS = {
    'geography': '#4D5137',
    'columns': '#80875C',
    'headings': '#B5BA9A',
    'row_alt_1': '#E6E8DD',
    'row_alt_2': '#CDD0BB',
    'text': '#000000',
    'border': '#FFFFFF'
}

CHART_COLORS = ['#D0B46A', '#9CA37A', '#C97A63', '#85A7B2',
                '#D89A86', '#4B6470', '#80875C', '#b55438',
                '#1d353d', '#5b2a1c', '#7d6c40', '#4d5137', '#000000']

TABLE_FONT = 'Bahnschrift'

# Map data paths
MAP_DATA_DIR = Path(__file__).parent.parent / "source" / "mapdata_simplified"
PROVINCE_SHAPEFILE = MAP_DATA_DIR / "province.shp"
REGION_DATA_DIR = MAP_DATA_DIR / "region_data"
SUBREGION_DATA_DIR = MAP_DATA_DIR / "subregion_data"