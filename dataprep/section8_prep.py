import pandas as pd
import numpy as np
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (build_master, 
                   get_val, 
                   sum_bands, 
                   pct, 
                   clean_val,
                   HH_TYPES)

POP_TYPE = ['1pp', '2pp', '3pp', '4pp', '5+pp']

class Section8DataPrep:

    def table_8_1(self) -> pd.DataFrame:
        """
        Table 8.1: Core Housing Need Indicators - Indigenous vs Non-Indigenous
        """
        print("Processing Table 8.1...")

        dfs = {
            "2006": fetch_data("8.1-8.2", sheets=["2006_IHNAT_T5"]),
            "2016": fetch_data("8.1-8.2", sheets=["2016_IHNAT_T3"]),
            "2021": fetch_data("8.1-8.2", sheets=["2021_IHNAT_T1"]),
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for indicator, metric_map in cm.TABLE_8_1_COL_MAP.items():
                for hh_type in HH_TYPES:
                    # Number of households row
                    row_count = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Indicator": indicator,
                        "Metric": "Number of households",
                        "Household Type": hh_type
                    }

                    # % of households row
                    row_pct = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Indicator": indicator,
                        "Metric": "% of households",
                        "Household Type": hh_type
                    }

                    for year in ["2006", "2016", "2021"]:
                        df = dfs[year]
                        match = df[df["Geocode"] == geocode]

                        if match.empty:
                            row_count[year] = None
                            row_pct[year] = None
                            continue

                        col_name = metric_map["Number of households"].get(year, {}).get(hh_type)

                        # Get the count value
                        if col_name and col_name in df.columns:
                            count_val = clean_val(match[col_name].iloc[0])
                            row_count[year] = count_val
                        elif indicator == "Acceptable Housing (Affordable, Adequate, and Suitable)":
                            # Calculate acceptable: Total - Below Adequacy - Below Suitability - Below Affordability - Below Multiple
                            # Reuse existing mappings
                            total_col = cm.TABLE_8_1_COL_MAP["Total households (for reference)"][
                                "Number of households"].get(year, {}).get(hh_type)
                            adequacy_col = \
                            cm.TABLE_8_1_COL_MAP["Adequacy (Households living in dwellings needing Major Repairs)"][
                                "Number of households"].get(year, {}).get(hh_type)
                            suitability_col = \
                            cm.TABLE_8_1_COL_MAP["Suitability (Households living in overcrowded dwellings)"][
                                "Number of households"].get(year, {}).get(hh_type)
                            affordability_col = \
                            cm.TABLE_8_1_COL_MAP["Affordability (Households paying >30% of income on shelter)"][
                                "Number of households"].get(year, {}).get(hh_type)
                            multiple_col = cm.TABLE_8_1_COL_MAP[
                                "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)"][
                                "Number of households"].get(year, {}).get(hh_type)

                            total = get_val(match, total_col)
                            below_adequacy = get_val(match, adequacy_col)
                            below_suitability = get_val(match, suitability_col)
                            below_affordability = get_val(match, affordability_col)
                            below_multiple = get_val(match, multiple_col)

                            # All values must be present to calculate
                            if all(v is not None for v in
                                   [total, below_adequacy, below_suitability, below_affordability, below_multiple]):
                                count_val = total - below_adequacy - below_suitability - below_affordability - below_multiple
                                row_count[year] = count_val
                            else:
                                count_val = None
                                row_count[year] = None
                        else:
                            count_val = None
                            row_count[year] = None

                        # Calculate percentage
                        total_col = cm.TABLE_8_1_COL_MAP["Total households (for reference)"]["Number of households"].get(
                            year, {}).get(hh_type)
                        total_val = get_val(match, total_col)
                        row_pct[year] = pct(count_val, total_val)

                    rows.append(row_count)
                    rows.append(row_pct)

        result = pd.DataFrame(rows)

        print("Table 8.1 is ready now...\n" + '=' * 60)
        return result

    def table_8_7(self) -> pd.DataFrame:
        """
        Table 8.7: Indigenous Affordable Housing Deficit by Income & Household size 2021
        """
        print("Processing Table 8.7...")

        df_8_7 = fetch_data("8.7", sheets=["2021_HART"])

        income_levels = list(next(iter(cm.TABLE_8_7_COL_MAP.values())).keys())

        rows = []
        for income_level in income_levels:
            col_to_size = {
                income_map[income_level]: POP_TYPE
                for POP_TYPE, income_map in cm.TABLE_8_7_COL_MAP.items()
                if income_map.get(income_level) and income_map[income_level] in df_8_7.columns
            }
            row = (
                df_8_7[["Geocode", "Geography"] + list(col_to_size)]
                .rename(columns=col_to_size)
                .assign(**{"Income Type": income_level})
            )
            rows.append(row)

        result = pd.concat(rows, ignore_index=True)
        result[POP_TYPE] = result[POP_TYPE].apply(lambda col: col.map(clean_val))

        totals = (
            result.groupby(["Geocode", "Geography"], as_index=False)[POP_TYPE].sum().assign(**{"Income Type": "Total"})
        )

        result = (
            pd.concat([result, totals], ignore_index=True).sort_values(
                ["Geocode", "Income Type"],
                key=lambda col: col if col.name != "Income Type" else (col=="Total").astype(int)).reset_index(drop=True)
        )

        result['Total'] = result[POP_TYPE].sum(axis=1, skipna=False)

        print("Table 8.7 is ready now...\n" + '=' * 60)
        return result

    
    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Table 8 methods and returns {name:df}"
        return {
            "8.1": self.table_8_1(),
            "8.7": self.table_8_7(),
        }