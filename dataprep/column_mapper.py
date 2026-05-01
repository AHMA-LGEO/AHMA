from utils import strip_map, YEARS, YEARS_MINUS_2011


TABLE_3_1_1_COL_MAP = strip_map({
    "First Nations": {
        "2006": "      North American Indian - single response",
        "2011": "    First Nations (North American Indian) single identity",
        "2016": "      First Nations (North American Indian)",
        "2021": "      First Nations (North American Indian)",
    },
    "Métis": {
        "2006": "      Métis - single response",
        "2011": "    Métis single identity",
        "2016": "      Métis",
        "2021": "      Métis",
    },
    "Inuit": {
        "2006": "      Inuit - single response",
        "2011": "    Inuk (Inuit) single identity",
        "2016": "      Inuk (Inuit)",
        "2021": "      Inuk (Inuit)",
    },
    "Multiple/Other Responses": {
        "2006": "      Multiple Aboriginal identity responses",
        "2011": "    Multiple Aboriginal identities",
        "2016": "    Multiple Aboriginal responses",
        "2021": "    Multiple Indigenous responses",
    },
    # TODO: add this item back if we want to use original total column and remove the calc total logic from 3.1.1 function
    # "TOTAL": {
    #     "2006": "   Total Aboriginal identity population",
    #     "2011": "  Aboriginal identity",
    #     "2016": "  Aboriginal identity",
    #     "2021": "  Indigenous identity",
    # },
})


TABLE_3_1_2_COL_MAP = strip_map({
    "Median Age": {
        "2006": "Median age of the Aboriginal identity population",
        "2011": "Median age of the population",
        "2016": "Median age of the Aboriginal identity population",
        "2021": "  Median age_Indigenous",
    },
    
    "under_15_direct": {
        "2016": "  0 to 14 years",
        "2021": "  0 to 14 years_Indigenous_Indigenous",
    },
    "under_15_bands": {
        "2006": ["   0 to 4 years", "   5 to 9 years", "   10 to 14 years"],
        "2011": ["  0 to 4 years", "  5 to 9 years", "  10 to 14 years"],
    },
    
    "over_65_direct": {
        "2016": "    65 years and over",
        "2021": "    65 years and over_Indigenous",
    },
    "over_65_bands": {
        "2006": ["   65 to 69 years", "   70 to 74 years", "   75 to 79 years",
                 "   80 to 84 years", "   85 years and over"],
        "2011": ["  65 to 69 years", "  70 to 74 years", "  75 to 79 years",
                 "  80 to 84 years", "  85 years and over"],
    },
    "total": {
            "2006": "Total Aboriginal identity population by age and sex groups - 20% sample data",
            "2011": "  Total Aboriginal identity population in private households by age groups",
            "2016": "  Total - Age groups",
            "2021": "  Total - Age groups_Indigenous_Indigenous",
        },
})

TABLE_3_1_3_COL_MAP = strip_map({
    "On Reserve": {
        "2006": "  On reserve_ Aboriginal household",
        "2016": "Total – Mobility status 5 years ago of the PHM_  On reserve_Aboriginal household",
        "2021": "Total – Mobility status 5 years ago of the PHM_  On reserve_  Indigenous household",
    },
    "Off Reserve": {
        "2006": "  Off reserve_ Aboriginal household",
        "2016": "Total – Mobility status 5 years ago of the PHM_  Off reserve_Aboriginal household",
        "2021": "Total – Mobility status 5 years ago of the PHM_  Off reserve_  Indigenous household",
    },
    "TOTAL": {
        "2006": "Total - Private households by area of residence _ Aboriginal household",
        "2016": "Total – Mobility status 5 years ago of the PHM_Total - Private households by area of residence of primary household maintainers_Aboriginal household",
        "2021": "Total – Mobility status 5 years ago of the PHM_Total - Residence on or off reserve_  Indigenous household",
    },
})

