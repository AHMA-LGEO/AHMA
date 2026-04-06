import pandas as pd
import numpy as np
import dataprep.column_mapper as cm
from dataprep.sheet_registry import fetch_data
from dataprep.utils import build_master, get_val, sum_bands, pct, clean_val

YEARS = ["2006", "2011", "2016", "2021"]
HH_TYPES = ["Indigenous HHs", "Non-Indigenous HHs"]
INDIGENOUS_COMMUNITIES = ["First Nations", "Métis", "Inuit"]

class Table4DataPrep:

    def table_4_1(self) -> pd.DataFrame:
        """
        Table 4.1: Housing Tenure - Indigenous vs Non-Indigenous Households
        """
        print("Processing Table 4.1...")

        dfs = {
            "2006": fetch_data("4.1-4.2", sheets=["2006_IHNAT_T6"]),
            "2011": fetch_data("4.1", sheets=["2011_Indig_Profile"]),
            "2016": fetch_data("4.1-4.2", sheets=["2016_IHNAT_T4"]),
            "2021": fetch_data("4.1-4.2", sheets=["2021_IHNAT_T2"]),
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for tenure_type, year_hh_map in cm.TABLE_4_1_COL_MAP.items():
                for hh_type in HH_TYPES:
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Households by Tenure": tenure_type,
                        "Household Type": hh_type
                    }

                    for year in YEARS:
                        df = dfs[year]
                        match = df[df["Geocode"] == geocode]

                        if match.empty:
                            row[year] = None
                            continue

                        col_name = year_hh_map.get(year, {}).get(hh_type)

                        # Direct value if column exists
                        if col_name and col_name in df.columns:
                            val = match[col_name].iloc[0]
                            row[year] = clean_val(val)

                        # Calculate percentages if needed
                        elif tenure_type in ["% of Owners with mortgage",
                                             "% of Owners without a mortgage"] and year in cm.TABLE_4_1_CALC_COLS:
                            calc_cols = cm.TABLE_4_1_CALC_COLS[year].get(hh_type, {})
                            total_owners = get_val(match, cm.TABLE_4_1_COL_MAP["Owner"][year].get(hh_type))

                            if tenure_type == "% of Owners with mortgage":
                                with_mortgage = get_val(match, calc_cols.get("owner_with_mortgage"))
                                row[year] = pct(with_mortgage, total_owners)

                            else:  # without mortgage
                                without_mortgage = get_val(match, calc_cols.get("owner_without_mortgage"))
                                row[year] = pct(without_mortgage, total_owners)

                        elif tenure_type in ["% of Renters in subsidized housing",
                                             "% of Renters not in subsidized housing"] and year in cm.TABLE_4_1_CALC_COLS:
                            calc_cols = cm.TABLE_4_1_CALC_COLS[year].get(hh_type, {})
                            total_renters = get_val(match, cm.TABLE_4_1_COL_MAP["Renter"][year].get(hh_type))

                            if tenure_type == "% of Renters in subsidized housing":
                                subsidized = get_val(match, calc_cols.get("renter_subsidized"))
                                row[year] = pct(subsidized, total_renters)

                            else:  # not subsidized
                                not_subsidized = get_val(match, calc_cols.get("renter_not_subsidized"))
                                row[year] = pct(not_subsidized, total_renters)
                        else:
                            row[year] = None

                    rows.append(row)

        result = pd.DataFrame(rows)

        print("Table 4.1 is ready now...")
        return result

    def table_4_2(self) -> pd.DataFrame:
        """
        Table 4.1 Breakdown / Table 4.2: Housing Tenure by Indigenous Community
        (First Nations, Métis, Inuit)
        Note: 2011 data not available by community breakdown
        """
        print("Processing Table 4.2...")

        dfs = {
            "2006": fetch_data("4.1-4.2", sheets=["2006_IHNAT_T6"]),
            "2016": fetch_data("4.1-4.2", sheets=["2016_IHNAT_T4"]),
            "2021": fetch_data("4.1-4.2", sheets=["2021_IHNAT_T2"]),
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for tenure_type, community_map in cm.TABLE_4_2_COL_MAP.items():
                for community in INDIGENOUS_COMMUNITIES:
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Households by Tenure": tenure_type,
                        "Indigenous Community": community
                    }
                    col_name = community_map.get(community)

                    for year in ["2006", "2016", "2021"]:
                        df = dfs[year]
                        match = df[df["Geocode"] == geocode]

                        if match.empty or col_name not in df.columns:
                            row[year] = None
                        else:
                            val = match[col_name].iloc[0]
                            row[year] = clean_val(val)

                    rows.append(row)

        result = pd.DataFrame(rows)

        print("Table 4.2 is ready now...")
        return result

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 4 methods and returns {name:df}"
        return {
            "4.1": self.table_4_1(),
            "4.2": self.table_4_2(),
        }
