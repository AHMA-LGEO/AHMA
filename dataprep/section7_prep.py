import pandas as pd
import numpy as np
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master,
    get_val,
    sum_bands,
    pct,
    growth_rate,
    clean_val,
    HH_TYPES,
    YEARS_2016_2021,
    YEARS_2016_TO_2023,
    YEARLY_INTERVALS_2016_TO_2023)

class Section7DataPrep:

    def table_7_1_7_2(self) -> pd.DataFrame:
        """
        Table 7.1: Households Median Shelter Cost for Owned & Rented dwellings (Indigenous & non-Indigenous) (2016, 2021)
        """
        print("Processing Table 7.1 and 7.2...")
        dfs_7_1_7_2 = {
            "2016": fetch_data("7.1-7.2", sheets=["2016_Indig_Profile"]),
            "2021": fetch_data("7.1-7.2", sheets=["2021_Indig_Profile"]),
        }

        master_7_1_7_2 = build_master(dfs_7_1_7_2)

        rows = []

        # blanks in for loops, when not refering to a variable in the loop, iterrows goes row by row. Here we are saying index, row
        for _, geo_row in master_7_1_7_2.iterrows():
            # creating geocode and geography attributes to equal the columns in the master df
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            # starting a for loop to get the key and value of the first layer of nested dictionary
            for tenure_type, year_hh_map in cm.TABLE_7_1_7_2_COL_MAP.items():
                # second for loop to get the values of the list HH_TYPES defined above
                for hh_type in HH_TYPES:
                    # assigning values to Geocode, Geography, Median Shelter Cost of Dwelling, and Household Type in row dictionary
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Households by Tenure:": tenure_type,
                        "Household Type": hh_type
                    }
                    # print(row)
                    # third for loop to get the values of the list HHYEAR defined above
                    for year in YEARS_2016_2021:
                        # creating df from dictionary of fetch data dataframes for each year
                        df = dfs_7_1_7_2[year]
                        # creating a datframe of the matched geocodes
                        match = df[df["Geocode"] == geocode]

                        # checking if there is no value saying continue with logic
                        if match.empty:
                            row[year] = None
                            continue

                        # creating col_name variable that gets filled in with the column name from the excel that matches the year and hh_type
                        # {} added to make sure we dont get none when a column name does not exist for a specific year
                        col_name = year_hh_map.get(year, {}).get(hh_type)
                        # print(col_name)

                        # Direct value if column exists
                        if col_name and col_name in df.columns:
                            val = match[col_name].iloc[0]
                            row[year] = clean_val(val)
                        else:
                            row[year] = None

                    rows.append(row)

        result = pd.DataFrame(rows)

        print("Tables 7.1 and 7.2 are ready now...\n" + '=' * 60)
        return result

    def table_7_3_1(self) -> pd.DataFrame:
        """
        Table 7.3.1: Number of Primary and Secondary Rental Units
        """
        print("Processing Table 7.3.1...")

        df_7_3_1 = fetch_data("7.3.1", sheets=["CMHC"])

        #cleaning values in column to do calculation
        for col in df_7_3_1.columns[2:]:
            df_7_3_1[col] = df_7_3_1[col].map(clean_val)

        #calculating secondary renters and dropping all renters columns
        for year in YEARS_2016_2021:
            df_7_3_1[f"{year}_Secondary_Renters"] = (
                df_7_3_1[f"{year}_All_Renters"] - df_7_3_1[f"{year}_Primary_Renters"]
            )
        df_7_3_1 = df_7_3_1.drop(columns=[f"{year}_All_Renters" for year in YEARS_2016_2021])

        # melt to long format
        df_7_3_1_long = df_7_3_1.melt(
            id_vars = ['Geocode', 'Geography'], #columns to keep as is
            var_name='temp', #temporary column for the old column names
            value_name='Value'     
        )

        #split the temp column (e.g. "2016_Primary") into your year and rental type
        df_7_3_1_long[['Year', 'Rental Type']] = df_7_3_1_long['temp'].str.split('_', n=1, expand=True)
        df_7_3_1_long['Rental Type'] = df_7_3_1_long['Rental Type'].str.replace('_', " ")
        df_7_3_1_long = df_7_3_1_long.drop(columns='temp')

        #pivot years back out into columns
        result = df_7_3_1_long.pivot_table(
            index=['Geocode', 'Geography', 'Rental Type'],
            columns='Year',
            values='Value'
        ).reset_index()

        print("Table 7.3.1 is ready now...\n" + '=' * 60)
        return result

    def table_7_3_2_1(self) -> pd.DataFrame:
        """
        Table 7.3.2.1: Average Monthly Rents From 2016 to 2023
        """
        print("Processing Table 7.3.2.1...")

        dfs = {
            "df": fetch_data("7.3.2", sheets=["CMHC"])
        }
        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            row = {
                "Geocode": geocode,
                "Geography": geography,
                "Statistic": "Avg Monthly Rent ($)",
            }

            df = dfs["df"]
            match = df[df["Geocode"] == geocode]

            if match.empty:
                for year in YEARS_2016_TO_2023:
                    row[year] = None
                continue

            for year, col_name in cm.TABLE_7_3_2_1_COL_MAP.items():
                val = match[col_name].iloc[0]
                row[year] = clean_val(val)

            rows.append(row)
        result = pd.DataFrame(rows)
        print("Table 7.3.2.1 is ready now...\n" + '=' * 60)
        return result

    def table_7_3_2_2(self) -> pd.DataFrame:
        """
        Table 7.3.2.2: Annual Change in Average Monthly Rents Between 2016 and 2023
        """
        print("Processing Table 7.3.2.2...")

        dfs = {
            "df": fetch_data("7.3.2", sheets=["CMHC"])
        }
        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            row = {
                "Geocode": geocode,
                "Geography": geography,
                "Statistic": "Change in Average Monthly Rent ($)",
            }

            df = dfs["df"]
            match = df[df["Geocode"] == geocode]

            if match.empty:
                for interval in YEARLY_INTERVALS_2016_TO_2023:
                    row[interval] = None
                continue

            for interval, year_map in cm.TABLE_7_3_2_2_COL_MAP.items():
                # getting the value for the first year
                col_name_y1 = year_map["year_1"]
                val_y1 = get_val(match, col_name_y1)
                
                # getting the value for the second year
                col_name_y2 = year_map["year_2"]
                val_y2 = get_val(match, col_name_y2)

                # calculate the growth rate between year 1 and year 2
                row[interval] = growth_rate(val_y1, val_y2)

            rows.append(row)

        result = pd.DataFrame(rows)
        print("Table 7.3.2.2 is ready now...\n" + '=' * 60)
        return result

    def table_7_3_3_1(self) -> pd.DataFrame:
        """
        Table 7.3.3.1: Vacancy Rates of Primary Rental Units From 2016 to 2023
        """
        print("Processing Table 7.3.3.1...")

        dfs = {
            "df": fetch_data("7.3.3", sheets=["CMHC"])
        }
        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            row = {
                "Geocode": geocode,
                "Geography": geography,
                "Statistic": "Vacancy Rate (%)",
            }

            df = dfs["df"]
            match = df[df["Geocode"] == geocode]

            if match.empty:
                for year in YEARS_2016_TO_2023:
                    row[year] = None
                continue

            for year, col_name in cm.TABLE_7_3_3_1_COL_MAP.items():
                val = match[col_name].iloc[0]
                val_cleaned = clean_val(val)
                # source data has vacancy rate (0-1). Multiplying by 100 to get percentage.
                row[year] = val_cleaned*100 if val_cleaned is not None else None

            rows.append(row)
        result = pd.DataFrame(rows)
        print("Table 7.3.3.1 is ready now...\n" + '=' * 60)
        return result
    
    def table_7_3_3_2(self) -> pd.DataFrame:
        """
        Table 7.3.3.2: Annual Change in Vacancy Rate Between 2016 and 2023
        """
        print("Processing Table 7.3.3.2...")

        dfs = {
            "df": fetch_data("7.3.3", sheets=["CMHC"])
        }
        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            row = {
                "Geocode": geocode,
                "Geography": geography,
                "Statistic": "Change in Vacancy Rate (%)",
            }

            df = dfs["df"]
            match = df[df["Geocode"] == geocode]

            if match.empty:
                for interval in YEARLY_INTERVALS_2016_TO_2023:
                    row[interval] = None
                continue

            for interval, year_map in cm.TABLE_7_3_3_2_COL_MAP.items():
                # getting the value for the first year
                col_name_y1 = year_map["year_1"]
                val_y1 = get_val(match, col_name_y1)
                
                # getting the value for the second year
                col_name_y2 = year_map["year_2"]
                val_y2 = get_val(match, col_name_y2)

                # calculate the growth rate between year 1 and year 2
                row[interval] = growth_rate(val_y1, val_y2)

            rows.append(row)

        result = pd.DataFrame(rows)
        print("Table 7.3.2.2 is ready now...\n" + '=' * 60)
        return result

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 7 methods and returns {name:df}"
        return {
            "7.1-7.2": self.table_7_1_7_2(),
            "7.3.1": self.table_7_3_1(),
            "7.3.2.1": self.table_7_3_2_1(),
            "7.3.2.2": self.table_7_3_2_2(),
            "7.3.3.1": self.table_7_3_3_1(),
            "7.3.3.2": self.table_7_3_3_2()
        }

if __name__ == '__main__':
    t = Section7DataPrep()
    t.table_7_3_2_1()
    t.table_7_3_2_2()
    t.table_7_3_3_1()
    t.table_7_3_3_2()