TABLE_3_1_4_COL_MAP = strip_map({
    "...to a Reserve from off-Reserve": {
        "2006": "Mover - lived off reserve 5 years ago _On reserve_Aboriginal household",
        "2016": "    Mover - lived off reserve 5 years ago (moved from off-reserve to another dwelling or CSD or country)_  On reserve_Aboriginal household",
        "2021": "    Mover - lived off reserve 5 years ago (moved from off-reserve to another dwelling or CSD or country)_  On reserve_  Indigenous household",
    },
    "...off a Reserve": {
        "2006": "Mover - lived on reserve 5 years ago_Off reserve_Aboriginal household",
        "2016": "    Mover - lived on reserve 5 years ago (moved from on-reserve to another dwelling or CSD or country)_  Off reserve_Aboriginal household",
        "2021": "    Mover - lived on reserve 5 years ago (moved from on-reserve to another dwelling or CSD or country)_  Off reserve_  Indigenous household",
    },
})

# Age bucket keys match the left-hand side of column names (e.g. "0 to 14 years_Non-indigenous")
TABLE_3_2_COL_MAP = {
    "0 to 14 years":     "0 - 14",
    "15 to 24 years":    "15 - 24",
    "25 to 34 years":    "25 - 34",
    "35 to 44 years":    "35 - 44",
    "45 to 54 years":    "45 - 54",
    "55 to 64 years":    "55 - 64",
    "65 years and over": "65+",
}

TABLE_3_4_COL_MAP = {
        '0 to 14 years': 'Under 15',
        '15 to 24 years': '15 - 24',
        '25 to 34 years': '25 - 34',
        '35 to 44 years': '35 - 44',
        '45 to 54 years': '45 - 54',
        '55 to 64 years': '55 - 64',
        '65 years and over': '65+',
        'Total - Age groups': 'Total'
    }


_T3_5_YEAR_SUFFIX = {
    "2006": "Aboriginal household",
    "2016": "Aboriginal household",
    "2021": "Indigenous household",
}

def _t3_5_col(prefix_2006_2016, prefix_2021=None, no_2006=False):
    """Build {year: col_name} for a TABLE_3_5 metric.
    no_2006=True when 2006 has no data for this metric."""

    prefix_2021 = prefix_2021 if prefix_2021 is not None else prefix_2006_2016
    return {
        "2006": None if no_2006 else f"{prefix_2006_2016}_{_T3_5_YEAR_SUFFIX['2006']}",
        "2016": f"{prefix_2006_2016}_{_T3_5_YEAR_SUFFIX['2016']}",
        "2021": f"{prefix_2021}_{_T3_5_YEAR_SUFFIX['2021']}",
    }

TABLE_3_5_COL_MAP = strip_map({
    "Youth-led (under 30)":    _t3_5_col("  29 years or less"),
    "Senior-led (65+)":        _t3_5_col("  65 years and over"),
    "Single-mother-led":       _t3_5_col("  With a lone parent that is a female",
                                          "  With a one-parent that is a woman+"),
    "Single-father-led":       _t3_5_col("  With a lone parent that is a male",
                                          "  With a one-parent that is a man+"),
    "HH with physical limitation": _t3_5_col(
        "  Household has at least one person who had at least one activity limitations reported for Q11a, Q11b, Q11c or Q11f or combinations of these health issues",
        "  Household has at least one person who had at least one activity limitations reported for Q18a, Q18b, Q18c or Q18f or combinations of these health issues",
        no_2006=True,
    ),
    "HH with cognitive limitation": _t3_5_col(
        "  Household has at least one person with activity limitations reported for Q11(d)",
        "  Household has at least one person with activity limitations reported for Q18d only",
        no_2006=True,
    ),
    "HH with mental or addictions limitation": _t3_5_col(
        "  Household has at least one person with activity limitations reported for Q11(e)",
        "  Household has at least one person with activity limitations reported for Q18e only",
        no_2006=True,
    ),
    "HH is gender diverse": {  # unique 2021 column name, hence kept explicit
        "2006": None,
        "2016": None,
        "2021": "  HH is gender diverse (HH includes  a same-gender, transgender or non-binary couple or includes a transgender or non-binary person who are not in a census family)_Indigenous household",
    },
})


_T3_5_COMMUNITY_SUFFIX = {
    "First Nations": {"2006": "First Nations-led", "2016": "First Nations-led", "2021": "First Nation-led"},
    "Métis":         {"2006": "Metis-led",          "2016": "Metis-led",          "2021": "Metis-led"},
    "Inuit":         {"2006": "Inuit-led",           "2016": "Inuit-led",          "2021": "Inuit-led"},
}

