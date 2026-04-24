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


TABLE_3_5_COL_MAP = strip_map({
    "Youth-led (under 30)": {
        "2006": "  29 years or less_Aboriginal household",
        "2016": "  29 years or less_Aboriginal household",
        "2021": "  29 years or less_Indigenous household",
    },
    "Senior-led (65+)": {
        "2006": "  65 years and over_Aboriginal household",
        "2016": "  65 years and over_Aboriginal household",
        "2021": "  65 years and over_Indigenous household",
    },
    "Single-mother-led": {
        "2006": "  With a lone parent that is a female_Aboriginal household",
        "2016": "  With a lone parent that is a female_Aboriginal household",
        "2021": "  With a one-parent that is a woman+_Indigenous household",
    },
    "Single-father-led": {
        "2006": "  With a lone parent that is a male_Aboriginal household",
        "2016": "  With a lone parent that is a male_Aboriginal household",
        "2021": "  With a one-parent that is a man+_Indigenous household",
    },
    "HH with physical limitation": {
        "2006": None, # no data in 2006
        "2016": "  Household has at least one person who had at least one activity limitations reported for Q11a, Q11b, Q11c or Q11f or combinations of these health issues_Aboriginal household",
        "2021": "  Household has at least one person who had at least one activity limitations reported for Q18a, Q18b, Q18c or Q18f or combinations of these health issues_Indigenous household",
    },
    "HH with cognitive limitation": {
        "2006": None, # no data in 2006
        "2016": "  Household has at least one person with activity limitations reported for Q11(d)_Aboriginal household",
        "2021": "  Household has at least one person with activity limitations reported for Q18d only_Indigenous household",
    },
    "HH with mental or addictions limitation": {
        "2006": None, # no data in 2006
        "2016": "  Household has at least one person with activity limitations reported for Q11(e)_Aboriginal household",
        "2021": "  Household has at least one person with activity limitations reported for Q18e only_Indigenous household",
    },
    "HH is gender diverse": {
        "2006": None, # no data in 2006
        "2016": None, # no data in 2016
        "2021": "  HH is gender diverse (HH includes  a same-gender, transgender or non-binary couple or includes a transgender or non-binary person who are not in a census family)_Indigenous household",
    },
})


_T3_5_SOURCE_SUFFIX = {
    "2006": "Aboriginal household",
    "2016": "Aboriginal household",
    "2021": "Indigenous household",
}
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
                    src = _T3_5_SOURCE_SUFFIX[year]
                    tgt = suffixes[year]
                    result[metric][community][year] = col.replace(src, tgt) if src in col else None
    return result

TABLE_3_5_1_COL_MAP = _build_3_5_1_map()



