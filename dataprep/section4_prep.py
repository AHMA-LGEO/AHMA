import pandas as pd
import numpy as np
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master, 
    get_original_geocode,
    get_val,
    pct, 
    clean_val,
    YEARS,
    YEARS_MINUS_2011,
    POP_SIZES,
    HH_TYPES,
    INDIGENOUS_COMMUNITIES)


class Section4DataPrep:

    def table_4_1(self) -> pd.DataFrame:
        """Table 4.1: Housing Tenure - Indigenous vs Non-Indigenous Households"""
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
                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]

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

        result_df = pd.DataFrame(rows)

        total_rows = []
        for (geocode, hh_type), group in result_df.groupby(["Geocode", "Household Type"]):

            filtered_group = group[group["Households by Tenure"].isin(['Owner', 'Renter', 
                                                                       'Dwelling provided by local government or First Nation'])]
            
            total_row = {
                "Geocode": geocode,
                "Geography": group["Geography"].iloc[0],
                "Households by Tenure": "Total",
                "Household Type": hh_type,
            }
            for year in YEARS:
                total_row[year] = pd.to_numeric(filtered_group[year], errors="coerce").sum()
            total_rows.append(total_row)

        attr_order = [
            "Owner",
            "Renter",
            "Dwelling provided by local government or First Nation",
            "Total",
            "% of Owners with mortgage",
            "% of Owners without a mortgage",
            "% of Renters in subsidized housing",
            "% of Renters not in subsidized housing"
        ]

        result = pd.concat([result_df, pd.DataFrame(total_rows)], ignore_index=True)

        result["Households by Tenure"] = pd.Categorical(result["Households by Tenure"],
                                                        categories=attr_order, ordered=True)

        result = (result.sort_values(
            ["Geocode", "Household Type", "Households by Tenure"],
            na_position="last").reset_index(drop=True))

        print("Table 4.1 is ready now...\n" + '=' * 60)
        return result

    def table_4_2(self) -> pd.DataFrame:
        """
        Table 4.1 Breakdown / Table 4.2: Housing Tenure by Indigenous Community
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

            for tenure_type, year_community_map in cm.TABLE_4_2_COL_MAP.items():
                for community in INDIGENOUS_COMMUNITIES:
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Households by Tenure": tenure_type,
                        "Indigenous Community": community
                    }

                    for year in YEARS_MINUS_2011:
                        df = dfs[year]
                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]

                        if match.empty:
                            row[year] = None
                            continue

                        col_name = year_community_map.get(year, {}).get(community)

                        # Direct value if column exists
                        if col_name and col_name in df.columns:
                            val = match[col_name].iloc[0]
                            row[year] = clean_val(val)

                        # Calculate percentages if needed
                        elif tenure_type in ["% of Owners with mortgage",
                                             "% of Owners without a mortgage"] and year in cm.TABLE_4_2_CALC_COLS:
                            calc_cols = cm.TABLE_4_2_CALC_COLS[year].get(community, {})
                            total_owners = get_val(match, cm.TABLE_4_2_COL_MAP["Owner"][year].get(community))

                            if tenure_type == "% of Owners with mortgage":
                                with_mortgage = get_val(match, calc_cols.get("owner_with_mortgage"))
                                row[year] = pct(with_mortgage, total_owners)

                            else:  # without mortgage
                                without_mortgage = get_val(match, calc_cols.get("owner_without_mortgage"))
                                row[year] = pct(without_mortgage, total_owners)

                        elif tenure_type in ["% of Renters in subsidized housing",
                                             "% of Renters not in subsidized housing"] and year in cm.TABLE_4_2_CALC_COLS:
                            calc_cols = cm.TABLE_4_2_CALC_COLS[year].get(community, {})
                            total_renters = get_val(match, cm.TABLE_4_2_COL_MAP["Renter"][year].get(community))

                            if tenure_type == "% of Renters in subsidized housing":
                                subsidized = get_val(match, calc_cols.get("renter_subsidized"))
                                row[year] = pct(subsidized, total_renters)

                            else:  # not subsidized
                                not_subsidized = get_val(match, calc_cols.get("renter_not_subsidized"))
                                row[year] = pct(not_subsidized, total_renters)
                        else:
                            row[year] = None

                    rows.append(row)

        result_df = pd.DataFrame(rows)

        total_rows = []
        for (geocode, community), group in result_df.groupby(["Geocode", "Indigenous Community"]):
            
            filtered_group = group[group["Households by Tenure"].isin(['Owner', 'Renter', 
                                                                       'Dwelling provided by local government or First Nation'])]

            total_row = {
                "Geocode": geocode,
                "Geography": group["Geography"].iloc[0],
                "Households by Tenure": "Total",
                "Indigenous Community": community,
            }
            for year in YEARS_MINUS_2011:
                total_row[year] = pd.to_numeric(filtered_group[year], errors="coerce").sum()
            total_rows.append(total_row)

        # result = (
        #     pd.concat([result_df, pd.DataFrame(total_rows)], ignore_index=True)
        #     .sort_values(["Geocode", "Indigenous Community", "Households by Tenure"])
        #     .reset_index(drop=True)
        # )
        attr_order = [
            "Owner",
            "Renter",
            "Dwelling provided by local government or First Nation",
            "Total",
            "% of Owners with mortgage",
            "% of Owners without a mortgage",
            "% of Renters in subsidized housing",
            "% of Renters not in subsidized housing"
        ]

        result = pd.concat([result_df, pd.DataFrame(total_rows)], ignore_index=True)

        result["Households by Tenure"] = pd.Categorical(result["Households by Tenure"],
                                                        categories=attr_order, ordered=True)

        result = (result.sort_values(
            ["Geocode", "Indigenous Community", "Households by Tenure"],
            na_position="last").reset_index(drop=True))

        print("Table 4.2 is ready now...\n" + '=' * 60)
        return result
    
    def table_4_3_4_4(self, process_table: str) -> pd.DataFrame:
        """Table 4.3 and 4.4: HHs by Household size
        Args:
            process_table:  Specifiy table name to process: either 4.3 or 4.4
        """
        if process_table == "4.3":
            print("Processing Table 4.3...")
            category = HH_TYPES
            table_mapper = cm.TABLE_4_3_4_4_COL_MAP
        else:
            print("Processing Table 4.4...")
            category = [comm + "-led Households by Size (number of people)"  for comm in INDIGENOUS_COMMUNITIES]
            table_mapper = cm.TABLE_4_3_1_COL_MAP

        dfs = {
            "2006": fetch_data("4.3", sheets=["2006_IHNAT_T5"]),
            "2016": fetch_data("4.3", sheets=["2016_IHNAT_T3"]),
            "2021": fetch_data("4.3", sheets=["2021_IHNAT_T1"])
        }
        master = build_master(dfs)

        rows = []

        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for hh_size, year_map in table_mapper.items():
                for cat in category:
                    output_row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Households by Size (number of people)": hh_size,
                        "Household Type": cat
                    }

                    for year in YEARS_MINUS_2011:
                        df = dfs[year]
                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]
            
                        if match.empty:
                            output_row[year] = None
                            continue
            
                        col_name = year_map.get(cat, {}).get(year)
            
                        if col_name and col_name in df.columns:
                            val = match[col_name].iloc[0]
                            output_row[year] = clean_val(val)
                        else:
                            output_row[year] = None
                    
                    rows.append(output_row)

        result = pd.DataFrame(rows)

        
        for year in YEARS_MINUS_2011:
            totals = (
                result[result["Households by Size (number of people)"].isin(POP_SIZES)]
                .groupby(["Geocode", "Household Type"])[year]
                .sum(min_count=1)
            )

            total_mask = result["Households by Size (number of people)"] == "Total"

            result.loc[total_mask, year] = result[total_mask].apply(
                lambda row: totals.get((row["Geocode"], row["Household Type"])),
                axis=1
            )

        if process_table == "4.3":
            print("Table 4.3 is ready now...\n" + '=' * 60)
        else:
            print("Table 4.4 is ready now...\n" + '=' * 60)

        return result
    

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 4 methods and returns {name:df}"
        return {
            "4.1": self.table_4_1(),
            "4.2": self.table_4_2(),
            "4.3": self.table_4_3_4_4("4.3"),
            "4.4": self.table_4_3_4_4("4.4"),
        }

# For testing
# if __name__ == '__main__':
#     t = Section4DataPrep()
#     t.table_4_3_4_4("4.3")