def _build_3_5_1_map():
    result = {}
    for metric, year_map in TABLE_3_5_COL_MAP.items():
        result[metric] = {}
        for community, suffixes in _T3_5_COMMUNITY_SUFFIX.items():
            result[metric][community] = {}
            for year, col in year_map.items():
                if col is None:
                    result[metric][community][year] = None
                else:
                    src = _T3_5_YEAR_SUFFIX[year]
                    tgt = suffixes[year]
                    result[metric][community][year] = col.replace(src, tgt) if src in col else None
    return result

TABLE_3_5_1_COL_MAP = _build_3_5_1_map()



_HH_SUFFIX_4_1_4_2 = {
    "2006": {"Indigenous HHs": "Aboriginal household",  "Non-Indigenous HHs": "Non-Aboriginal HH"},
    "2011": {"Indigenous HHs": "Indigenous"},
    "2016": {"Indigenous HHs": "Aboriginal household",  "Non-Indigenous HHs": "Non-Aboriginal household"},
    "2021": {"Indigenous HHs": "Indigenous household",  "Non-Indigenous HHs": "Non-Indigenous household"},
}

_T4_1_TENURE_PREFIX = {
    "Owner": {
        "2006": "Owners",
        "2011": "Owner", "2016": "Owner", "2021": "Owner",
    },
    "Renter": {
        "2006": "Renter", "2011": "Renter", "2016": "Renter", "2021": "Renter",
    },
    "Dwelling provided by local government or First Nation": {
        "2006": "Dwelling provided by the local government, First Nation or Indian band",
        "2011": "Band housing",   # different label in 2011
        "2016": "Dwelling provided by the local government, First Nation or Indian band",
        "2021": "Dwelling provided by the local government, First Nation or Indian band",
    },
    "TOTAL": {
        "2006": "Total – Housing tenure and presence of mortgage",
        "2011": "Total number of private Aboriginal households by tenure",
        "2016": "Total - Tenure including presence of mortgage payments and subsidized housing",
        "2021": "Total - Tenure including presence of mortgage payment and subsidized housing",
    },
}

_T4_1_PCT_DIRECT = {
    "% of Owners with mortgage":          {"Indigenous HHs": "% of owner households with a mortgage_Indigenous"},
    "% of Owners without a mortgage":     {"Indigenous HHs": "% of owner households WITHOUT a mortgage_Indigenous"},
    "% of Renters in subsidized housing": {"Indigenous HHs": "% of tenant households in subsidized housing_Indigenous"},
    "% of Renters not in subsidized housing": {"Indigenous HHs": "% of tenant households NOT in subsidized housing_Indigenous"},
}

# Calc column labels – shared between table 4.1 (by HH type) and 4.2 (by community)
_CALC_LABELS_4_1_4_2 = {
    "owner_with_mortgage":    "Owner - with mortgage",
    "owner_without_mortgage": "Owner - without mortgage",
    "renter_subsidized":      "Renter - subsidized housing",
    "renter_not_subsidized":  "Renter - not subsidized housing",
}

# Which calc keys are available per year, no subsidized data for 2006
_CALC_YEARS_4_1 = {
    "2006": ["owner_with_mortgage", "owner_without_mortgage"],
    "2016": list(_CALC_LABELS_4_1_4_2),
    "2021": list(_CALC_LABELS_4_1_4_2),
}

# Community suffixes for table 4.2 (same across 2006, 2016, 2021)
_T4_2_COMMUNITY_SUFFIX = {
    "First Nations": "First Nations-led",
    "Métis":         "Metis-led",
    "Inuit":         "Inuit-led",
}

def _build_4_1_col_map():
    result = {}
    for tenure, year_prefix_map in _T4_1_TENURE_PREFIX.items():
        result[tenure] = {}
        for year in YEARS:
            result[tenure][year] = {
                hh_type: f"{year_prefix_map[year]}_{suffix}"
                for hh_type, suffix in _HH_SUFFIX_4_1_4_2[year].items()
            }
    
    for field, direct_map in _T4_1_PCT_DIRECT.items():
        result[field] = {
            year: {
                hh_type: (direct_map.get(hh_type) if year == "2011" else None)
                for hh_type in _HH_SUFFIX_4_1_4_2[year]
            }
            for year in YEARS
        }
    return result


