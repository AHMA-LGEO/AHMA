import pandas as pd
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master,
    clean_val,
    YEARS_2016_2021,
    HH_TYPES,
    get_val,
    pct)

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

    def table_5_4(self) -> pd.DataFrame:
        """
        Table 5.4: Median Household & Per Person Income (2016, 2021)
        """
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
                        match = df[df["Geocode"] == geocode]

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
        """
        Table 5.5-5.6: Number of Household Maintainers (Indigenous & non-Indigenous)
        """
        print("Processing Tables 5.5 & 5.6...")

        dfs = {
            "2016": fetch_data("5.5-5.6", sheets=["2016_Indig_Profile"]),
            "2021": fetch_data("5.5-5.6", sheets=["2021_Indig_Profile"])
        }

        def calc_total(df, year, hh_type):
            """
            Calculates the total number of households for all numbers of maintainers for a given year and household type,
            necessary for calculating the percentage columns and the TOTAL rows.
            """
            total = 0
            for num_maintainers, year_hh_map in cm.TABLE_5_5_5_6_COL_MAP.items():
                if num_maintainers != 'TOTAL':
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
                        match = df[df["Geocode"] == geocode]

                        # If geography doesn't exist in a year, total and % will be null
                        if match.empty:
                            row[num_hhs] = None
                            row[percent_hhs] = None
                            continue
                        
                        # calculate the total hhs for the number of maintainers, year, and hh type, we need it once for every row
                        total = calc_total(match, year, hh_type)

                        # for TOTAL rows we just need the total, no need to calculate percent, we know it is 100%
                        if num_maintainers == 'TOTAL':
                            row[num_hhs] = total
                            row[percent_hhs] = '100' if total else None
                        
                        # for all rows other than TOTALs, we access the hh value, and calculate the percent 
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
    t.table_5_5_5_6()



    