_HH_SUFFIX = {
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

# No exact pattern for this, hence taking this out
_T4_1_DWELLING = {
    "Dwelling provided by local government or First Nation": {
        "2021": {"Non-Indigenous HHs": None},   # not available in 2021
    },
}

_T4_1_PCT_DIRECT = {
    "% of Owners with mortgage":          {"Indigenous HHs": "% of owner households with a mortgage_Indigenous"},
    "% of Owners without a mortgage":     {"Indigenous HHs": "% of owner households WITHOUT a mortgage_Indigenous"},
    "% of Renters in subsidized housing": {"Indigenous HHs": "% of tenant households in subsidized housing_Indigenous"},
    "% of Renters not in subsidized housing": {"Indigenous HHs": "% of tenant households NOT in subsidized housing_Indigenous"},
}

# Calc column labels – shared between table 4.1 (by HH type) and 4.2 (by community)
_CALC_LABELS = {
    "owner_with_mortgage":    "Owner - with mortgage",
    "owner_without_mortgage": "Owner - without mortgage",
    "renter_subsidized":      "Renter - subsidized housing",
    "renter_not_subsidized":  "Renter - not subsidized housing",
}

# Which calc keys are available per year, no subsidized data for 2006
_CALC_YEARS_4_1 = {
    "2006": ["owner_with_mortgage", "owner_without_mortgage"],
    "2016": list(_CALC_LABELS),
    "2021": list(_CALC_LABELS),
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
            dwelling = _T4_1_DWELLING.get(tenure, {}).get(year, {})
            result[tenure][year] = {
                hh_type: (
                    dwelling[hh_type] if hh_type in dwelling
                    else f"{year_prefix_map[year]}_{suffix}"
                )
                for hh_type, suffix in _HH_SUFFIX[year].items()
            }
    
    for field, direct_map in _T4_1_PCT_DIRECT.items():
        result[field] = {
            year: {
                hh_type: (direct_map.get(hh_type) if year == "2011" else None)
                for hh_type in _HH_SUFFIX[year]
            }
            for year in YEARS
        }
    return result


def _build_4_1_calc_cols():
    return {
        year: {
            hh_type: {key: f"{_CALC_LABELS[key]}_{suffix}" for key in keys}
            for hh_type, suffix in _HH_SUFFIX[year].items()
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
                key: f"{_CALC_LABELS[key]}_{comm_suffix}"
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


TABLE_8_1_COL_MAP = strip_map({
    "Affordability (Households paying >30% of income on shelter)": {
        "Number of households": {
            "2006": {
                "Indigenous HHs": "Below affordability threshold_Aboriginal household",
                "Non-Indigenous HHs": "Below affordability threshold_Non-Aboriginal household"
            },
            "2016": {
                "Indigenous HHs": "Below affordability: 30% or more of household income is spent on shelter costs_Aboriginal household",
                "Non-Indigenous HHs": "Below affordability: 30% or more of household income is spent on shelter costs_Non-Aboriginal household"
            },
            "2021": {
                "Indigenous HHs": "Below affordability standard (Spending 30% or more )_Indigenous household",
                "Non-Indigenous HHs": "Below affordability standard (Spending 30% or more )_Non-Indigenous household"
            }
        }
    },
    "Adequacy (Households living in dwellings needing Major Repairs)": {
        "Number of households": {
            "2006": {
                "Indigenous HHs": "Below adequacy: major repairs are needed_Aboriginal household",
                "Non-Indigenous HHs": "Below adequacy: major repairs are needed_Non-Aboriginal household"
            },
            "2016": {
                "Indigenous HHs": "Below adequacy: major repairs needed_Aboriginal household",
                "Non-Indigenous HHs": "Below adequacy: major repairs needed_Non-Aboriginal household"
            },
            "2021": {
                "Indigenous HHs": "Below adequacy standard (major repairs needed)_Indigenous household",
                "Non-Indigenous HHs": "Below adequacy standard (major repairs needed)_Non-Indigenous household"
            }
        }
    },
    "Suitability (Households living in overcrowded dwellings)": {
        "Number of households": {
            "2006": {
                "Indigenous HHs": "Below suitability (crowding) standard_Aboriginal household",
                "Non-Indigenous HHs": "Below suitability (crowding) standard_Non-Aboriginal household"
            },
            "2016": {
                "Indigenous HHs": "Below suitability: not suitable_Aboriginal household",
                "Non-Indigenous HHs": "Below suitability: not suitable_Non-Aboriginal household"
            },
            "2021": {
                "Indigenous HHs": "Below suitability: not suitable_Indigenous household",
                "Non-Indigenous HHs": "Below suitability: not suitable_Non-Indigenous household"
            }
        }
    },
    "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)": {
        "Number of households": {
            "2006": {
                "Indigenous HHs": "Below Multiple standards_Aboriginal household",
                "Non-Indigenous HHs": "Below Multiple standards_Non-Aboriginal household"
            },
            "2016": {
                "Indigenous HHs": "Below Multiple standards_Aboriginal household",
                "Non-Indigenous HHs": "Below Multiple standards_Non-Aboriginal household"
            },
            "2021": {
                "Indigenous HHs": "Below multiple standards_Indigenous household",
                "Non-Indigenous HHs": "Below multiple standards_Non-Indigenous household"
            }
        }
    },
    "Acceptable Housing (Affordable, Adequate, and Suitable)": {
        "Number of households": {
            "2006": {
                "Indigenous HHs": "Acceptable_Aboriginal household",
                "Non-Indigenous HHs": "Acceptable_Non-Aboriginal household"
            },
            "2016": {
                "Indigenous HHs": None,  # Calculate: Total - all below standards
                "Non-Indigenous HHs": None
            },
            "2021": {
                "Indigenous HHs": None,  # Calculate: Total - all below standards
                "Non-Indigenous HHs": None
            }
        }
    },
    "Total households (for reference)": {
        "Number of households": {
            "2006": {
                "Indigenous HHs": "Total - Housing indicators_Aboriginal household",
                "Non-Indigenous HHs": "Total - Housing indicators_Non-Aboriginal household"
            },
            "2016": {
                "Indigenous HHs": "Total - Housing indicators_Aboriginal household",
                "Non-Indigenous HHs": "Total - Housing indicators_Non-Aboriginal household"
            },
            "2021": {
                "Indigenous HHs": "Total - Housing indicators_Indigenous household",
                "Non-Indigenous HHs": "Total - Housing indicators_Non-Indigenous household"
            }
        }
    }
})


