import pandas as pd
import numpy as np
import column_mapper as cm
from sheet_registry import fetch_data
from utils import (
    build_master, 
    get_val,
    pct, 
    clean_val,
    HH_TYPES,
    POP_SIZES,
    YEARS_MINUS_2011,
    HH_TYPES)

_UNACCEPTABLE_KEYS = [
    "Affordability (Households paying >30% of income on shelter)",
    "Adequacy (Households living in dwellings needing Major Repairs)",
    "Suitability (Households living in overcrowded dwellings)",
    "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)",
]
_ACCEPTABLE_KEY = "Acceptable Housing (Affordable, Adequate, and Suitable)"
_TOTAL_KEY = "Total households (for reference)"


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
                    row_count = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Indicator": indicator,
                        "Metric": "Number of households",
                        "Household Type": hh_type,
                    }
                    row_pct = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Indicator": indicator,
                        "Metric": "% of households",
                        "Household Type": hh_type,
                    }

                    for year in ["2006", "2016", "2021"]:
                        df = dfs[year]
                        match = df[df["Geocode"] == geocode]

                        if match.empty:
                            row_count[year] = None
                            row_pct[year] = None
                            continue

                        col_name = metric_map["Number of households"].get(year, {}).get(hh_type)

                        unaccept_vals = [
                            get_val(match, cm.TABLE_8_1_COL_MAP[k]["Number of households"].get(year, {}).get(hh_type))
                            for k in _UNACCEPTABLE_KEYS
                        ]
                        sum_of_unacceptable = (
                            sum(v for v in unaccept_vals if v is not None)
                            if any(v is not None for v in unaccept_vals) else None
                        )

                        
                        raw_total = get_val(
                            match,
                            cm.TABLE_8_1_COL_MAP[_TOTAL_KEY]["Number of households"].get(year, {}).get(hh_type),
                        )

                        # If total is less than sum of unacceptable categories, reassign the total = sum of unacceptable
                        if raw_total is not None and sum_of_unacceptable is not None:
                            total_val = max(raw_total, sum_of_unacceptable)
                        else:
                            total_val = raw_total if raw_total is not None else sum_of_unacceptable

                        if col_name and col_name in df.columns:
                            count_val = clean_val(match[col_name].iloc[0])
                            # Use corrected total (max of raw vs sum of below categories)
                            if indicator == _TOTAL_KEY:
                                count_val = total_val
                            row_count[year] = count_val
                        elif indicator == _ACCEPTABLE_KEY:
                            if total_val is not None and all(v is not None for v in unaccept_vals):
                                count_val = max(0, total_val - sum_of_unacceptable)
                                row_count[year] = count_val
                            else:
                                count_val = None
                                row_count[year] = None
                        else:
                            count_val = None
                            row_count[year] = None

                        row_pct[year] = pct(count_val, total_val)

                    rows.append(row_count)
                    rows.append(row_pct)

        result = pd.DataFrame(rows)

        print("Table 8.1 is ready now...\n" + '=' * 60)
        return result

    def table_8_3(self) -> pd.DataFrame:
        """
        Table 8.3: Households in Core Housing Need (CHN) or Extreme CHN, by Tenure (Indigenous & non-Indigenous) (2006, 2016, 2021)
        """
        print("Processing Table 8.3...")

        result = self.create_table_8_3_8_4(cm.TABLE_8_3_COL_MAP, HH_TYPES)

        print("Table 8.3 is ready now...\n" + '=' * 60)
        return result

    def table_8_4(self) -> pd.DataFrame:
        """
        Table 8.4: Households in Core Housing Need (CHN) or Extreme CHN, by Tenure (by Indigenous distinction) (2006, 2016, 2021)
        """
        print("Processing Table 8.4...")

        indigenous_distinctions = ["First Nations-led HH", "Métis-led HH", "Inuit-led HH"]
        result = self.create_table_8_3_8_4(cm.TABLE_8_4_COL_MAP, indigenous_distinctions)

        print("Table 8.4 is ready now...\n" + '=' * 60)
        return result

    def create_table_8_3_8_4(self, col_map: dict, distinctions: list) -> pd.DataFrame:
        """
        Does the bulk of the work for tables 8.3 & 8.4 since the logic is the same. 
        Takes the specific column map and list of distinctions i.e. [Indigenous, Non-Indigenous] OR [First Nations-led, Inuit-led, etc.]
        """

        dfs = {
            "2006": fetch_data("8.3-8.4", sheets=["2006_IHNAT_T6"]),
            "2016": fetch_data("8.3-8.4", sheets=["2016_IHNAT_T4"]),
            "2021": fetch_data("8.3-8.4", sheets=["2021_IHNAT_T2"])
        }

        master = build_master(dfs)

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]

            for statistic, year_hh_map in col_map.items():
                for hh_type in distinctions:
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Census Year": statistic,
                        "Household Type": hh_type
                    }

                    for year in YEARS_MINUS_2011:
                        df = dfs[year]
                        match = df[df["Geocode"] == geocode]

                        if match.empty:
                            row[year] = None
                            continue

                        col_name = year_hh_map.get(year, {}).get(hh_type)

                        # Direct value if column already exists in the source table
                        if col_name and col_name in df.columns:
                            val = match[col_name].iloc[0]
                            row[year] = clean_val(val)

                        # Calculate percentages if needed
                        elif statistic in cm._T8_3_8_4_CALC_COLS:

                            calc_cols = cm.TABLE_8_3_8_4_CALC_COL_MAP[year][hh_type]
                            total_cols = calc_cols["total"]
                            renters_cols = calc_cols["renters"]

                            if statistic in ["Rate of CHN (%)", "Rate of Extreme CHN (%)"]:

                                examined_col = total_cols["examined"]
                                examined = get_val(match, examined_col)
                                
                                if statistic == "Rate of CHN (%)":
                                    chn = get_val(match, total_cols["chn"])
                                    row[year] = pct(chn, examined)

                                elif statistic == "Rate of Extreme CHN (%)":
                                    echn = get_val(match, total_cols["echn"])
                                    row[year] = pct(echn, examined)

                            elif statistic in ["% of HHs in CHN who rent", "% of HHs in Extreme CHN who rent"]:
                                
                                if statistic == "% of HHs in CHN who rent":
                                    chn_renters = get_val(match, renters_cols["chn"])
                                    chn_total = get_val(match, total_cols["chn"])
                                    row[year] = pct(chn_renters, chn_total)
                            
                                elif statistic == "% of HHs in Extreme CHN who rent":
                                    echn_renters = get_val(match, renters_cols["echn"])
                                    echn_total = get_val(match, total_cols["echn"])
                                    row[year] = pct(echn_renters, echn_total)
                        else:
                            row[year] = None

                    rows.append(row)

        result = pd.DataFrame(rows)

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
        result[POP_SIZES] = result[POP_SIZES].apply(lambda col: col.map(clean_val))

        totals = (
            result.groupby(["Geocode", "Geography"], as_index=False)[POP_SIZES].sum().assign(**{"Income Type": "Total"})
        )

        result = (
            pd.concat([result, totals], ignore_index=True).sort_values(
                ["Geocode", "Income Type"],
                key=lambda col: col if col.name != "Income Type" else (col=="Total").astype(int)).reset_index(drop=True)
        )

        result['Total'] = result[POP_SIZES].sum(axis=1, skipna=False)

        print("Table 8.7 is ready now...\n" + '=' * 60)
        return result

    
    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 8 methods and returns {name:df}"
        return {
            "8.1": self.table_8_1(),
            "8.3": self.table_8_3(),
            "8.4": self.table_8_4(),
            "8.7": self.table_8_7(),
        }
    
if __name__ == '__main__':
    t = Section8DataPrep()
    t.table_8_3()
    t.table_8_4()