def _build_4_1_calc_cols():
    return {
        year: {
            hh_type: {key: f"{_CALC_LABELS_4_1_4_2[key]}_{suffix}" for key in keys}
            for hh_type, suffix in _HH_SUFFIX_4_1_4_2[year].items()
        }
        for year, keys in _CALC_YEARS_4_1.items()
    }


def _build_4_2_col_map():
    result = {}
    
    for tenure, year_prefix_map in _T4_1_TENURE_PREFIX.items():
        result[tenure] = {
            year: {
                community: f"{year_prefix_map[year]}_{comm_suffix}"
                for community, comm_suffix in _T4_2_COMMUNITY_SUFFIX.items()
            }
            for year in YEARS_MINUS_2011
        }
    
    for field in _T4_1_PCT_DIRECT:
        result[field] = {
            year: {community: None for community in _T4_2_COMMUNITY_SUFFIX}
            for year in YEARS_MINUS_2011
        }
    return result


def _build_4_2_calc_cols():
    return {
        year: {
            community: {
                key: f"{_CALC_LABELS_4_1_4_2[key]}_{comm_suffix}"
                for key in keys
            }
            for community, comm_suffix in _T4_2_COMMUNITY_SUFFIX.items()
        }
        for year, keys in _CALC_YEARS_4_1.items()
        if year in YEARS_MINUS_2011
    }


TABLE_4_1_COL_MAP   = strip_map(_build_4_1_col_map())
TABLE_4_1_CALC_COLS = strip_map(_build_4_1_calc_cols())
TABLE_4_2_COL_MAP   = strip_map(_build_4_2_col_map())
TABLE_4_2_CALC_COLS = strip_map(_build_4_2_calc_cols())


# Size-row column prefixes, shared by both 4.3/4.4 and 4.3.1
_T4_3_SIZE_PREFIX = {
    "1 pp":   {"2006": "  1 person",             "2016": "1 person",          "2021": "1 person"},
    "2 pp":   {"2006": "  2 persons",            "2016": "2 persons",         "2021": "2 persons"},
    "3 pp":   {"2006": "  3 persons",            "2016": "3 persons",         "2021": "3 persons"},
    "4 pp":   {"2006": "  4 persons",            "2016": "4 persons",         "2021": "4 persons"},
    "5+ pp": {"2006": "  5 or more",            "2016": "5 or more persons", "2021": "5 or more persons"},
    "Total": {"2006": "Total - Household size", "2016": "Total - Household size", "2021": "Total - Household size"},
}
_T4_3_AVG_PREFIX = {
    "2006": "Average number of persons",
    "2016": "Average household size",
    "2021": "Average Household size",
}

_T4_3_1_COMMUNITY_SUFFIX = {
    "First Nations-led Households by Size (number of people)": {
        "2006": "First Nations led", "2016": "First Nations-led", "2021": "First Nations-led"
    },
    "Métis-led Households by Size (number of people)": {
        "2006": "Metis led", "2016": "Metis-led", "2021": "Metis-led"
    },
    "Inuit-led Households by Size (number of people)": {
        "2006": "Inuit led", "2016": "Inuit-led", "2021": "Inuit-led"
    },
}


_HH_SUFFIX_4_3 = _HH_SUFFIX_4_1_4_2.copy()
_HH_SUFFIX_4_3["2006"]["Indigenous HHs"] = "  Aboriginal household"

_T4_3_4_4_HH_SUFFIX = {
    hh: {year: _HH_SUFFIX_4_1_4_2[year][hh] for year in YEARS_MINUS_2011}
    for hh in ("Indigenous HHs", "Non-Indigenous HHs")
}


def _build_size_map_4_3_4_4(size_prefixes: dict, group_suffix_map: dict) -> dict:
    """Build {size: {group: {year: col_name}}} for household-size tables."""
    return {
        size: {
            group: {year: f"{size_prefix[year]}_{suffix[year]}" for year in YEARS_MINUS_2011}
            for group, suffix in group_suffix_map.items()
        }
        for size, size_prefix in size_prefixes.items()
    }


