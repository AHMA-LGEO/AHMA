import pandas as pd
import numpy as np
import column_mapper as cm
from sheet_registry import fetch_data, get_sheet
from utils import (build_master, 
                   get_val, 
                   sum_bands, 
                   pct, 
                   clean_val,
                   HH_TYPES)


class Section9DataPrep:

    def table_9_1(self) -> pd.DataFrame:
        """
        Table 9.1: Number of Indigenous People Released from Corrections by Age Group (2008-2024)
        """
        print("Processing Table 9.1...")
        result = self._build_corrections_table("9.1", cm.TABLE_9_1_COL_MAP)

        print("Table 9.1 is ready now...\n" + '=' * 60)
        return result

    def table_9_1_1(self) -> pd.DataFrame:
        """
        Table 9.1.1: Percent of Indigenous People Released from Corrections by Age Group (2008-2024)
        """
        print("Processing Table 9.1.1...")
        result_indig = self.table_9_1()
        result_all   = self._build_corrections_table("9.1.1", cm.TABLE_9_1_1_COL_MAP)
        result_all.iloc[:, -4:] = round(
            (result_indig.iloc[:, -4:] / result_all.iloc[:, -4:]) * 100, 1
        )

        print("Table 9.1.1 is ready now...\n" + '=' * 60)
        return result_all
    

    def table_9_2(self) -> pd.DataFrame:
        """
        Table 9.2: Number of Indigenous Children Ageing out of Care or Youth Agreements (FY24)
        """
        print("Processing Table 9.2...")

        df_9_2 = get_sheet("MCFD")

        rows = []

        for _, org_df in df_9_2.iterrows():
            geocode = org_df["Geocode"]
            region = org_df["Region"]

            for exit_type, people_group_map in cm.TABLE_9_2_COL_MAP.items():
                output_row = {
                "Geocode":     geocode,
                "Geography":   region,
                "Exit Reason": exit_type,
            }
                for people_group, col_name in people_group_map.items():
                    output_row[people_group] = clean_val(org_df[col_name])
            
                    if col_name and col_name in df_9_2.columns:
                        output_row[people_group] = clean_val(org_df[col_name]) 
                    else:
                        output_row[people_group] = None
            
                rows.append(output_row)

        result = pd.DataFrame(rows)

        #adding "Total Children Ageing Out of Care" row

        #as_index=False keeps those columns as columns instead of making it the index
        totals = (
            result.groupby(["Geocode", "Geography"], as_index=False
                           )[["Indigenous", "Total Population"]].sum().assign(**{"Exit Reason": "Total Children Ageing Out of Care"})
        )

        result = (
            pd.concat([result, totals], ignore_index=True
                      ).sort_values(["Geocode", "Exit Reason"]).reset_index(drop=True)
        )

        result['% Indigenous'] = round((result["Indigenous"] / result["Total Population"])*100, 1)

        print("Table 9.2 is ready now...\n" + '=' * 60)
        return result
    

    def _build_corrections_table(self, table_id: str, col_map: dict) -> pd.DataFrame:
        """Shared logic for table_9_1 and table_9_1_1."""
        df = fetch_data(table_id, sheets=["BC Corrections"])
        rows = []
        for _, org_df in df.iterrows():
            geocode = org_df["Geocode"]
            region  = org_df["Region"]

            for fy, age_group_map in col_map.items():
                output_row = {"Geocode": geocode, "Geography": region, "Year": fy}
                for age_group, col_name in age_group_map.items():
                    output_row[age_group] = (
                        clean_val(org_df[col_name]) if col_name and col_name in df.columns else None
                    )
                rows.append(output_row)
                
        result = pd.DataFrame(rows)
        result['Total'] = result[['Under 30', '30-49', '50+']].sum(axis=1, min_count=3)
        return result

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 9 methods and returns {name:df}"
        return {
            "9.1": self.table_9_1(),
            "9.1.1": self.table_9_1_1(),
            "9.2": self.table_9_2(),
        }
    

