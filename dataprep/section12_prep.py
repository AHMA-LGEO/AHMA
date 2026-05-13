import pandas as pd
import numpy as np
import column_mapper as cm
from sheet_registry import fetch_data


class Section12DataPrep:

    def table_12_2(self) -> pd.DataFrame:
        """Table 12.2: Indigenous Housing Target - Urban, Rural and Northern (off-reserve)"""
        print("Processing Table 12.2...")

        df = (fetch_data("12.2", sheets=["Housing Targets"])
              .rename(columns={'Total Indigenous Housing Need': 'Total Indigenous Housing Need - 2034'}))
        
        df["Rent/affordability assistance (39%)"] = df["Total Indigenous Housing Need - 2034"] * 0.39
        df["Supportive Housing (20%)"] = df["Total Indigenous Housing Need - 2034"] * 0.20
        df["Affordable home ownership (4%)"] = df["Total Indigenous Housing Need - 2034"] * 0.04
        df["Independent subsidized housing (37%)"] = df["Total Indigenous Housing Need - 2034"] * 0.37

        geo_columns = ["Geocode", "Geography"]
        housing_attrs = [attr for attr in df.columns if attr not in geo_columns]
        # attr_order = [
        #     "1. Indigenous HHs in CHN",
        #     "2. LESS Indigenous HHs in CHN and subsidized housing",
        #     "3. PLUS Indigenous PEH from 2023 (4541 people) distributed by CHN",
        #     "4. PLUS New Indigenous households (2024 to 2034) times 15.5%",
        #     "Total Indigenous Housing Need - 2034",
        #     "Rent/affordability assistance (39%)",
        #     "Supportive Housing (20%)",
        #     "Affordable home ownership (4%)",
        #     "Independent subsidized housing (37%)"
        # ]

        df_pivot = pd.melt(df, id_vars=geo_columns, var_name="Calculation of Indigenous Housing Target",
                           value_vars=housing_attrs, value_name= "# of HHs (2034)"
                           )
        # df_pivot['Calculation of Indigenous Housing Target'] = pd.Categorical(df_pivot['Calculation of Indigenous Housing Target'], 
        #                                                                       categories=attr_order, ordered=True)
        
        # df_pivot = df_pivot.sort_values(geo_columns + ["Calculation of Indigenous Housing Target"])
        
        print("Table 12.2 is ready now...\n" + '=' * 60)
        return df_pivot

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 12 methods and returns {name:df}"
        return {
            "12.2": self.table_12_2(),
        }
    
if __name__ == '__main__':
    t = Section12DataPrep()
    t.table_12_2()
