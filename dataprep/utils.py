import pandas as pd
import numpy as np
from typing import Union
from sheet_registry import fetch_data

YEARS = ["2006", "2011", "2016", "2021"]
YEARS_MINUS_2011 = ["2006", "2016", "2021"]
YEARS_2016_2021 = ["2016", "2021"]
YEARS_2016_TO_2023 = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
YEARLY_INTERVALS_2016_TO_2023 = ["2016-2017", "2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023"]
PIT_YEARS = ["2021", "2023", "2025"]
PROJECTION_YEARS = ["2021", "2026", "2031", "2046"]

HH_TYPES = ["Indigenous HHs", "Non-Indigenous HHs"]
INDIGENOUS_COMMUNITIES = ["First Nations", "Métis", "Inuit"]
NO_INFO_VALUES = ["x", "..", "...", "....", "n/a", "N/A", "--", 
                  "xx", "xxx", "xxxx", "xxxxx", "#N/A", "#n/a", '**']
POP_SIZES = ["1 pp", "2 pp", "3 pp", "4 pp", "5+ pp"]

pct_count = 0
over_100_count = 0

_REVERSE_MAPPING = {}

# Define geocode mappings for different scenarios
GEOCODE_MAPPINGS = {
    # Scenario 1: Single geocode in 2006 maps to different one in later years
    "2006_to_later": {
        5919807: 5919822,  # 2006 geocode -> later years geocode
        5933867: 5933881,
        5957801: 5949845,
        5957805: 5949846,
    },
    
    # Scenario 2: Geocodes starting with 5925 in 2006 -> 5926 in later years (last 3 digits same)
    # Comox-Strathcona (5925) (2006) → Comox-Valley (5926) + Strathcona (5924) (2011, 2016, 2021)
    # e.g., 5925005 -> 5926005, 5925010 -> 5926010, etc.
    "5925_to_5926": {
        5925005: 5926005,
        5925010: 5926010,
        5925014: 5926014,
        5925022: 5926022,
        5925024: 5926024,
        5925801: 5926801,
        5925802: 5926802,
        
    },
    
    # Scenario 3: Geocodes starting with 5925 in 2006 -> 5924 in later years (last 3 digits same)
    # Comox-Strathcona (5925) (2006) → Comox-Valley (5926) + Strathcona (5924) (2011, 2016, 2021)
    # e.g., 5925803 -> 5924803, 5925804 -> 5924804, etc.
    "5925_to_5924": {
        5925025: 5924025,
        5925029: 5924029,
        5925030: 5924030,
        5925034: 5924034,
        5925039: 5924039,
        5925042: 5924042,
        5925052: 5924052,
        5925054: 5924054,
        5925803: 5924803,
        5925804: 5924804,
        5925805: 5924805,
        5925806: 5924806,
        5925812: 5924812,
        5925813: 5924813,
        5925814: 5924814,
        5925817: 5924817,
        5925818: 5924818,
        5925820: 5924820,
        5925833: 5924833,
        5925835: 5924835,
        5925836: 5924836,
        5925840: 5924840,
    },

    
    # Scenario 4: Single geocode maps differently across years
    "year_specific_mapping": {
        5933838: {
            "2011": 5933838,
            "2016": 5933898,
            "2021": 5933898,
        }
    },
}


def strip_map(d: dict) -> dict:
    """Recursively strip all string values in a nested dict/list."""
    return {
        k: strip_map(v) if isinstance(v, dict)
           else [s.strip() for s in v] if isinstance(v, list)
           else v.strip() if isinstance(v, str)
           else v
        for k, v in d.items()
    }


