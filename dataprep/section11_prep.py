import pandas as pd
import column_mapper as cm
from sheet_registry import get_sheet, fetch_data
from utils import (
    build_master, 
    get_val,
    PROJECTION_YEARS, 
    growth_rate)

class Section11DataPrep:
    def table_11_1_1(self) -> pd.DataFrame:
        """
        Table 11.1.1: Projected Population of Indigenous People (First Nations, Metis, Inuit, or Other) 2021-2046
        """
        print("Processing Table 11.1.1...")

        # 11.1 sheet is missing geography column, joining geography column from another 2021 sheet.
        df_BC_Stats = fetch_data("11.1", sheets=["BC Stats Projections"])
        df_2021_T1 = get_sheet("2021_IHNAT_T1")
        df = df_2021_T1[["Geocode", "Geography"]].merge(df_BC_Stats, on='Geocode', how='outer')

        master = build_master({"df": df})

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]
            match = df[df["Geocode"] == geocode] #  Geocode mapping not required, only 2021 data

            # for a given geography, initialize a new dict in order to store pop values
            pop_vals = { year: {} for year in PROJECTION_YEARS }

            # for each population count (i.e. First Mations, Inuit, etc.)
            for indigenous_pop, year_col_map in cm.TABLE_11_1_1_COL_MAP.items():

                # if not total, which should be the last loop iteration, calculate and populate num hhs and % change for all years
                if indigenous_pop != "Total": 
                    # grab the population values for all the years
                    for year in PROJECTION_YEARS:
                        # store the value in our dictionary
                        pop_vals[year][indigenous_pop] = get_val(match, year_col_map[year])

                # calculate the totals
                elif indigenous_pop == "Total":
                    for year in PROJECTION_YEARS:
                        vals = list(pop_vals[year].values())

                        # if all the values are None, we want to maintain a total of None
                        if all(v is None for v in vals):
                            pop_vals[year]["Total"] = None
                        else:
                            pop_vals[year]["Total"] = sum([v for v in vals if v is not None and v == v])

                # create a row for each metric
                for metric in ["Estimate", "Projection", "% Change from 2021"]:
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Population Count": indigenous_pop,
                        "Metric": metric
                    }

                    # estimate row is only for 2021 pop, all the other years populate with None
                    if metric == "Estimate":    
                        for year in PROJECTION_YEARS:
                            if year == "2021":
                                row[year] = pop_vals[year][indigenous_pop]
                            else:
                                row[year] = None
                    
                    # if pop. projection row, populate the values for all years except 2021
                    elif metric == "Projection":
                        for year in PROJECTION_YEARS:
                            if year == "2021":
                                row[year] = None
                            else:
                                row[year] = pop_vals[year][indigenous_pop]

                    # if % change row, calculate the % change for all rows but 2021
                    elif metric == "% Change from 2021":
                        for year in PROJECTION_YEARS:
                            if year == "2021": 
                                row[year] = None
                            else:
                                row[year] = growth_rate(pop_vals["2021"][indigenous_pop], pop_vals[year][indigenous_pop])
                    
                    rows.append(row)

        result = pd.DataFrame(rows)

        print("Table 11.1.1 is ready now...\n" + '=' * 60)
        return result

    def table_11_1_2(self) -> pd.DataFrame:
        """
        Table 11.1.2: Projected Number of Indigenous Households (First Nations, Metis, Inuit, or Other) 2021-2046
        """
        print("Processing Table 11.1.2...")

        def calc_num_hhs(pop: int, hh_size: float) -> float:
            """
            Safely Calculates an estimated number of households (rounded to nearest whole number), given a population
            and average household size, if household size or population is None, returns None
            """
            if hh_size is None or hh_size == 0:
                return None
            else:
                return round(pop/hh_size, 0)

        # 11.1 sheet is missing geography column, joining geography column from another 2021 sheet.
        df_BC_Stats = fetch_data("11.1", sheets=["BC Stats Projections"])
        df_2021_T1 = get_sheet("2021_IHNAT_T1")
        df = df_2021_T1[["Geocode", "Geography"]].merge(df_BC_Stats, on='Geocode', how='outer')

        master = build_master({"df": df})

        rows = []
        for _, geo_row in master.iterrows():
            geocode = geo_row["Geocode"]
            geography = geo_row["Geography"]
            match = df[df["Geocode"] == geocode]  # Geocode mapping not required, only 2021 data

            # for a given geography, initialize a new dict in order to efficiently calculate totals and growth rates
            num_hhs = { year: {} for year in PROJECTION_YEARS }

            # Pre-compute HH sizes with fallback logic before the main loop
            _hh_fn    = get_val(match, cm.TABLE_11_1_2_COL_MAP["First Nations"]["Avg. Indigenous HH size (Province, 2021)"])
            _hh_metis = get_val(match, cm.TABLE_11_1_2_COL_MAP["Métis"]["Avg. Indigenous HH size (Province, 2021)"])
            _hh_inuit = get_val(match, cm.TABLE_11_1_2_COL_MAP["Inuit"]["Avg. Indigenous HH size (Province, 2021)"])
            _hh_other = get_val(match, cm.TABLE_11_1_2_COL_MAP["Other Indigenous"]["Avg. Indigenous HH size (Province, 2021)"])

            def _has_val(v):
                return v is not None and not pd.isna(v)

            if _has_val(_hh_other) and not _has_val(_hh_metis) and not _has_val(_hh_inuit):
                _hh_metis = _hh_other
                _hh_inuit = _hh_other
            elif not _has_val(_hh_other) and _has_val(_hh_fn):
                _hh_metis = _hh_fn
                _hh_inuit = _hh_fn
                _hh_other = _hh_fn

            hh_size_overrides = {
                "First Nations": _hh_fn,
                "Métis": _hh_metis,
                "Inuit": _hh_inuit,
                "Other Indigenous": _hh_other,
            }

            # for each population count (i.e. First Mations, Inuit, etc.)
            for indigenous_pop, year_col_map in cm.TABLE_11_1_2_COL_MAP.items():

                # if not total, which should be the last loop iteration, calculate and populate num hhs and % change for all years
                if indigenous_pop != "Total":
                    # calculate estimated number of households for all the years
                    hh_size = hh_size_overrides.get(
                        indigenous_pop,
                        get_val(match, year_col_map["Avg. Indigenous HH size (Province, 2021)"])
                    )
                    for year in PROJECTION_YEARS:
                        pop = get_val(match, year_col_map[year])
                        # store the value in our dictionary
                        num_hhs[year][indigenous_pop] = calc_num_hhs(pop, hh_size)

                # calculate the totals
                elif indigenous_pop == "Total":
                    for year in PROJECTION_YEARS:
                        vals = list(num_hhs[year].values())

                        # if all the values are None, we want to maintain a total of None
                        if all(v is None for v in vals):
                            num_hhs[year]["Total"] = None
                        else:
                            num_hhs[year]["Total"] = sum([v for v in vals if v is not None and v == v])

                # create a row for each metric
                for metric in ["Estimate", "Projection", "% Change from 2021"]:
                    row = {
                        "Geocode": geocode,
                        "Geography": geography,
                        "Household Count": indigenous_pop,
                        "Metric": metric
                    }

                    # populate the average hh size column for every row (except total rows)
                    row["Avg. Indigenous HH size (Province, 2021)"] = hh_size if indigenous_pop != "Total" else None

                    # estimate row is only for 2021 pop, all the other years populate with None
                    if metric == "Estimate":    
                        for year in PROJECTION_YEARS:
                            if year == "2021":
                                val = num_hhs[year][indigenous_pop]
                                row[year] = round(val, 0) if val is not None else None
                            else:
                                row[year] = None
                    
                    # if pop. projection row, populate the values for all years except 2021
                    elif metric == "Projection":
                        for year in PROJECTION_YEARS:
                            if year == "2021":
                                row[year] = None
                            else:
                                val = num_hhs[year][indigenous_pop]
                                row[year] = round(val, 0) if val is not None else None

                    # if % change row, calculate the % change for all rows but 2021
                    elif metric == "% Change from 2021":
                        for year in PROJECTION_YEARS:
                            if year == "2021": 
                                row[year] = None
                            else:
                                row[year] = growth_rate(num_hhs["2021"][indigenous_pop], num_hhs[year][indigenous_pop])
                    
                    rows.append(row)

        result = pd.DataFrame(rows)

        print("Table 11.1.2 is ready now...\n" + '=' * 60)
        return result

    def run_all(self) -> dict[str, pd.DataFrame]:
        "Runs all Section 11 methods and returns {name:df}"
        return {
            "11.1.1": self.table_11_1_1(),
            "11.1.2": self.table_11_1_2()
        }
    
if __name__ == '__main__':
    t = Section11DataPrep()
    df_11_1_1 = t.table_11_1_1()
    df_11_1_2 = t.table_11_1_2()