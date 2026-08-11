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
    resolve_op,
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

    def table_4_5_1_4_5_2(self) -> pd.DataFrame:
        """Table 4.5.1 and 4.5.2: HHs by Family Type (becomes externally labelled as 4.5)
        """
        print("Processing Table 4.5...")
        # ---- SETUP ----
        dfs_4_5 = {
            "2006": fetch_data("4.5", sheets=["2006_IHNAT_T5"]),
            "2016": fetch_data("4.5", sheets=["2016_IHNAT_T3"]),
            "2021": fetch_data("4.5", sheets=["2021_IHNAT_T1"])
        }
        master_4_5 = build_master(dfs_4_5)

        # ---- TABLE LOGIC ----
        org_df = dfs_4_5
        master = master_4_5
        COL_MAP = cm.TABLE_4_5_1_4_5_2_COL_MAP
        PCT_REF = cm.PCT_REFS_4_5
        OP_MAP = cm.OP_MAP_4_5

        rows = []
        YEARS = ["2006", "2016", "2021"]
        HH_TYPES = ["Indigenous HHs", "Non-Indigenous HHs"]

        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for category, hh_type_map in COL_MAP.items():
                for hh_type in HH_TYPES:
                    output_row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Family Type": category,
                        "Household Type": hh_type
                    }

                    # third for loop to get values from column names
                    for year in YEARS:
                        df = org_df[year]
                        match = df[df["Geocode"] == geocode]

                        if match.empty:
                            output_row[year] = None
                            continue

                        col_entry = hh_type_map.get(hh_type, {}).get(year)
                        op = OP_MAP.get(category)

                        if col_entry is None:
                            output_row[year] = None

                        # check if values in COL_MAP are a list
                        elif isinstance(col_entry, list):
                            # multi-column: pull all values, apply op
                            raw_vals = [
                                match[c].iloc[0] if c in df.columns else None
                                for c in col_entry
                            ]
                            output_row[year] = resolve_op(op, raw_vals)
                        else:
                            # original single-column path - untouched
                            if col_entry in df.columns:
                                output_row[year] = clean_val(match[col_entry].iloc[0])
                            else:
                                output_row[year] = None
                    rows.append(output_row)
                    # if geocode == 59:
                    #     print(rows)
        result = pd.DataFrame(rows)

        #### Recalculate totals
        # #calculate totals for "Total" rows by summing the non-total hh_size rows per group
        # CAT_ROWS = ["Households with children",
        #             "Households led by a single-parent",
        #             "Number of multigenerational households",
        #             "Number of non-family households (i.e. single or roomates)",
        #             "Apartment in building with fewer than 5 storeys",
        #             "Apartment in building with 5+ storeys",
        #             "Other single-attached house",
        #             "Moveable dwelling"
        #             ]  # rows that should be summed
        # CAT = "Family Type"
        # TYPE = "Household Type"
        # TOTAL_ROW = "Total Households for reference"

        # for year in YEARS:
        #     # for each (Geocode, Household type) group, sum the size rows and assign to "total"
        #     totals = (
        #         result[result[CAT].isin(CAT_ROWS)]
        #         .groupby(["Geocode", TYPE])[year]
        #         .sum(min_count=1)
        #     )

        #     # build a mask for the "Total" rows
        #     # B - not totally sure how to use this in the future
        #     total_mask = result[CAT] == TOTAL_ROW

        #     # map the summed values back using (Geocode, Houshold Type) as the key
        #     # B - not totally sure how to use this in the future
        #     result.loc[total_mask, year] = result[total_mask].apply(
        #         lambda row: totals.get((row["Geocode"], row[TYPE])),
        #         axis=1
        #     )

        #### APPLY PERCENTAGE CALCULATION AFTER FILLING IN VALUE FIELDS IN DATAFRAME

        # pass 2 - fill in % rows
        for pct_category, (num_label, den_label) in PCT_REF.items():
            for year in YEARS:
                num_lookup = (
                    result[result["Family Type"] == num_label]
                    .set_index(["Geocode", "Household Type"])[year]
                )
                den_lookup = (
                    result[result["Family Type"] == den_label]
                    .set_index(["Geocode", "Household Type"])[year]
                )

                pct_mask = result["Family Type"] == pct_category

                # calculate all values first, then write once
                result.loc[pct_mask, year] = result[pct_mask].apply(
                    lambda row: resolve_op("pct", [
                        num_lookup.get((row["Geocode"], row["Household Type"])),
                        den_lookup.get((row["Geocode"], row["Household Type"]))
                    ]),
                    axis=1
                )

        print("Table 4.5 is ready now...\n" + '=' * 60)
        return result

    def table_4_5_3(self) -> pd.DataFrame:
        """Table 4.5.3 : HHs by Family Type and Community (becomes externally labelled as 4.6)
        """

        print("Processing Table 4.6...")
        # ---- SETUP ----
        dfs_4_5 = {
            "2006": fetch_data("4.5", sheets=["2006_IHNAT_T5"]),
            "2016": fetch_data("4.5", sheets=["2016_IHNAT_T3"]),
            "2021": fetch_data("4.5", sheets=["2021_IHNAT_T1"])
        }
        master_4_5 = build_master(dfs_4_5)

        # ---- TABLE LOGIC ----
        org_df = dfs_4_5
        master = master_4_5
        COL_MAP = cm.TABLE_4_5_3_COL_MAP
        PCT_REF = cm.PCT_REFS_4_5
        OP_MAP = cm.OP_MAP_4_5

        rows = []
        YEARS = ["2006", "2016", "2021"]
        SUB_TYPES = ["First Nations-led", "Metis-led", "Inuit-led"]

        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for category, hh_type_map in COL_MAP.items():
                for sub_type in SUB_TYPES:
                    output_row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Family Type": category,
                        "Household Type": sub_type
                    }

                    # third for loop to get values from column names
                    for year in YEARS:
                        df = org_df[year]
                        match = df[df["Geocode"] == geocode]

                        if match.empty:
                            output_row[year] = None
                            continue

                        col_entry = hh_type_map.get(sub_type, {}).get(year)
                        op = OP_MAP.get(category)

                        if col_entry is None:
                            output_row[year] = None

                        # check if values in COL_MAP are a list
                        elif isinstance(col_entry, list):
                            # multi-column: pull all values, apply op
                            raw_vals = [
                                match[c].iloc[0] if c in df.columns else None
                                for c in col_entry
                            ]
                            output_row[year] = resolve_op(op, raw_vals)
                        else:
                            # original single-column path - untouched
                            if col_entry in df.columns:
                                output_row[year] = clean_val(match[col_entry].iloc[0])
                            else:
                                output_row[year] = None
                    rows.append(output_row)
                    # if geocode == 59:
                    #     print(rows)
        result = pd.DataFrame(rows)

        #### APPLY PERCENTAGE CALCULATION AFTER FILLING IN VALUE FIELDS IN DATAFRAME

        # pass 2 - fill in % rows
        for pct_category, (num_label, den_label) in PCT_REF.items():
            for year in YEARS:
                num_lookup = (
                    result[result["Family Type"] == num_label]
                    .set_index(["Geocode", "Household Type"])[year]
                )
                den_lookup = (
                    result[result["Family Type"] == den_label]
                    .set_index(["Geocode", "Household Type"])[year]
                )

                pct_mask = result["Family Type"] == pct_category

                # calculate all values first, then write once
                result.loc[pct_mask, year] = result[pct_mask].apply(
                    lambda row: resolve_op("pct", [
                        num_lookup.get((row["Geocode"], row["Household Type"])),
                        den_lookup.get((row["Geocode"], row["Household Type"]))
                    ]),
                    axis=1
                )

        print("Table 4.6 is ready now...\n" + '=' * 60)
        return result.replace('Metis-led', 'Métis-led')

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 4 methods and returns {name:df}"
        return {
            "4.1": self.table_4_1(),
            "4.2": self.table_4_2(),
            "4.3": self.table_4_3_4_4("4.3"),
            "4.4": self.table_4_3_4_4("4.4"),
            "4.5": self.table_4_5_1_4_5_2(),
            "4.6": self.table_4_5_3(),
        }

# For testing
if __name__ == '__main__':
    t = Section4DataPrep()
    t.table_4_5_1_4_5_2()