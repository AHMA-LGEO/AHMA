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

class Section5DataPrep:

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
        "Runs all Table 5 methods and returns {name:df}"
        return {
            "5.4": self.table_5_4(),
            "5.5-5.6": self.table_5_5_5_6(),
        }

if __name__ == '__main__':
    t = Section5DataPrep()
    t.table_5_5_5_6()