TABLE_4_3_4_4_COL_MAP = strip_map(_build_size_map_4_3_4_4(
    {**_T4_3_SIZE_PREFIX, "Average Household Size": _T4_3_AVG_PREFIX},
    _T4_3_4_4_HH_SUFFIX,
))

TABLE_4_3_1_COL_MAP = strip_map(_build_size_map_4_3_4_4(
    {**_T4_3_SIZE_PREFIX, "Average": _T4_3_AVG_PREFIX},
    _T4_3_1_COMMUNITY_SUFFIX,
))


TABLE_5_1_COL_MAP = {
    'Total - Private Households by core housing need status  _  Households with household income 20% or under of area median household income (AMHI)_  Indigenous household': 'Very Low Income (20% or under of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 21% to 50% of AMHI_  Indigenous household': 'Low Income (21% or 50% of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 51% to 80% of AMHI_  Indigenous household': 'Moderate Income (51% or 80% of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 81% to 120% of AMHI_  Indigenous household': 'Median Income (81% to 120% of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 121% and over of AMHI_  Indigenous household': 'High Income (121% and more of AMHI)'
    }


TABLE_5_4_COL_MAP = strip_map({
    'Median Annual Household Income': {
        '2016': {
            'Indigenous household': '  Median total income of households in 2015 ($)_Aboriginal household',
            'Non-Indigenous household': '  Median total income of households in 2015 ($)_Non-Aboriginal household'
        },
        '2021': {
            'Indigenous household': '  Median total income of households in 2020_Indigenous household',
            'Non-Indigenous household': '  Median total income of households in 2020_Non-Indigenous household'
        }
    },
    'Median Annual Per Person Income': {
        '2016': {
            'Indigenous person': '    Median total income in 2015 per person_Aboriginal household',
            'Non-Indigenous person': '    Median total income in 2015 per person_Non-Aboriginal household'
        },
        '2021': {
            'Indigenous person': '    Median total income in 2020 per person_Indigenous identity',
            'Non-Indigenous person': '    Median total income in 2020 per person_Non-Indigenous identity'
        }
    }
})

_T5_5_5_6_HH_SUFFIX = {
    "2016": {"Indigenous HHs": " Aboriginal household", "Non-Indigenous HHs": "Non-Aboriginal household"},
    "2021": {"Indigenous HHs": "Indigenous household",  "Non-Indigenous HHs": "Non-Indigenous household"},
}

_T5_5_5_6_MAINTAINER_PREFIX = {
    '1 maintainer': {
        '2016': '  1 household maintainer',
        '2021': '  One-maintainer household'
    },
    '2 maintainers': {
        '2016': '  2 household maintainers',
        '2021': '  Two-maintainer household'
    },
    '3+ maintainers': {
        '2016': '  3 or more household maintainers',
        '2021': '  Three-or-more-maintainer household'
    }
}

TABLE_5_5_5_6_COL_MAP = strip_map({
    maintainers: {
        year: {
            hh: f"{year_map[year]}_{suffix}" for hh, suffix in suffixes.items()
        }
        for year, suffixes in _T5_5_5_6_HH_SUFFIX.items()
    }
    for maintainers, year_map in _T5_5_5_6_MAINTAINER_PREFIX.items()
})
TABLE_5_5_5_6_COL_MAP['TOTAL'] = None


_T7_HH_SUFFIX = {
    "2016": {"Indigenous HHs": " Aboriginal household", "Non-Indigenous HHs": "Non-Aboriginal household"},
    "2021": {"Indigenous HHs": "Indigenous household",  "Non-Indigenous HHs": "Non-Indigenous household"},
}
_T7_DWELLING_PREFIX = {
    "Owned dwellings":  "Median monthly shelter costs for owned dwellings ($)",
    "Rented dwellings": "Median monthly shelter costs for rented dwellings ($)",
}

TABLE_7_1_7_2_COL_MAP = strip_map({
    tenure: {
        year: {hh: f"{prefix}_{suffix}" for hh, suffix in suffixes.items()}
        for year, suffixes in _T7_HH_SUFFIX.items()
    }
    for tenure, prefix in _T7_DWELLING_PREFIX.items()
})


