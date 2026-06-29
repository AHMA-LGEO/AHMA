import pandas as pd
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master,
    get_original_geocode,
    clean_val,
    YEARS_2016_2021,
    YEARS_MINUS_2011,
    HH_TYPES,
    INDIGENOUS_COMMUNITIES,
    get_val,
    pct)

INCOME_BRACKETS = [
    ("or under", None, 0.20),   # "20% or under"
    ("121%",     1.20, None),   # must come before "21%" to avoid substring match
    ("21%",      0.20, 0.50),
    ("51%",      0.50, 0.80),
    ("81%",      0.80, 1.20),
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
    

    def table_5_2(self) -> pd.DataFrame:
        """Table 5.2: Households by AMHI Income (2006, 2016, 2021)"""
        print("Processing Table 5.2...")

        dfs = {
            "2006": fetch_data("5.2-5.3", sheets=["2006_IHNAT_T6"]),
            "2016": fetch_data("5.2-5.3", sheets=["2016_IHNAT_T4"]),
            "2021": fetch_data("5.2-5.3", sheets=["2021_IHNAT_T2"])
        }

        dfs_amhi = {
            "2006": fetch_data("5.1", sheets=["2006_HART"]),
            "2016": fetch_data("5.1", sheets=["2016_HART"]),
            "2021": fetch_data("5.1", sheets=["2021_HART"])
        }

        master = build_master(dfs)
        rows = []
        CATEGORY_LABEL = "Households by Income"
        categories = list(cm._T5_2_INCOME_BASE.keys())

        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for income_type, year_map in cm.TABLE_5_2_COL_MAP.items():
                for hh_type in HH_TYPES:
                    output_row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        CATEGORY_LABEL: income_type,
                        "Household Type": hh_type
                    }

                    #third for loop to get values from column names
                    for year in YEARS_MINUS_2011:
                        if income_type not in categories:
                            df = dfs_amhi[year]
                        else:
                            df = dfs[year]
                        
                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]
            
                        #checking if there is no value and saying continue with logic
                        if match.empty:
                            output_row[year] = None
                            continue
            
                        #creating col_name variable that gets filled in with the column name from the excel that matches the year and hh_type
                        # {} added to make sure we dont get none when a column name does not exist for a specific year
                        col_name = year_map.get(hh_type, {}).get(year)
            
                        # Direct value if column exists
                        if col_name and col_name in df.columns:
                            val = match[col_name].iloc[0]
                            output_row[year] = clean_val(val)
                        else:
                            output_row[year] = None
                    
                    rows.append(output_row)

        result = pd.DataFrame(rows)

            #for each (Geocode, Household type) group, sum the size rows and assign to "total"
        totals = (
            result[result[CATEGORY_LABEL].isin(categories)]
            .groupby(["Geocode", "Geography", "Household Type"])[YEARS_MINUS_2011]
            .sum(min_count=1)
        )

        total_rows = totals.reset_index()
        total_rows[CATEGORY_LABEL] = "Total"
        
        total_rows = total_rows[result.columns]
        # append to original dataframe
        result = pd.concat([result, total_rows], ignore_index=True)

        result["_is_total"] = (result[CATEGORY_LABEL] == "Total").astype(int)
        result = result.sort_values(by=["Geocode", "_is_total", "Household Type"]).reset_index(drop=True)

        result = result.drop(columns=["_is_total"])
        
        print("Table 5.2 is ready now...\n" + '=' * 60)
        return result
    

    def table_5_3(self) -> pd.DataFrame:
        """Table 5.3: Households by AMHI Income by Indigenous communities (2006, 2016, 2021)"""
        print("Processing Table 5.3...")

        dfs = {
            "2006": fetch_data("5.2-5.3", sheets=["2006_IHNAT_T6"]),
            "2016": fetch_data("5.2-5.3", sheets=["2016_IHNAT_T4"]),
            "2021": fetch_data("5.2-5.3", sheets=["2021_IHNAT_T2"])
        }

        dfs_amhi = {
            "2006": fetch_data("5.1", sheets=["2006_HART"]),
            "2016": fetch_data("5.1", sheets=["2016_HART"]),
            "2021": fetch_data("5.1", sheets=["2021_HART"])
        }

        master = build_master(dfs)
        CATEGORY_LABEL = "Households by Income"
        categories = list(cm._T5_2_INCOME_BASE.keys())
        
        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for community in INDIGENOUS_COMMUNITIES:
                for income_type, year_map in cm.TABLE_5_3_COL_MAP.items():
                # if income_type == "Area Median Household income (all HHs)":
                
                    output_row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        CATEGORY_LABEL: income_type,
                        "Distinction": community
                    }

                    df_source = dfs_amhi if income_type == "Area Median Household income (all HHs)" else dfs

                    for year in YEARS_MINUS_2011:
                        df = df_source[year]

                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]

                        if match.empty:
                            output_row[year] = None
                            continue

                        col_name = year_map.get(community, {}).get(year)

                        if col_name and col_name in df.columns:
                            output_row[year] = clean_val(match[col_name].iloc[0])
                        else:
                            output_row[year] = None

                    rows.append(output_row)

        result = pd.DataFrame(rows)

        # PATCH WORK - Removing duplicate categories from communities
        # result = result[
        #     ~((result[CATEGORY_LABEL] == "Area Median Household income (all HHs)") & 
        #         (result["Distinction"].isin(["Métis", "Inuit"])))
        # ]
        
        # PATCH WORK - Updating the First Nations to All Distinction Type
        # result.loc[
        #     (result[CATEGORY_LABEL] == "Area Median Household income (all HHs)") & 
        #     (result["Distinction"] == "First Nations"),
        #     "Distinction"
        # ] = "All"

        totals = (
            result[result[CATEGORY_LABEL].isin(categories)]
            .groupby(["Geocode", "Geography", "Distinction"])[YEARS_MINUS_2011]
            .sum(min_count=1)
        )

        total_rows = totals.reset_index()
        total_rows[CATEGORY_LABEL] = "Total"
        
        total_rows = total_rows[result.columns]
        # append to original dataframe
        result = pd.concat([result, total_rows], ignore_index=True)

        result["_is_total"] = (result[CATEGORY_LABEL] == "Total").astype(int)
        result = result.sort_values(by=["Geocode", "_is_total", "Distinction"]).reset_index(drop=True)

        result = result.drop(columns=["_is_total"])

        print("Table 5.3 is ready now...\n" + '=' * 60)
        return result


    def table_5_4(self) -> pd.DataFrame:
        """Table 5.4: Median Household & Per Person Income (2016, 2021)"""
        print("Processing Table 5.4...")

        dfs = {
            "2016": fetch_data("5.4", sheets=["2016_Indig_Profile"]),
            "2021": fetch_data("5.4", sheets=["2021_Indig_Profile"])
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for income_type, year_iden_map in cm.TABLE_5_4_COL_MAP.items():
                for hh_person_iden in year_iden_map['2016']:
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Income type": income_type,
                        "Household/person identity": hh_person_iden
                    }
                    for year in YEARS_2016_2021:
                        df = dfs[year]
                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]

                        if match.empty:
                            row[year] = None
                            continue

                        col_name = year_iden_map.get(year, {}).get(hh_person_iden)
                        
                        # Get the cleaned $ value
                        val = match[col_name].iloc[0]
                        row[year] = clean_val(val)

                    rows.append(row)

        result = pd.DataFrame(rows)

        print("Table 5.4 is ready now...\n" + '=' * 60)
        return result
    
    
    def table_5_5_5_6(self) -> pd.DataFrame:
        """Table 5.5-5.6: Number of Household Maintainers (Indigenous & non-Indigenous)"""
        print("Processing Tables 5.5 & 5.6...")

        dfs = {
            "2016": fetch_data("5.5-5.6", sheets=["2016_Indig_Profile"]),
            "2021": fetch_data("5.5-5.6", sheets=["2021_Indig_Profile"])
        }

        def calc_total(df, year, hh_type):
            """
            Calculates the total number of households for all numbers of maintainers for a given year and household type,
            necessary for calculating the percentage columns and the Total rows.
            """
            total = 0
            for num_maintainers, year_hh_map in cm.TABLE_5_5_5_6_COL_MAP.items():
                if num_maintainers != 'Total':
                    col_name = year_hh_map.get(year, {}).get(hh_type)
                    val = get_val(df, col_name)
                    total += val
            return total

        master = build_master(dfs)

        num_hhs = 'HHs'
        percent_hhs = r'% of Total'

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for num_maintainers, year_hh_map in cm.TABLE_5_5_5_6_COL_MAP.items():
                for hh_type in HH_TYPES:
                    for year in YEARS_2016_2021:
                        row = {
                            "Geocode": geocode,
                            "Geography": geography,
                            "Households by Number of Household Maintainers": num_maintainers,
                            "Household Type": hh_type,
                            "Census Year": year
                        }

                        df = dfs[year]
                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]

                        # If geography doesn't exist in a year, total and % will be null
                        if match.empty:
                            row[num_hhs] = None
                            row[percent_hhs] = None
                            continue
                        
                        # calculate the total hhs for the number of maintainers, year, and hh type, we need it once for every row
                        total = calc_total(match, year, hh_type)

                        # for Total rows we just need the total, no need to calculate percent, we know it is 100%
                        if num_maintainers == 'Total':
                            row[num_hhs] = total
                            row[percent_hhs] = '100' if total else None
                        
                        # for all rows other than Totals, we access the hh value, and calculate the percent 
                        else:
                            col_name = year_hh_map.get(year, {}).get(hh_type)
                            val = get_val(match, col_name)
                            row[num_hhs] = val
                            row[percent_hhs] = pct(val, total)

                        rows.append(row)

        result = pd.DataFrame(rows)

        print("Table 5.5-5.6 is ready now...\n" + '=' * 60)
        return result
    

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 5 methods and returns {name:df}"
        return {
            "5.1": self.table_5_1(),
            "5.2": self.table_5_2(),
            "5.3": self.table_5_3(),
            "5.4": self.table_5_4(),
            "5.5-5.6": self.table_5_5_5_6(),
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

if __name__ == '__main__':
    t = Section5DataPrep()
    t.table_5_3()



    
