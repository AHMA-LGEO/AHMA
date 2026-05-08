import pandas as pd
from sheet_registry import fetch_data, get_sheet


class Section2DataPrep:

    def table_2_1(self) -> pd.DataFrame:
        df = fetch_data("2.1")

        nation_links = get_sheet("Native Land_URLs")

        return df, nation_links

    def table_2_2(self) -> pd.DataFrame:
        df = fetch_data("2.2")
        return df

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 2 methods and returns {name:df}"
        df_2_1, df_2_1_1 = self.table_2_1()
        return {
            "2.1": df_2_1,
            "2.1.1": df_2_1_1,
            "2.2": self.table_2_2()
        }
    

if __name__ == '__main__':
    t = Section2DataPrep()
    t.table_2_1()