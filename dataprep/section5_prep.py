import pandas as pd
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master,
    clean_val,
    YEARS_2016_2021,)

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

            for income_type, year_iden_map in cm.TABLE_5_1_COL_MAP.items():
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

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 5 methods and returns {name:df}"
        return {
            "5.4": self.table_5_4(),
            #"5.5": self.table_5_5(),
            #"5.6": self.table_5_6(),
        }

if __name__ == '__main__':
    t = Section5DataPrep()
    t.table_5_4()