_T8_1_HH_SUFFIX = {
    "2006": {"Indigenous HHs": "Aboriginal household",  "Non-Indigenous HHs": "Non-Aboriginal household"},
    "2016": {"Indigenous HHs": "Aboriginal household",  "Non-Indigenous HHs": "Non-Aboriginal household"},
    "2021": {"Indigenous HHs": "Indigenous household",  "Non-Indigenous HHs": "Non-Indigenous household"},
}


_T8_1_INDICATOR_PREFIX = {
    "Affordability (Households paying >30% of income on shelter)": {
        "2006": "Below affordability threshold",
        "2016": "Below affordability: 30% or more of household income is spent on shelter costs",
        "2021": "Below affordability standard (Spending 30% or more )",
    },
    "Adequacy (Households living in dwellings needing Major Repairs)": {
        "2006": "Below adequacy: major repairs are needed",
        "2016": "Below adequacy: major repairs needed",
        "2021": "Below adequacy standard (major repairs needed)",
    },
    "Suitability (Households living in overcrowded dwellings)": {
        "2006": "Below suitability (crowding) standard",
        "2016": "Below suitability: not suitable",
        "2021": "Below suitability: not suitable",
    },
    "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)": {
        "2006": "Below Multiple standards",
        "2016": "Below Multiple standards",
        "2021": "Below multiple standards",
    },
    "Acceptable Housing (Affordable, Adequate, and Suitable)": {
        "2006": "Acceptable",
        "2016": None,  # Calculate: Total - all below standards
        "2021": None,
    },
    "Total households (for reference)": {
        "2006": "Total - Housing indicators",
        "2016": "Total - Housing indicators",
        "2021": "Total - Housing indicators",
    },
}

TABLE_8_1_COL_MAP = strip_map({
    indicator: {
        "Number of households": {
            year: {
                hh: f"{prefix}_{suffix}" if prefix else None
                for hh, suffix in _T8_1_HH_SUFFIX[year].items()
            }
            for year, prefix in year_map.items()
        }
    }
    for indicator, year_map in _T8_1_INDICATOR_PREFIX.items()
})


_T8_7_INCOME = {
    "Very Low Income": "20% or under of area median household income (AMHI)",
    "Low":             "21% to 50% of AMHI",
    "Moderate":        "51% to 80% of AMHI",
    "Median":          "81% to 120% of AMHI",
    "High":            "121% and over of AMHI",
}
_T8_7_HH_SIZE = {
    "1 pp":  "  1 person HH",
    "2 pp":  "  2 persons HH",
    "3 pp":  "  3 persons HH",
    "4 pp":  "  4 persons HH",
    "5+ pp": "  5 or more persons HH",
}
_T8_7_BASE = "Households in core housing need status_  Households with household income"

TABLE_8_7_COL_MAP = strip_map({
    hh_size: {
        income: f"{_T8_7_BASE} {bracket}_{size}_  Indigenous household"
        for income, bracket in _T8_7_INCOME.items()
    }
    for hh_size, size in _T8_7_HH_SIZE.items()
})


_T9_FY_YEARS  = [f"FY{i:02d}" for i in range(9, 25)]   # FY09 … FY24
_T9_AGE_GROUPS = ["Under 30", "30-49", "50+"]

def _build_9_1_map(prefix: str) -> dict:
    return strip_map({
        fy: {age: f"{prefix}_{fy}_{age}" for age in _T9_AGE_GROUPS}
        for fy in _T9_FY_YEARS
    })

TABLE_9_1_COL_MAP   = _build_9_1_map("Indigenous")
TABLE_9_1_1_COL_MAP = _build_9_1_map("All persons")

TABLE_9_2_COL_MAP = strip_map({
    "Children Who Exited Care due to Transitioning into Adulthood":{
        "Indigenous": "Exited Care_Indigenous",
        "Total Population": "Exited Care_Total"
    },
    "Children Who Exited from their Youth Agreement (YA) due to Transitioning into Adulthood":{
        "Indigenous": "Exited from their Youth Agreement_Indigenous",
        "Total Population": "Exited from their Youth Agreement_Total"
    },
})