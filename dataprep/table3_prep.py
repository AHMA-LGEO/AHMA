import pandas as pd
import numpy as np
import dataprep.column_mapper as cm
from dataprep.sheet_registry import fetch_data
from dataprep.utils import build_master, get_val, sum_bands, pct, clean_val


YEARS = ["2006", "2011", "2016", "2021"]
TABLE_3_2_TOTAL_KEY = "Total - Age groups"
TABLE_3_2_NON_INDIGENOUS_SUFFIX = "Non-indigenous"
# Three named Indigenous identity groups with a 4th group ("Total - Age groups" section)
# uses column names where both sides of '_' strip to the same age key
# (e.g. "0 to 14 years_  0 to 14 years") — handled with pattern matching in table_3_2()
TABLE_3_2_INDIGENOUS_SUFFIXES = ["First Nations", "Metis", "Multiple Indigenous responses"]

GENDER_MAPPING = {
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

    def table_3_2(self) -> pd.DataFrame:
        print("Processing Table 3.2 and 3.3...")

        df_2021 = fetch_data("3.2-3.3", sheets=["2021_Indig_Profile"])

        def find_col(df, age_key, identity):
            """
            Find all column where split on the first '_' gives: left.strip() == age_key  AND  right.strip() == identity.
            Handles the "Total - Age groups" section whose columns appear as
            e.g. '0 to 14 years_  0 to 14 years' (internal whitespace in suffix).
            """
            for col in df.columns:
                idx = col.find('_')
                if idx == -1:
                    continue
                if col[:idx].strip() == age_key and col[idx + 1:].strip() == identity:
                    return col
            return None

        def sum_indigenous(df, age_key):
            """
            Sum counts from all 4 Indigenous groups for a given age key:
              - 3 named groups (First Nations, Metis, Multiple Indigenous responses)
              - "Total - Age groups" group: column where both sides strip to age_key
            """
            total = 0
            found = False
            for suffix in TABLE_3_2_INDIGENOUS_SUFFIXES:
                val = get_val(df, find_col(df, age_key, suffix))
                if val is not None and not np.isnan(val):
                    total += val
                    found = True
            # 4th group: suffix strips to the same label as age_key
            val_4th = get_val(df, find_col(df, age_key, age_key))
            if val_4th is not None and not np.isnan(val_4th):
                total += val_4th
                found = True
            return total if found else None

        result = []
        for _, geo_row in df_2021.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]
            geo_df = df_2021[df_2021["Geocode"] == geocode].reset_index(drop=True)

            # Denominators — total population for each group
            non_indg_total = get_val(geo_df, find_col(geo_df, TABLE_3_2_TOTAL_KEY, TABLE_3_2_NON_INDIGENOUS_SUFFIX))
            indg_total = sum_indigenous(geo_df, TABLE_3_2_TOTAL_KEY)

            for age_key, age_label in cm.TABLE_3_2_COL_MAP.items():
                non_indg_count = get_val(geo_df, find_col(geo_df, age_key, TABLE_3_2_NON_INDIGENOUS_SUFFIX))
                indg_count = sum_indigenous(geo_df, age_key)

                result.append({
                    "Geocode": geocode,
                    "Geography": geography,
                    "Age Group": age_label,
                    "Indigenous Count": indg_count,
                    "Non-Indigenous Count": non_indg_count,
                    "Indigenous %": pct(indg_count, indg_total),
                    "Non-Indigenous %": pct(non_indg_count, non_indg_total),
                    "First Nations": get_val(geo_df, find_col(geo_df, age_key, TABLE_3_2_INDIGENOUS_SUFFIXES[0])), # fetching 0th index = First Nations
                    "Métis": get_val(geo_df, find_col(geo_df, age_key, TABLE_3_2_INDIGENOUS_SUFFIXES[1])), # fetching 1st index = Metis
                    "Inuit": get_val(geo_df, find_col(geo_df, age_key, age_key)), # weird pattern for inuit community??
                    "Multiple/Other Responses": get_val(geo_df, find_col(geo_df, age_key, TABLE_3_2_INDIGENOUS_SUFFIXES[2])), # fetching 2nd index = Multiple Other Responses
                    
                })

        print("Table 3.2 and 3.3 is ready now...")
        return pd.DataFrame(result)


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

                for gender_census, gender_label in GENDER_MAPPING.items():
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
            "3.2": self.table_3_2(),
            "3.4": self.table_3_4()
        }
    

if __name__ == '__main__':
    t = Table3DataPrep()
    t.table_3_2()