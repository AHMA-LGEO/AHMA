import pandas as pd
from dataprep.sheet_registry import fetch_data


class Table2DataPrep:

    def table_2_1(self) -> pd.DataFrame:
        df = fetch_data("2.1")
        return df

    def table_2_2(self) -> pd.DataFrame:
        df = fetch_data("2.2")
        return df

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 2 methods and returns {name:df}"
        return {
            "2.1": self.table_2_1(),
            "2.2": self.table_2_2()
        }