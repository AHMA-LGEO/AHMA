import os
import pandas as pd
import column_mapper as cm
from sheet_registry import ACCESS_DATA_PATH
from utils import build_master, get_val, pct



class Section10DataPrep:
    def table_10_1(self) -> pd.DataFrame:
        """
        Table 10.1: Access to Health Care, Sports & Rec facilities, Primary & Secondary education, Child Care by Public Transit
        """
        print("Processing Table 10.1...")

        df = pd.read_csv(ACCESS_DATA_PATH, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        df = df.reset_index(drop=True)

        dfs = {
            "2021": df
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for service, service_col_map in cm.TABLE_10_1_COL_MAP.items():
                row = {
                    "Geocode": geocode,
                    "Geography": geography,
                    "Service": service,
                }
                df = dfs["2021"]
                match = df[df["Geocode"] == geocode] # Geocode mapping not required, only 2021 data
                
                # if the geography exists, get the total indigenous pop value since we need it to calculate %'s for every row of this geog.
                total_val = get_val(match, cm.TABLE_10_1_COL_MAP[cm._T10_1_TOTAL_COL])

                # if total col, just take the raw total value
                if service == cm._T10_1_TOTAL_COL:
                    for tr_type in cm._T10_1_TRANSPORT_TYPES:
                        row[tr_type] = total_val

                # if buffer col, same calculated percent access value for all transport types
                elif service in cm._T10_1_BUFFER_COLS:
                    access_val = get_val(match, service_col_map)
                    pct_access = pct(access_val, total_val)
                    for tr_type in cm._T10_1_TRANSPORT_TYPES:
                        row[tr_type] = pct_access

                # for all the other columns, calcuate the percent access for each transport type.
                else:
                    for tr_type in cm._T10_1_TRANSPORT_TYPES:
                        access_val = get_val(match, service_col_map[tr_type])
                        row[tr_type] = pct(access_val, total_val)
                            
                rows.append(row)

        result = pd.DataFrame(rows)

        print("Table 10.1 is ready now...\n" + '=' * 60)
        return result

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 10 methods and returns {name:df}"
        return {
            "10.1": self.table_10_1()
        }
    
if __name__ == '__main__':
    t = Section10DataPrep()
    t.table_10_1()