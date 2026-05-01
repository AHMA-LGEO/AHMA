import pandas as pd
import numpy as np
from sheet_registry import fetch_data

YEARS = ["2006", "2011", "2016", "2021"]
YEARS_MINUS_2011 = ["2006", "2016", "2021"]
YEARS_2016_2021 = ["2016", "2021"]

HH_TYPES = ["Indigenous HHs", "Non-Indigenous HHs"]
INDIGENOUS_COMMUNITIES = ["First Nations", "Métis", "Inuit"]
NO_INFO_VALUES = ["x", "..", "...", "n/a", "N/A", "--", "xxxxx"]
POP_SIZES = ["1 pp", "2 pp", "3 pp", "4 pp", "5+ pp"]

def strip_map(d: dict) -> dict:
    """Recursively strip all string values in a nested dict/list."""
    return {
        k: strip_map(v) if isinstance(v, dict)
           else [s.strip() for s in v] if isinstance(v, list)
           else v.strip() if isinstance(v, str)
           else v
        for k, v in d.items()
    }


def build_master(dfs: dict) -> pd.DataFrame:
    """Prepares master geocode, geography columns, across years"""
    # union of all geocodes across all years, latest available Geography wins
    return (
        pd.concat([df[["Geocode", "Geography"]] for df in dfs.values() if "Geography" in df.columns]) # because for some reason 2011 data does not have a geography column
        .drop_duplicates(subset="Geocode", keep="last")  # keep last = most recent year's Geography
        .reset_index(drop=True)
    )


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
    """Safe percentage calculation."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round((numerator / denominator) * 100, 1)


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
    return result_df