import pandas as pd
import numpy as np
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master, 
    get_val, 
    sum_bands, 
    pct, 
    clean_val,
    YEARS,
    YEARS_MINUS_2011,
    POP_SIZES,
    HH_TYPES,
    INDIGENOUS_COMMUNITIES)


INCOME_BRACKETS = [
    ("or under", None, 0.20),   # "20% or under"
    ("21%",      0.20, 0.50),
    ("51%",      0.50, 0.80),
    ("81%",      0.80, 1.20),
    ("121%",     1.20, None),
]

class Section5DataPrep:

    def table_5_1(self) -> pd.DataFrame:
        """Table 5.1: Income and Shelter Cost Category for Indigenous Households"""
        print("Processing Table 5.1...")

        df = fetch_data("5.1", sheets=["2021_HART"])
        
        df.rename(columns=cm.TABLE_5_1_COL_MAP, inplace = True)
        
        for col in df.columns[2:]:
            df[col] = df[col].map(clean_val)

        
        df["Total_Calculated"] = df.iloc[:, 3:8].sum(axis=1, min_count=1)
        df["Area Median Household Income"] = df['AMHI (2020$)']

        df_long = df.melt(
            id_vars=['Geocode', 'Geography'],
            value_vars= ["Area Median Household Income", 
                        "Very Low Income (20% or under of AMHI)", 
                        "Low Income (21% or 50% of AMHI)", 
                        "Moderate Income (51% or 80% of AMHI)", 
                        "Median Income (81% to 120% of AMHI)", 
                        "High Income (121% and more of AMHI)"
                        ],
            var_name='Income Category',
            value_name = 'Total Indigenous HHs').merge(
            df[['Geocode', 'Geography', 'AMHI (2020$)', 'Total_Calculated']],
            on=['Geocode', 'Geography'],
            how='left'
            ).sort_values(['Geocode', 'Geography']).reset_index(drop=True)

        
        mask = df_long["Income Category"] != "Area Median Household Income"

        df_long.loc[mask, "% of Total Indigenous HHs"] = (
            (df_long.loc[mask, "Total Indigenous HHs"] / 
            df_long.loc[mask, "Total_Calculated"].replace(0, float('nan'))) * 100
        ).round(2)

        for idx, row in df_long.iterrows():
            df_long.at[idx, "Annual HH Income"] = self.get_income_range(row["Income Category"], row["AMHI (2020$)"])

            df_long.at[idx, "Affordable Shelter Cost (2020 CAD$)"] = self.get_cost_range(row["Income Category"], row["AMHI (2020$)"])

        result = df_long.drop(columns=['Total Indigenous HHs', "Total_Calculated", 'AMHI (2020$)'])

        print("Table 5.1 is ready now...\n" + '=' * 60)
        return result
    
    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 5 methods and returns {name:df}"
        return {
            "5.1": self.table_5_1(),
        }


    @staticmethod
    def get_income_range(col_name, ahma):
        if pd.isna(ahma):
            return None
        for marker, lo_f, hi_f in INCOME_BRACKETS:
            if marker in col_name:
                lo = ahma * lo_f if lo_f is not None else None
                hi = ahma * hi_f if hi_f is not None else None
                if lo is None: return f"<= ${hi:,.0f}"
                if hi is None: return f">= ${lo:,.0f}"
                return f"${lo:,.0f} - ${hi:,.0f}"
        return f"${ahma:,.0f}"

    @staticmethod
    def get_cost_range(col_name, ahma):
        if pd.isna(ahma):
            return None
        sc = lambda x: x * 0.3 / 12
        for marker, lo_f, hi_f in INCOME_BRACKETS:
            if marker in col_name:
                lo = sc(ahma * lo_f) if lo_f is not None else None
                hi = sc(ahma * hi_f) if hi_f is not None else None
                if lo is None: return f"<= ${hi:,.0f}"
                if hi is None: return f">= ${lo:,.0f}"
                return f"${lo:,.0f} - ${hi:,.0f}"
        return f"${sc(ahma):,.0f}"