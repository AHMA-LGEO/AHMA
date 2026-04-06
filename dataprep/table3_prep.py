import pandas as pd
import numpy as np
import dataprep.column_mapper as cm
from dataprep.sheet_registry import fetch_data
from dataprep.utils import build_master, get_val, sum_bands, pct, clean_val


YEARS = ["2006", "2011", "2016", "2021"]
gender_mapping = {
        'Total - Gender': 'Indigenous',
        '  Men+': 'Men+',
        '  Women+': 'Women+'
    }

class Table3DataPrep:

    def table_3_1_1(self) -> pd.DataFrame:
        print("Processing Table 3.1.1...")
        dfs = {
            "2006": fetch_data("3.1.1", sheets=["2006_Indig_Profile"]),
            "2011": fetch_data("3.1.1", sheets=["2011_Indig_Profile"]),
            "2016": fetch_data("3.1.1", sheets=["2016_Indig_Profile"]),
            "2021": fetch_data("3.1.1", sheets=["2021_Indig_Profile"]),
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for canonical_name, year_col_map in cm.TABLE_3_1_1_COL_MAP.items():
                row = {
                    "Geocode": geocode,
                    "Geography": geography,
                    "Indigenous Population (by CSD)": canonical_name
                }
                for year, col_name in year_col_map.items():
                    df = dfs[year]
                    match = df[df["Geocode"] == geocode]
                    row[year] = match[col_name].iloc[0] if col_name in df.columns and not match.empty else None
                rows.append(row)

        result = pd.DataFrame(rows)

        # add TOTAL row logic below, if suggested not to use the total columns from raw data
        total_rows = []
        for geocode, group in result.groupby("Geocode"):
            total_row = {
                "Geocode": geocode,
                "Geography": group["Geography"].iloc[0],
                "Indigenous Population (by CSD)": "TOTAL",
            }
            for year in YEARS:
                total_row[year] = pd.to_numeric(group[year], errors="coerce").sum()
            total_rows.append(total_row)

        result = (
            pd.concat([result, pd.DataFrame(total_rows)], ignore_index=True)
            .sort_values(["Geocode", "Indigenous Population (by CSD)"])
            .reset_index(drop=True)
        )

        print("Table 3.1.1 is ready now...")
        return result

    def table_3_1_2(self) -> pd.DataFrame:
        print("Processing Table 3.1.2...")
        dfs = {
            "2006": fetch_data("3.1.2", sheets=["2006_Indig_Profile"]),
            "2011": fetch_data("3.1.2", sheets=["2011_Indig_Profile"]),
            "2016": fetch_data("3.1.2", sheets=["2016_Indig_Profile"]),
            "2021": fetch_data("3.1.2", sheets=["2021_Indig_Profile"]),
        }

        master = build_master(dfs)

        metrics = ["Median Age (years)", "% Under 15 years old", "% 65 years or older"]
        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            # filter each year df to this geocode
            year_dfs = {yr: df[df["Geocode"] == geocode].reset_index(drop=True)
                        for yr, df in dfs.items()}

            derived = {metric: {"Geocode": geocode, "Geography": geography,
                                "Age Profile": metric}
                       for metric in metrics}

            for year, df in year_dfs.items():
                col_map = cm.TABLE_3_1_2_COL_MAP

                # Median Age
                median_col = col_map["Median Age"].get(year)
                derived["Median Age (years)"][year] = get_val(df, median_col) if median_col else None

                # Total population for pct denominator
                total_col = col_map["total"].get(year)
                total = get_val(df, total_col)

                # Under 15
                if year in col_map["under_15_direct"]:
                    under_15 = get_val(df, col_map["under_15_direct"][year])
                else:
                    under_15 = sum_bands(df, col_map["under_15_bands"].get(year, []))
                derived["% Under 15 years old"][year] = pct(under_15, total)

                # 65 or older
                if year in col_map["over_65_direct"]:
                    over_65 = get_val(df, col_map["over_65_direct"][year])
                else:
                    over_65 = sum_bands(df, col_map["over_65_bands"].get(year, []))
                derived["% 65 years or older"][year] = pct(over_65, total)

            rows.extend(derived.values())

        print("Table 3.1.2 is ready now...")
        return pd.DataFrame(rows)

    def table_3_1_3(self):
        print("Processing Table 3.1.3...")
        dfs = {
            "2006": fetch_data("3.1.3-3.1.4", sheets=["2006_IHNAT_T6"]),
            "2011": None,  # no data
            "2016": fetch_data("3.1.3-3.1.4", sheets=["2016_IHNAT_T4"]),
            "2021": fetch_data("3.1.3-3.1.4", sheets=["2021_IHNAT_T2"]),
        }
        available_dfs = {yr: df for yr, df in dfs.items() if df is not None}
        master = build_master(available_dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for canonical_name, year_col_map in cm.TABLE_3_1_3_COL_MAP.items():
                row = {
                    "Geocode": geocode,
                    "Geography": geography,
                    "Regional Indigenous Households (by CD)": canonical_name,
                }
                for year in YEARS:
                    if dfs[year] is None:
                        row[year] = None  # no data for 2011
                        continue
                    df = dfs[year][dfs[year]["Geocode"] == geocode].reset_index(drop=True)
                    col = year_col_map.get(year)
                    raw = get_val(df, col) if col else None
                    row[year] = clean_val(raw)
                rows.append(row)

        print("Table 3.1.3 is ready now...")
        return pd.DataFrame(rows)

    def table_3_1_4(self):
        print("Processing Table 3.1.4...")
        dfs = {
            "2006": fetch_data("3.1.3-3.1.4", sheets=["2006_IHNAT_T6"]),
            "2011": None,
            "2016": fetch_data("3.1.3-3.1.4", sheets=["2016_IHNAT_T4"]),
            "2021": fetch_data("3.1.3-3.1.4", sheets=["2021_IHNAT_T2"]),
        }

        available_dfs = {yr: df for yr, df in dfs.items() if df is not None}
        master = build_master(available_dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for canonical_name, year_col_map in cm.TABLE_3_1_4_COL_MAP.items():
                row = {
                    "Geocode": geocode,
                    "Geography": geography,
                    "Number of Indigenous-led HHs who have moved in last 5 years (by CD)...": canonical_name,
                }
                for year in YEARS:
                    if dfs[year] is None:
                        row[year] = None
                        continue
                    df = dfs[year][dfs[year]["Geocode"] == geocode].reset_index(drop=True)
                    col = year_col_map.get(year)
                    raw = get_val(df, col) if col else None
                    row[year] = clean_val(raw)
                rows.append(row)

        print("Table 3.1.4 is ready now...")
        return pd.DataFrame(rows)


    def table_3_4(self) -> pd.DataFrame:
        print("Processing Table 3.4...")

        df_2021 = fetch_data("3.4", sheets=["2021_Indig_Profile"])
        result = []

        for _, geo_row in df_2021.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for age_census, age_label in cm.TABLE_3_4_COL_MAP.items():
                row = {
                    "Geocode": geocode,
                    "Geography": geography,
                    'Age Group - Census 2021': age_label
                }

                for gender_census, gender_label in gender_mapping.items():
                    # Find matching columns
                    pattern_parts = [age_census, gender_census, 'Indigenous identity']
                    matching_cols = [col for col in df_2021.columns
                                     if all(part in col for part in pattern_parts)]

                    df = df_2021[df_2021["Geocode"] == geocode].reset_index(drop=True)
                    raw = get_val(df, matching_cols[0]) if matching_cols else None
                    row[gender_label] = clean_val(raw)

                result.append(row)

        result_df = pd.DataFrame(result)

        print("Table 3.4 is ready now...")
        return result_df

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 3 methods and returns {name:df}"
        return {
            "3.1.1": self.table_3_1_1(),
            "3.1.2": self.table_3_1_2(),
            "3.1.3": self.table_3_1_3(),
            "3.1.4": self.table_3_1_4(),
            "3.4": self.table_3_4()
        }