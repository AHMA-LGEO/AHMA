import pandas as pd
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master,
    get_original_geocode,
    clean_val,
    YEARS_MINUS_2011,
    INDIGENOUS_COMMUNITIES,
    HH_TYPES
    )


class Section6DataPrep:
  
    def table_6_1_6_6(self, process_table: str) -> pd.DataFrame:
        """
        Table 6.1 and 6.2: Households by Number of Bedrooms in Dwelling (Indigenous & non-Indigenous) (2006, 2016, 2021)
        Table 6.3 and 6.4: Households by Period of Construction of Dwelling (Indigenous & non-Indigenous) (2006, 2016, 2021)
        Table 6.5 and 6.6: Households by Structural Type of Dwelling (Indigenous & non-Indigenous) (2006, 2016, 2021)
        Args:
            process_table:  Specifiy table name to process: either 6.1, 6.2, 6.3, 6.4, 6.5 or 6.6
            """

        if process_table == "6.1":
            print("Processing Table 6.1...")
            category = HH_TYPES
            table_mapper = cm.TABLE_6_1_COL_MAP
            topic = "Households by Number of Bedrooms of Dwelling"
            distinction_type = "Household Type"
        elif process_table == "6.2":
            print("Processing Table 6.2...")
            category = INDIGENOUS_COMMUNITIES
            table_mapper = cm.TABLE_6_2_COL_MAP
            topic = "Households by Number of Bedrooms of Dwelling"
            distinction_type = "Distinction"

        elif process_table == "6.3":
            print("Processing Table 6.3...")
            category = HH_TYPES
            table_mapper = cm.TABLE_6_3_COL_MAP
            topic = "Households by Period of Construction of Dwelling"
            distinction_type = "Household Type"
        elif process_table == "6.4":
            print("Processing Table 6.4...")
            category = INDIGENOUS_COMMUNITIES
            table_mapper = cm.TABLE_6_4_COL_MAP
            topic = "Households by Period of Construction of Dwelling"
            distinction_type = "Distinction"

        elif process_table == "6.5":
            print("Processing Table 6.5...")
            category = HH_TYPES
            table_mapper = cm.TABLE_6_5_COL_MAP
            topic = "Households by Structural Type of Dwelling"
            distinction_type = "Household Type"
        else:
            print("Processing Table 6.6...")
            category = INDIGENOUS_COMMUNITIES
            table_mapper = cm.TABLE_6_6_COL_MAP
            topic = "Households by Structural Type of Dwelling"
            distinction_type = "Distinction"

        dfs = {
            "2006": fetch_data("6.1-6.6", sheets=["2006_IHNAT_T5"]),
            "2016": fetch_data("6.1-6.6", sheets=["2016_IHNAT_T3"]),
            "2021": fetch_data("6.1-6.6", sheets=["2021_IHNAT_T1"])
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for hh_size, year_map in table_mapper.items():
                for cat in category:
                    output_row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        topic: hh_size,
                        distinction_type: cat
                    }

                    #third for loop to get values from column names
                    for year in YEARS_MINUS_2011:
                        df = dfs[year]
                        original_geocode = get_original_geocode(geocode, year)
                        match = df[df["Geocode"] == original_geocode]
            
                        #checking if there is no value and saying continue with logic
                        if match.empty:
                            output_row[year] = None
                            continue
            
                        #creating col_name variable that gets filled in with the column name from the excel that matches the year and cat
                        # {} added to make sure we dont get none when a column name does not exist for a specific year
                        col_name = year_map.get(cat, {}).get(year)
            
                        if col_name is None:
                            output_row[year] = None

                        elif isinstance(col_name, list):
                            raw_vals_sum = (
                                match.reindex(columns=col_name)
                                    .iloc[0]
                                    .map(clean_val)
                                    .pipe(pd.to_numeric, errors="coerce")
                                    .sum(min_count=1)
                            )
                            output_row[year] = raw_vals_sum
            
                        # Direct value if column exists
                        else:
                            if col_name in df.columns:
                                val = match[col_name].iloc[0]
                                output_row[year] = clean_val(val)
                            else:
                                output_row[year] = None
                    
                    rows.append(output_row)

        result = pd.DataFrame(rows)

        # #calculate totals for "Total" rows by summing the non-total hh_size rows per group
         #rows that should be summed

        #for each (Geocode, Household type) group, sum the size rows and assign to "total"
        if process_table == "6.1" or process_table == "6.2":
            cat_rows = list(cm._T6_BEDROOM_KEYS.keys())
            totals = (
                result[result[topic].isin(cat_rows)]
                .groupby(["Geocode", "Geography", distinction_type])[YEARS_MINUS_2011]
                .sum(min_count=1)
            )


        elif process_table == "6.3" or process_table == "6.4":
            cat_rows = list(cm._T6_PERIOD_BUCKETS.keys())
            totals = (
                result[result[topic].isin(cat_rows)]
                .groupby(["Geocode", "Geography", distinction_type])[YEARS_MINUS_2011]
                .sum(min_count=1)
            )

        else:
            cat_rows = list(cm._T6_STRUCTURE_LABELS.keys())
            totals = (
                result[result[topic].isin(cat_rows)]
                .groupby(["Geocode", "Geography", distinction_type])[YEARS_MINUS_2011]
                .sum(min_count=1)
            )

        total_rows = totals.reset_index()
        total_rows[topic] = "Total"
        
        total_rows = total_rows[result.columns]
        # append to original dataframe
        result = pd.concat([result, total_rows], ignore_index=True)

        # Keep total tags at the bottom of geography subgroup
        result["_is_total"] = (result[topic] == "Total").astype(int)
        result = result.sort_values(by=["Geocode", "_is_total", distinction_type]).reset_index(drop=True)

        result = result.drop(columns=["_is_total"])


        if process_table == "6.1":
            print("Table 6.1 is ready now...\n" + '=' * 60)
        elif process_table == "6.2":
            print("Table 6.2 is ready now...\n" + '=' * 60)
        elif process_table == "6.3":
            print("Table 6.3 is ready now...\n" + '=' * 60)
        elif process_table == "6.4":
            print("Table 6.4 is ready now...\n" + '=' * 60)
        elif process_table == "6.5":
            print("Table 6.5 is ready now...\n" + '=' * 60)
        else:
            print("Table 6.6 is ready now...\n" + '=' * 60)

        return result
    
  
    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 6 methods and returns {name:df}"
        return {
            "6.1": self.table_6_1_6_6("6.1"),
            "6.2": self.table_6_1_6_6("6.2"),
            "6.3": self.table_6_1_6_6("6.3"),
            "6.4": self.table_6_1_6_6("6.4"),
            "6.5": self.table_6_1_6_6("6.5"),
            "6.6": self.table_6_1_6_6("6.6"),
        }
    
if __name__ == '__main__':
    t = Section6DataPrep()
    t.table_6_1_6_6("6.3")