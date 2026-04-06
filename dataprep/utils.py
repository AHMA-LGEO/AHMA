import pandas as pd
import numpy as np


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
    """Replace 'x' and '..' suppressed values with NaN."""
    if pd.isna(val):
        return None
    if str(val).strip().lower() == "x" or str(val).strip().lower() == "..":
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