def apply_geocode_mapping(df: pd.DataFrame, from_year: str, to_year: str) -> pd.DataFrame:
    """
    Apply geocode mappings to convert geocodes from one year to another.
    
    Args:
        df: DataFrame with 'Geocode' column
        from_year: Source year
        to_year: Target year
    
    Returns:
        DataFrame with mapped geocodes
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Scenario 1: Direct single geocode mappings (2006 to later years)
    if from_year == "2006":
        for old_code, new_code in GEOCODE_MAPPINGS["2006_to_later"].items():
            df.loc[df['Geocode'] == old_code, 'Geocode'] = new_code
    
    # Scenario 2: Specific 5925 -> 5926 mappings
    if from_year == "2006":
        for old_code, new_code in GEOCODE_MAPPINGS["5925_to_5926"].items():
            df.loc[df['Geocode'] == old_code, 'Geocode'] = new_code
    
    # Scenario 3: Specific 5925 -> 5924 mappings
    if from_year == "2006":
        for old_code, new_code in GEOCODE_MAPPINGS["5925_to_5924"].items():
            df.loc[df['Geocode'] == old_code, 'Geocode'] = new_code
    
    # Scenario 4: Year-specific mappings
    for old_code, year_map in GEOCODE_MAPPINGS["year_specific_mapping"].items():
        if to_year in year_map:
            new_code = year_map[to_year]
            df.loc[df['Geocode'] == old_code, 'Geocode'] = new_code
    
    return df
 

def build_master(dfs: dict) -> pd.DataFrame:
    """Prepares master geocode, geography columns, across years
    Applies geocode mappings to ensure consistency across years.
    """
    # union of all geocodes across all years, latest available Geography wins
    # return (
    #     pd.concat([df[["Geocode", "Geography"]] for df in dfs.values() if "Geography" in df.columns]) # because for some reason 2011 data does not have a geography column
    #     .drop_duplicates(subset="Geocode", keep="last")  # keep last = most recent year's Geography
    #     .reset_index(drop=True)
    # )
    
    # Apply mappings to all dfs and track the mappings
    mapped_dfs = {}
    for year, df in dfs.items():
        if df is None or df.empty:
            mapped_dfs[year] = df
            continue
        
        df_mapped = apply_geocode_mapping(df.copy(), year, year)
        mapped_dfs[year] = df_mapped
        
        # Track original -> mapped geocodes
        for orig_code, mapped_code in zip(df['Geocode'], df_mapped['Geocode']):
            if mapped_code not in _REVERSE_MAPPING:
                _REVERSE_MAPPING[mapped_code] = {}
            _REVERSE_MAPPING[mapped_code][year] = orig_code
    
    all_geocodes = set()
    
    # Collect all unique geocodes
    for year, df in mapped_dfs.items():
        if df is not None and not df.empty:
            all_geocodes.update(df['Geocode'].unique())
    
    # Build master with mapped geocodes
    master_list = []
    for geocode in sorted(all_geocodes):
        geo_name = None
        for year, df in mapped_dfs.items():
            if df is not None and not df.empty:
                match = df[df['Geocode'] == geocode]
                if not match.empty and 'Geography' in match.columns:
                    geo_name = match['Geography'].iloc[0]
                    break
        
        if geo_name:
            master_list.append({
                'Geocode': geocode,
                'Geography': geo_name
            })
    
    return pd.DataFrame(master_list)


def get_original_geocode(mapped_geocode: int, year: str) -> int:
    """Get the original geocode for a mapped geocode in a specific year."""
    return _REVERSE_MAPPING.get(mapped_geocode, {}).get(year, mapped_geocode)


def clean_val(val):
    """Replace text values with NaN."""
    if pd.isna(val):
        return None
    if str(val).strip().lower() in NO_INFO_VALUES:
        return None
    return val

def get_val(df: pd.DataFrame, col: str) -> int:
    """Safely get a single numeric value from a df column."""
    if col is None or df.empty:
        return None
    if col in df.columns and not df.empty:
        return pd.to_numeric(df[col].iloc[0], errors="coerce")
    return None


def sum_bands(df: pd.DataFrame, cols: list) -> int:
    """Sum multiple age band columns into one value."""
    if df.empty:
        return None
    vals = [pd.to_numeric(df[c].iloc[0], errors="coerce") for c in cols if c in df.columns]
    return sum(v for v in vals if pd.notna(v)) or None


def pct(numerator: int, denominator: int) -> float:
    """Safe percentage calculation. Limits any calculated percentage over 100 to 100"""
    global pct_count
    global over_100_count

    pct_count += 1
    if numerator is None or denominator is None or denominator == 0:
        return None
    pct = round((numerator / denominator) * 100, 1)
    if pct > 100:
        over_100_count += 1
        return 100
    return pct

def growth_rate(beginning: int , ending: int) -> Union[float, str]:
    """
    Safe growth rate (%) calculation. Undefined growth rates (beginning = 0) return 'No Rate'.
    If either value is 'None', 'None' is returned.
    """
    if beginning is None or ending is None:
        return None
    elif beginning == 0:
        return "No Rate"
    else:
        delta = ending - beginning
        return round((delta / beginning) * 100, 1)

def transform_geocode_master() -> pd.DataFrame:
    """
    Transform master geocode file from nested format to flat structure.

    Input format:
        Geocode | Geography
        59      | British Columbia (59) 20000  (  4.9%)
        5901    |   East Kootenay (5901) 00000  (  7.9%)
        5901043 |     Canal Flats (5901043) 00010  ( 13.8%)

    Output format:
        Geo_Code | Region_Code | Province_Code | Geography | Region | Province
    """

    # Taking example table to fetch all geocodes for 2021, KEEP ONLY 2021 GEOs
    df_2021 = fetch_data("3.5", sheets=["2021_IHNAT_T1"])

    def extract_name(text):
        """Extract clean name from format 'Name (Code) Value ( %)'"""
        if pd.isna(text):
            return text

        # Remove leading spaces and extract name before first parenthesis
        text = text.strip()
        if '(' in text:
            return text.split('(')[0].strip()
        return text
    
    def is_no_info_row(row, exclude_cols, no_info_vals=NO_INFO_VALUES):
        """
        Return True if ALL attribute columns (i.e. not geocode/geo cols)
        contains only 'x', '..', '...' or NaN.
        """
        attr_vals = row.drop(labels=exclude_cols, errors='ignore')
        return attr_vals.apply(
            lambda v: pd.isna(v) or str(v).strip() in no_info_vals
        ).all()

    def determine_level(geocode):
        """Determine geographic level based on geocode length"""
        code_str = str(geocode)
        if len(code_str) == 2:
            return 'province'
        elif len(code_str) == 4:
            return 'cd'  # Census Division / Regional District
        elif len(code_str) == 7:
            return 'csd'  # Census Subdivision
        return 'unknown'

    def add_type_suffix(name, level):
        """Add type suffix to geography name"""
        if pd.isna(name):
            return name
        if level == 'province':
            return f"{name} (Province)"
        elif level == 'cd':
            return f"{name} (CD, BC)"
        elif level == 'csd':
            return f"{name} (CSD, BC)"
        return name
    
    mask_no_info = df_2021.apply(is_no_info_row, axis=1, exclude_cols=["Geocode", "Geography"])
    cleaned_df_2021 = df_2021[~mask_no_info].reset_index(drop=True)

    print(f"Original rows : {len(df_2021)}")
    print(f"No-info rows  : {len(df_2021[mask_no_info])}")
    

    rows = []

    # Track current province and region for hierarchy
    current_province_code = None
    current_province_name = None
    current_region_code = None
    current_region_name = None

    for _, row in cleaned_df_2021.iterrows():
        geocode = str(row['Geocode'])
        geography_raw = row['Geography']

        # Extract clean name
        clean_name = extract_name(geography_raw)
        level = determine_level(geocode)

        # Determine codes and names based on hierarchy
        if level == 'province':
            # Province level
            province_code = geocode
            region_code = geocode
            geo_code = geocode

            province_name = add_type_suffix(clean_name, 'province')
            region_name = province_name
            geography = province_name

            # Update tracking
            current_province_code = province_code
            current_province_name = province_name
            current_region_code = None
            current_region_name = None

        elif level == 'cd':
            # Census Division / Regional District level
            province_code = current_province_code
            region_code = geocode
            geo_code = geocode

            geography = add_type_suffix(clean_name, 'cd')
            region_name = geography
            province_name = current_province_name

            # Update tracking
            current_region_code = region_code
            current_region_name = region_name

        elif level == 'csd':
            # Census Subdivision level
            province_code = current_province_code
            region_code = current_region_code
            geo_code = geocode

            geography = add_type_suffix(clean_name, 'csd')
            region_name = current_region_name
            province_name = current_province_name

        else:
            # Unknown level - use as-is
            province_code = geocode[:2] if len(geocode) >= 2 else geocode
            region_code = geocode[:4] if len(geocode) >= 4 else geocode
            geo_code = geocode
            geography = clean_name
            region_name = clean_name
            province_name = current_province_name

        rows.append({
            'Geo_Code': geo_code,
            'Region_Code': region_code,
            'Province_Code': province_code,
            'Geography': geography,
            'Region': region_name,
            'Province': province_name
        })

    result_df = pd.DataFrame(rows)
    return result_df.sort_values('Geography')