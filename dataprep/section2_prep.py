import pandas as pd
from sheet_registry import fetch_data, get_sheet


class Section2DataPrep:

    def table_2_1(self) -> pd.DataFrame:
        df = fetch_data("2.1")

        nation_links = get_sheet("Native Land_URLs")

        # FOLLOWING LOGIC FOR GEOCODE = 59, PROVINCE WIDE DATA = EVERYTHING

        # get all unique non-empty nations across columns
        val_cols = [c for c in df.columns if c.startswith('Nation')]

        unique_vals = (
            df[val_cols]
            .stack()
            .dropna()
            .astype(str)
            .str.strip()
        )

        unique_vals = sorted(v for v in unique_vals.unique() if v)

        bc_row = {'Geocode': 59}

        # expand columns if needed
        needed_cols = [f'Nation{i}' for i in range(1, len(unique_vals) + 1)]
        for col in needed_cols:
            if col not in df.columns:
                df[col] = None

        # assign unique values
        bc_row.update(dict(zip(needed_cols, unique_vals)))
        df.loc[len(df)] = bc_row

        return df, nation_links

    def table_2_2(self) -> pd.DataFrame:
        df = fetch_data("2.2")

        # FOLLOWING LOGIC FOR GEOCODE = 59, PROVINCE WIDE DATA = EVERYTHING

        # get all unique values from comma-separated strings
        unique_vals = (
            df["Metis Community"]
            .fillna('')
            .str.split(r"\s*,\s*")   # split on commas + optional spaces
            .explode()
            .str.strip()
        )

        unique_vals = sorted(v for v in unique_vals.unique() if v)

        df.loc[len(df)] = {
            "Geocode": 59, # British Columbia geocode
            "Metis Community": ", ".join(unique_vals)
        }

        return df

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 2 methods and returns {name:df}"
        df_2_1, df_2_1_1 = self.table_2_1()
        return {
            "2.1": df_2_1,
            "2.1.1": df_2_1_1,
            "2.2": self.table_2_2()
        }
    

# For testing
# if __name__ == '__main__':
#     t = Section2DataPrep()
#     t.table_2_1()