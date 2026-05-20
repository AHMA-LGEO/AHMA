from utils import (
    strip_map, 
    YEARS, 
    YEARS_MINUS_2011, 
    YEARS_2016_TO_2023, 
    YEARLY_INTERVALS_2016_TO_2023, 
    PIT_YEARS, 
    PROJECTION_YEARS,
    INDIGENOUS_COMMUNITIES,
    HH_TYPES)

#-------------------- Section 3 – Indigenous Population --------------------

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


#-------------------- Section 4 – Housing Tenure --------------------

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


#-------------------- Section 5 – Income --------------------

TABLE_5_1_COL_MAP = {
    'Total - Private Households by core housing need status  _  Households with household income 20% or under of area median household income (AMHI)_  Indigenous household': 'Very Low Income (20% or under of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 21% to 50% of AMHI_  Indigenous household': 'Low Income (21% or 50% of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 51% to 80% of AMHI_  Indigenous household': 'Moderate Income (51% or 80% of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 81% to 120% of AMHI_  Indigenous household': 'Median Income (81% to 120% of AMHI)',
    'Total - Private Households by core housing need status  _  Households with household income 121% and over of AMHI_  Indigenous household': 'High Income (121% and more of AMHI)'
    }


_T5_2_INCOME_BASE = {
    "Very Low Income": "Very Low Income (20% or under of AMHI)",
    "Low": "Low Income (21% to 50% of AMHI)",
    "Moderate": "Moderate Income (51% to 80% of AMHI)",
    "Median": "Median Income (81% to 120% of AMHI)",
    "High": "High Income (121% and more of AMHI)",
    # "Total": "Total"
}

_T5_2_INDIGENOUS_SUFFIX = {
    "2006": "_Aboriginal household",
    "2016": "_Aboriginal household",
    "2021": "_Indigenous household",
}

_T5_2_NON_INDIGENOUS_SUFFIX = {
    "2006": "_Non-Aboriginal household",
    "2016": "_Non-Aboriginal household",
    "2021": "_Non-Indigenous household",
}


_T5_2_VERY_LOW_BASE = {
    "2006": "Households with  income 20% or under of area median household income (AMHI)",
    "2016": "Households with  income 20% or under of area median household income (AMHI)",
    "2021": "Households with  income 20% or under of AMHI",
}

TABLE_5_2_COL_MAP = strip_map({
    income: {
        "Indigenous HHs": {
            year: (
                _T5_2_VERY_LOW_BASE[year] + _T5_2_INDIGENOUS_SUFFIX[year]
                if income == "Very Low Income"
                else TABLE_5_1_COL_MAP.get(
                    f"{_T5_2_INCOME_BASE}_{_T5_2_INDIGENOUS_SUFFIX[year]}",
                    f"{prefix}{_T5_2_INDIGENOUS_SUFFIX[year]}"
                )
                if income != "Area Median Household income (all HHs)"
                else f"AMHI ({int(year)-1}$)"
            )
            for year in _T5_2_INDIGENOUS_SUFFIX
        },
        "Non-Indigenous HHs": {
            year: (
                _T5_2_VERY_LOW_BASE[year] + _T5_2_NON_INDIGENOUS_SUFFIX[year]
                if income == "Very Low Income"
                else TABLE_5_1_COL_MAP.get(
                    f"{_T5_2_INCOME_BASE}_{_T5_2_NON_INDIGENOUS_SUFFIX[year]}",
                    f"{prefix}{_T5_2_NON_INDIGENOUS_SUFFIX[year]}"
                )
                if income != "Area Median Household income (all HHs)"
                else f"AMHI ({int(year)-1}$)"
            )
            for year in _T5_2_NON_INDIGENOUS_SUFFIX
        },
    }
    for income, prefix in {
        "Area Median Household income (all HHs)": "AMHI",
        "Very Low Income": None,
        "Low": "Households with income 21% to 50% of AMHI",
        "Moderate": "Households with income 51%  to 80% of AMHI",
        "Median": "Households with income 81% to 120% of AMHI",
        "High": "Households with income 121% or over of AMHI",
        # "Total": "Total - Household income ranges as proportion to AMHI",
    }.items()
})


_T5_3_COMMUNITY_SUFFIX = {
    "First Nations": "First Nations-led",
    "Métis":         "Metis-led",
    "Inuit":         "Inuit-led",
}

_T5_3_INCOME_MAP = {
    "Area Median Household income (all HHs)": None,
    "Very Low Income": None,
    "Low": "Households with income 21% to 50% of AMHI",
    "Moderate": "Households with income 51%  to 80% of AMHI",
    "Median": "Households with income 81% to 120% of AMHI",
    "High": "Households with income 121% or over of AMHI",
    # "Total": "Total - Household income ranges as proportion to AMHI",
}


def _get_suffix_5_3(year: str, comm: str) -> str:
    if year == "2006":
        return f"_{comm} HH"
    return f"_{comm}"


TABLE_5_3_COL_MAP = strip_map({
    income: {
        com: {
            year: (
                # AMHI row
                f"AMHI ({int(year)-1}$)"
                if income == "Area Median Household income (all HHs)"
                
                # Very Low Income special handling (INLINE)
                else (
                    (
                        "Households with  income 20% or under of area median household income (AMHI)"
                        if year in {"2006", "2016"}
                        else "Households with  income 20% or under of AMHI"
                    )
                    + _get_suffix_5_3(year, com_long_name)
                )
                if income == "Very Low Income"
                
                # all other income categories
                else (
                    f"{_T5_3_INCOME_MAP[income]}"
                    + _get_suffix_5_3(year, com_long_name)
                )
            )
            for year in YEARS_MINUS_2011
        }
        for com, com_long_name in _T5_3_COMMUNITY_SUFFIX.items()
    }
    for income in _T5_3_INCOME_MAP.keys()
})


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


#-------------------- Section 6 – Dwelling --------------------

_T6_BEDROOM_KEYS = {
    "No bedrooms (studio)": "No bedroom",
    "1 bedroom": "1 bedroom",
    "2 bedrooms": "2 bedrooms",
    "3 bedrooms": "3 bedrooms",
    "4 or more bedrooms": "4 or more bedrooms",
}

def _bedroom_label_6_1(display_name, year):
    """Handles No bedroom(s) singular/plural shift"""
    base = _T6_BEDROOM_KEYS[display_name]

    if display_name == "No bedrooms (studio)" and year in {"2016", "2021"}:
        return "No bedrooms"

    return base


# def _total_label(year):
#     if year == "2006":
#         return "Total - Number of bedrooms"
#     return "Total - Occupied private dwellings by number of bedrooms - 25% sample data"


def _build_bedroom_map_6_1_6_2(groups):
    rows = {}

    # for bedroom in [*_T6_BEDROOM_KEYS.keys(), "Total"]:
    for bedroom in [*_T6_BEDROOM_KEYS.keys()]:
        rows[bedroom] = {}

        for grp_name, suffix_map in groups.items():
            rows[bedroom][grp_name] = {}

            for year in YEARS_MINUS_2011:
                suffix = suffix_map[year]

                # if bedroom == "Total":
                #     col = f"{_total_label(year)}_{suffix}"
                # else:
                col = f"{_bedroom_label_6_1(bedroom, year)}_{suffix}"

                rows[bedroom][grp_name][year] = col

    return strip_map(rows)


TABLE_6_1_COL_MAP = _build_bedroom_map_6_1_6_2({
    "Indigenous HHs": {
        "2006": "Aboriginal household",
        "2016": "Aboriginal household",
        "2021": "Indigenous household",
    },
    "Non-Indigenous HHs": {
        "2006": "Non-Aboriginal household",
        "2016": "Non-Aboriginal household",
        "2021": "Non-Indigenous household",
    },
})


TABLE_6_2_COL_MAP = _build_bedroom_map_6_1_6_2({
    "First Nations": {
        "2006": "First Nations-led",
        "2016": "First Nations-led",
        "2021": "First Nations-led",
    },
    "Métis": {
        "2006": "Metis-led",
        "2016": "Metis-led",
        "2021": "Metis-led",
    },
    "Inuit": {
        "2006": "Inuit-led",
        "2016": "Inuit-led",
        "2021": "Inuit-led",
    },
})


_T6_PERIOD_BUCKETS = {
    "Before 1960": {
        "2006": ["1920 or before", "1921 to 1945", "1946 to 1960"],
        "2016": ["1920 or before", "1921 to 1945", "1946 to 1960"],
        "2021": ["1920 or before", "1921 to 1945", "1946 to 1960"],
    },
    "1960-1980": {
        "2006": ["1961 to 1970", "1971 to 1980"],
        "2016": ["1961 to 1970", "1971 to 1980"],
        "2021": ["1961 to 1970", "1971 to 1980"],
    },
    "1980-2000": {
        "2006": ["1981 to 1985", "1986 to 1990", "1991 to 1995", "1996 to 2000"],
        "2016": ["1981 to 1990", "1991 to 1995", "1996 to 2000"],
        "2021": ["1981 to 1990", "1991 to 1995", "1996 to 2000"],
    },
    "After 2000": {
        "2006": ["2001 to 2006"],
        "2016": ["2001 to 2005", "2006 to 2010", "2011 to 2016"],
        "2021": ["2001 to 2005", "2006 to 2010", "2011 to 2015", "2016 to 2021"],
    },
}


def _build_period_map_6_3_6_4(groups):
    rows = {}

    # for bucket in [* _T6_PERIOD_BUCKETS.keys(), "Total"]:
    for bucket in [* _T6_PERIOD_BUCKETS.keys()]:
        rows[bucket] = {}

        for grp_name, suffix_map in groups.items():
            rows[bucket][grp_name] = {}

            for year in YEARS_MINUS_2011:
                suffix = suffix_map[year]

                # if bucket == "Total":
                #     rows[bucket][grp_name][year] = (
                #         f"Total - Period of construction_{suffix}"
                #     )
                # else:
                rows[bucket][grp_name][year] = [
                    f"{label}_{suffix}"
                    for label in _T6_PERIOD_BUCKETS[bucket][year]
                ]

    return strip_map(rows)


TABLE_6_3_COL_MAP = _build_period_map_6_3_6_4({
    "Indigenous HHs": {
        "2006": "Aboriginal household",
        "2016": "Aboriginal household",
        "2021": "Indigenous household",
    },
    "Non-Indigenous HHs": {
        "2006": "Non-Aboriginal household",
        "2016": "Non-Aboriginal household",
        "2021": "Non-Indigenous household",
    },
})


TABLE_6_4_COL_MAP = _build_period_map_6_3_6_4({
    "First Nations": {
        "2006": "First Nations-led",
        "2016": "First Nations-led",
        "2021": "First Nations-led",
    },
    "Métis": {
        "2006": "Metis-led",
        "2016": "Metis-led",
        "2021": "Metis-led",
    },
    "Inuit": {
        "2006": "Inuit-led",
        "2016": "Inuit-led",
        "2021": "Inuit-led",
    },
})


_T6_STRUCTURE_LABELS = {
    "Single-detached house": {
        "2006": "Single-detached house",
        "2016": "Single-detached house",
        "2021": "Single-detached house",
    },
    "Semi-detatched": {
        "2006": "Semi-detached house",
        "2016": "Semi-detached house",
        "2021": "Semi-detached house",
    },
    "Row house": {
        "2006": "Row house",
        "2016": "Row house",
        "2021": "Row house",
    },
    "Apartment or flat in a duplex": {
        "2006": "Apartment, duplex",
        "2016": "Apartment or flat in a duplex",
        "2021": "Apartment or flat in a duplex",
    },
    "Apartment in building with fewer than 5 storeys": {
        "2006": "Apartment, building that has fewer than five storeys",
        "2016": "Apartment in a building that has fewer than five storeys",
        "2021": "Apartment in a building that has fewer than five storeys",
    },
    "Apartment in building with 5+ storeys": {
        "2006": "Apartment, building that has five or more storeys",
        "2016": "Apartment in a building that has five or more storeys",
        "2021": "Apartment in a building that has five or more storeys",
    },
    "Other single-attached house": {
        "2006": "Other single-attached house",
        "2016": "Other single-attached house",
        "2021": "Other single-attached house",
    },
    "Moveable dwelling": {
        "2006": "Movable dwelling",
        "2016": "Movable dwelling",
        "2021": "Movable dwelling",
    },
}


# def _structure_total_label_6_5(year, suffix):
#     if year == "2016":
#         return (
#             "Total - Occupied private dwellings by structural type "
#             f"of dwelling - 25% sample data_{suffix}"
#         )
#     return f"Total - Structural type of dwelling_{suffix}"


def _build_structure_map_6_5_6_6(groups):
    rows = {}

    # for structure in [*_T6_STRUCTURE_LABELS.keys(), "Total"]:
    for structure in [*_T6_STRUCTURE_LABELS.keys()]:
        rows[structure] = {}

        for grp_name, suffix_map in groups.items():
            rows[structure][grp_name] = {}

            for year in YEARS_MINUS_2011:
                suffix = suffix_map[year]

                # if structure == "Total":
                #     rows[structure][grp_name][year] = _structure_total_label(
                #         year, suffix
                #     )
                # else:
                label = _T6_STRUCTURE_LABELS[structure][year]
                rows[structure][grp_name][year] = f"{label}_{suffix}"

    return strip_map(rows)


TABLE_6_5_COL_MAP = _build_structure_map_6_5_6_6({
    "Indigenous HHs": {
        "2006": "Aboriginal household",
        "2016": "Total - Aboriginal household status",
        "2021": "Indigenous household",
    },
    "Non-Indigenous HHs": {
        "2006": "Non-Aboriginal household",
        "2016": "Non-Aboriginal household",
        "2021": "Non-Indigenous household",
    },
})


TABLE_6_6_COL_MAP = _build_structure_map_6_5_6_6({
    "First Nations": {
        "2006": "First Nations-led",
        "2016": "First Nations-led",
        "2021": "First Nations-led",
    },
    "Métis": {
        "2006": "Metis-led",
        "2016": "Metis-led",
        "2021": "Metis-led",
    },
    "Inuit": {
        "2006": "Inuit-led",
        "2016": "Inuit-led",
        "2021": "Inuit-led",
    },
})


#-------------------- Section 7 – Shelter Costs and Rental Market --------------------

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

TABLE_7_3_2_1_COL_MAP = strip_map({
    year: f"Avg_Rent_{year}" for year in YEARS_2016_TO_2023
})

TABLE_7_3_2_2_COL_MAP = strip_map({
    interval: {
        "year_1": f"Avg_Rent_{interval.split('-')[0]}",
        "year_2": f"Avg_Rent_{interval.split('-')[1]}"
    }
    for interval in YEARLY_INTERVALS_2016_TO_2023
})

TABLE_7_3_3_1_COL_MAP = strip_map({
    year: f"Vacancy_{year}" for year in YEARS_2016_TO_2023
})

TABLE_7_3_3_2_COL_MAP = strip_map({
    interval: {
        "year_1": f"Vacancy_{interval.split('-')[0]}",
        "year_2": f"Vacancy_{interval.split('-')[1]}"
    }
    for interval in YEARLY_INTERVALS_2016_TO_2023
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

#-------------------- Section 8 – Core Housing Need --------------------

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

_T8_3_8_4_CALC_COLS = ["Rate of CHN (%)", "% of HHs in CHN who rent", "Rate of Extreme CHN (%)", "% of HHs in Extreme CHN who rent"]

_T8_3_8_4_CALC_COL_PREFIXES = {
    "renters": {
        "examined": {
            "2006": "  Household examined for core housing need_  Renter",
            "2016": "  Household examined for core housing need_  Renter",
            "2021": "  Household examined for core housing need_  Renter"
        },
        "chn": {
            "2006": "In CHN or Extreme CHN_Renter",
            "2016": "_Renter",
            "2021": "In CHN or Extreme CHN_Renter"
        },
        "echn": {
            "2006": "    In extreme core housing need_  Renter",
            "2016": "    In extreme core housing need_  Renter",
            "2021": "    In extreme core housing need_  Renter"
        }
    },
    "total": {
        "examined": {
            "2006": "  Household examined for core housing need_Total – Housing tenure and presence of mortgage",
            "2016": "  Household examined for core housing need_Total - Tenure including presence of mortgage payments and subsidized housing",
            "2021": "  Household examined for core housing need_Total - Tenure including presence of mortgage payment and subsidized housing"
        },
        "chn": { 
            "2006": "In CHN or Extreme CHN_Total",
            "2016": "In CHN or Extreme CHN_Total",
            "2021": "In CHN or Extreme CHN_Total"
        },
        "echn": { 
            "2006": "    In extreme core housing need_Total – Housing tenure and presence of mortgage",
            "2016": "    In extreme core housing need_Total - Tenure including presence of mortgage payments and subsidized housing",
            "2021": "    In extreme core housing need_Total - Tenure including presence of mortgage payment and subsidized housing"
        }
    }
}

_T8_3_8_4_COL_MAP_PREFIXES = {
    "HHs in Core Housing Need"        : { 
        "2006": "In CHN or Extreme CHN_Total",
        "2016": "In CHN or Extreme CHN_Total",
        "2021": "In CHN or Extreme CHN_Total",
    },
    "Rate of CHN (%)"                 : None,
    "% of HHs in CHN who rent"        : None,
    "HHs in Extreme CHN"              : { 
        "2006": "    In extreme core housing need_Total – Housing tenure and presence of mortgage",
        "2016": "    In extreme core housing need_Total - Tenure including presence of mortgage payments and subsidized housing",
        "2021": "    In extreme core housing need_Total - Tenure including presence of mortgage payment and subsidized housing",
    },
    "Rate of Extreme CHN (%)"         : None,
    "% of HHs in Extreme CHN who rent": None
}

_T8_3_8_4_SUFFIXES = {
    "2006": {
        "Non-Indigenous HHs": "Non-Aboriginal HH",
        "Indigenous HHs": "Aboriginal HH",
        "First Nations": "First Nations-led",
        "Métis": "Metis-led",
        "Inuit": "Inuit-led"
    },
    "2016": {
        "Non-Indigenous HHs": "Non-Aboriginal household",
        "Indigenous HHs": "Aboriginal household",
        "First Nations": "First Nations-led",
        "Métis": "Metis-led",
        "Inuit": "Inuit-led"
    },
    "2021": {
        "Non-Indigenous HHs": "Non-Indigenous household",
        "Indigenous HHs": "Indigenous household",
        "First Nations": "First Nations-led",
        "Métis": "Metis-led",
        "Inuit": "Inuit-led"
    }
}

# column map to all the fields needed for calculations, but not necessarily direct output
TABLE_8_3_8_4_CALC_COL_MAP = strip_map({
    year: {
        hh_type: {
            tenure: {
                statistic: f"{prefix_map[year]}_{suffix}"
                for statistic, prefix_map in tenure_map.items()
            }
            for tenure, tenure_map in _T8_3_8_4_CALC_COL_PREFIXES.items()
        }
        for hh_type, suffix in hh_type_map.items()
    }
    for year, hh_type_map in _T8_3_8_4_SUFFIXES.items()
})

TABLE_8_3_COL_MAP = strip_map({
    statistic: {
        year: {
            hh_type: None if prefix_map is None else f"{prefix_map[year]}_{hh_type_map[hh_type]}"
            for hh_type in HH_TYPES
        }
        for year, hh_type_map in _T8_3_8_4_SUFFIXES.items()
    }
    for statistic, prefix_map in _T8_3_8_4_COL_MAP_PREFIXES.items()
})

TABLE_8_4_COL_MAP = strip_map({
    statistic: {
        year: {
            hh_type: None if prefix_map is None else f"{prefix_map[year]}_{hh_type_map[hh_type]}"
            for hh_type in INDIGENOUS_COMMUNITIES
        }
        for year, hh_type_map in _T8_3_8_4_SUFFIXES.items()
    }
    for statistic, prefix_map in _T8_3_8_4_COL_MAP_PREFIXES.items()
})

_T8_5_8_6_PREFIXES = {
    "chn": "    In core housing need, but Not in extreme core housing need",
    "echn": "    In extreme core housing need",
    "examined": "  Household examined for core housing need",
}

_T8_5_8_6_BASES = {
    "Youth-led (under 30)" : {
        "2006": "  29 years or less",
        "2016": "  29 years or less",
        "2021": "  29 years or less",
    },
    "Senior-led (65+)" : {
        "2006": "  65 years and over",
        "2016": "  65 years and over",
        "2021": "  65 years and over",
    },
    "Single-mother-led" : {
        "2006": "  With a lone parent that is a female",
        "2016": "  With a lone parent that is a female",
        "2021": "  With a one-parent that is a woman+",
    },
    "Single-father-led" : {
        "2006": "  With a lone parent that is a male",
        "2016": "  With a lone parent that is a male",
        "2021": "  With a one-parent that is a man+",
    },
    "HH with physical limitation" : {
        "2006": None,
        "2016": "  Household has at least one person who had at least one activity limitations reported for Q11a, Q11b, Q11c or Q11f or combinations of these health issues",
        "2021": "  Household has at least one person who had at least one activity limitations reported for Q18a, Q18b, Q18c or Q18f or combinations of these health issues",
    },
    "HH with cognitive limitation" : {
        "2006": None,
        "2016": "  Household has at least one person with activity limitations reported for Q11(d)",
        "2021": "  Household has at least one person with activity limitations reported for Q18d only",
    },
    "HH with mental or addictions limitations" : {
        "2006": None,
        "2016": "  Household has at least one person with activity limitations reported for Q11(e)",
        "2021": "  Household has at least one person with activity limitations reported for Q18e only",
    },
    "HH is gender diverse" : {
        "2006": None,
        "2016": None,
        "2021": "  HH is gender diverse (HH includes  a same-gender, transgender or non-binary couple or includes a transgender or non-binary person who are not in a census family)",
    },
}

_T8_5_8_6_SUFFIX_2006_2016 = {
    "Non-Indigenous HHs": "Non-Aboriginal household",
    "Indigenous HHs": "Aboriginal household",
    "First Nations": "First Nations-led",
    "Métis": "Metis-led",
    "Inuit": "Inuit-led"
}

_T8_5_8_6_SUFFIXES = {
    "2006": _T8_5_8_6_SUFFIX_2006_2016,
    "2016": _T8_5_8_6_SUFFIX_2006_2016,
    "2021": {
        "Non-Indigenous HHs": "Non-Indigenous household",
        "Indigenous HHs": "Indigenous household",
        "First Nations": "First Nations-led",
        "Métis": "Metis-led",
        "Inuit": "Inuit-led"
    }
}

TABLE_8_5_COL_MAP = strip_map({
    distinction: {
        year: {
            hh_type: {
                statistic: None if year_base_map[year] is None else f"{prefix}_{year_base_map[year]}_{hh_type_map[hh_type]}"
                for statistic, prefix in _T8_5_8_6_PREFIXES.items()
            }
            for hh_type in HH_TYPES
        }
        for year, hh_type_map in _T8_5_8_6_SUFFIXES.items()
    }
    for distinction, year_base_map in _T8_5_8_6_BASES.items()
})

TABLE_8_6_COL_MAP = strip_map({
    distinction: {
        year: {
            hh_type: {
                statistic: None if year_base_map[year] is None else f"{prefix}_{year_base_map[year]}_{hh_type_map[hh_type]}"
                for statistic, prefix in _T8_5_8_6_PREFIXES.items()
            }
            for hh_type in INDIGENOUS_COMMUNITIES
        }
        for year, hh_type_map in _T8_5_8_6_SUFFIXES.items()
    }
    for distinction, year_base_map in _T8_5_8_6_BASES.items()
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


#-------------------- Section 9 – Systemic Pathways and Indigenous Homelessness --------------------

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



def _pit_map(attrs: dict) -> dict:
    return {attr: {y: cols.get(y) for y in PIT_YEARS} for attr, cols in attrs.items()}


TABLE_9_3_COL_MAP = strip_map(_pit_map({
    "First Nations": {
        "2025": "2025_Indigenous_Indigenous distinction_First Nations",
    },
    "Métis": {
        "2025": "2025_Indigenous_Indigenous distinction_Métis",
    },
    "Inuit": {
        "2025": "2025_Indigenous_Indigenous distinction_Inuit",
    },
    "Other/Multiple Indigenous Communities": {
        "2025": "2025_Indigenous_Indigenous distinction_Other Indigenous ancestry / Unknown",
    },
    "Total number of Indigenous people who experienced homelessness": {
        "2021": "2021_All Respondents_Number of Indigenous individuals who experienced homelessness_(blank)",
        "2023": "2023_All Respondents_Number of Indigenous individuals who experienced homelessness_(blank)",
        "2025": "2025_All Respondents_Number of individuals who experienced homelessness _(blank)" # calculating indigenous number using this field * 2025_All Respondents_% of respondents identified as Indigenous_(blank)
    },
    "% of PEH who were Indigenous": {
        "2021": "2021_All Respondents_% of respondents identified as Indigenous_(blank)",
        "2023": "2023_All Respondents_% of respondents identified as Indigenous_(blank)",
        "2025": "2025_All Respondents_% of respondents identified as Indigenous_(blank)",
    },
    "All Respondents Sheltered": {
        "2021": "2021_All Respondents_Sheltered_% Sheltered",
        "2023": "2023_All Respondents_Sheltered_(blank)",
        "2025": "2025_All Respondents_Sheltered_(blank)",
    },
    "All Respondents Unsheltered": {
        "2021": "2021_All Respondents_Unsheltered_% Unsheltered",
        "2023": "2023_All Respondents_Unsheltered_(blank)",
        "2025": "2025_All Respondents_Unsheltered_(blank)",
    },
    "Length of time experiencing homelessness - 12+ months": {
        "2021": "2021_All Respondents_Length of homelessness situation_% One year or more",
        "2023": "2023_All Respondents_Length of homelessness situation_% One year or more",
        "2025": "2025_All Respondents_Length of homelessness situation_%One year or more",
    },
    "Length of time experiencing homelessness - 6-12 months": {
        "2021": "2021_All Respondents_Length of homelessness situation_% Six months to less than one year",
        "2023": "2023_All Respondents_Length of homelessness situation_% Six months to less than one year",
        "2025": "2025_All Respondents_Length of homelessness situation_%6-12 months",
    },
    "Length of time experiencing homelessness - <6 months": {
        "2021": "2021_All Respondents_Length of homelessness situation_% Under six months",
        "2023": "2023_All Respondents_Length of homelessness situation_% Under six months",
        "2025": "2025_All Respondents_Length of homelessness situation_%Under six months",
    },
    "Length of time experiencing homelessness - Other/Unknown": {
        "2021": "2021_All Respondents_Length of homelessness situation_% Other length / unknown",
        "2023": "2023_All Respondents_Length of homelessness situation_% Unknown / no asnwer",
        "2025": "2025_All Respondents_Length of homelessness situation_%Other/Unknown",
    },
    "Reason for housing loss - Not enough income %": {
        "2021": "2021_All Respondents_Reason for housing loss_% Not enough income",
        "2023": "2023_All Respondents_Reason for housing loss_% Not enough income",
        "2025": "2025_All Respondents_Reason for housing loss_Not enough income",
    },
    "Reason for housing loss - Substance use issue %": {
        "2021": "2021_All Respondents_Reason for housing loss_% Substance use issue",
        "2023": "2023_All Respondents_Reason for housing loss_% Substance use issue",
        "2025": "2025_All Respondents_Reason for housing loss_Substance use issue",
    },
    "Reason for housing loss - Conflict with landlord %": {
        "2021": "2021_All Respondents_Reason for housing loss_% Conflict with landlord",
        "2023": "2023_All Respondents_Reason for housing loss_% Landlord/tenant conflict",
        "2025": "2025_All Respondents_Reason for housing loss_Conflict with landlord",
    },
    "Reason for housing loss - Conflict with spouse/partner %": {
        "2021": "2021_All Respondents_Reason for housing loss_% Conflict with spouse/partner/family/other",
        "2023": "2023_All Respondents_Reason for housing loss_%Conflict with spouse/partner/parent/guardian",
        "2025": "2025_All Respondents_Reason for housing loss_Conflict with spouse/partner/parent/other",
    },
    "Reason for housing loss - Mental health issue %": {
        "2021": "2021_All Respondents_Reason for housing loss_% Mental health issue",
        "2023": "2023_All Respondents_Reason for housing loss_% Mental health issue",
        "2025": "2025_All Respondents_Reason for housing loss_Mental/physical health issue",
    },
    "Reason for housing loss - Other %": {
        "2021": "2021_All Respondents_Reason for housing loss_% Other",
        "2023": "2023_All Respondents_Reason for housing loss_% Other",
        "2025": "2025_All Respondents_Reason for housing loss_Other",
    },
    "% who identified eviction as cause of most recent housing loss": {
        "2025": "2025_All Respondents_%Eviction as cause of most recent housing loss_(blank)",
    },
    "% who experienced homelessness for the first time as a youth (Indigenous)": {
        "2025": "2025_Indigenous_Experienced homelessness for the first time as a youth_(blank)",
    },
    "% who experienced homelessness for the first time as a youth (Non-Indigenous)": {
        "2025": "2025_Non-Indigenous_Experienced homelessness for the first time as a youth_(blank)",
    },
    "% of youth who were in foster care (Indigenous)": {
        "2025": "2025_Indigenous_Foster care as a youth_(blank)",
    },
    "% of youth who were in foster care (Non-Indigenous)": {
        "2025": "2025_Non-Indigenous_Foster care as a youth_(blank)",
    },
    "% with acquired brain injury": {
        "2021": "2021_All Respondents_% Brain injury_(blank)",
        "2023": "2023_All Respondents_% Brain injury_(blank)",
        "2025": "2025_All Respondents_%Brain injury_(blank)",
    },
}))


#-------------------- Section 10 – Access to Services --------------------

_T10_1_TOTAL_COL = "Number of Indigenous people in selected geography (for reference)"
_T10_1_BUFFER_COLS = ["Pharmacies (within 3 km buffer)", "Pharmacies (within 5 km buffer)",
                      "Friendship Centres (within 10 km buffer)", "Friendship Centres (within 20 km buffer)"]
_T10_1_TRANSPORT_TYPES = ["Walking", "Transit", "Biking"]

TABLE_10_1_COL_MAP = strip_map({
    "Health Care": {
        "Walking": "Indigenous_Population_w__Walking_Access_to_Health_Care",
        "Transit": "Indigenous_Population_w__Transit_Access_to_Health_Care",
        "Biking": "Indigenous_Population_w__Cycling_Access_to_Health_Care"
    },
    "Recreation Centres": {
        "Walking": "Indigenous_Population_w__Walking_Access_to_Recreation",
        "Transit": "Indigenous_Population_w__Transit_Access_to_Recreation",
        "Biking": "Indigenous_Population_w__Cycling_Access_to_Recreation"
    },
    "Primary or Secondary Education": {
        "Walking": "Indigenous_Population_w__Walking_Access_to_Primary_or_Secondary",
        "Transit": "Indigenous_Population_w__Transit_Access_to_Primary_or_Secondary",
        "Biking": "Indigenous_Population_w__Cycling_Access_to_Primary_or_Secondary"
    },
    "Child Care": {
        "Walking": "Indigenous_Population_w__Walking_Access_to_Child_Care",
        "Transit": "Indigenous_Population_w__Transit_Access_to_Child_Care",
        "Biking": "Indigenous_Population_w__Cycling_Access_to_Child_Care"
    },
    "Pharmacies (within 3 km buffer)": "Indigenous_Pop_w_3k_Pharm_Acc",
    "Pharmacies (within 5 km buffer)": "Indigenous_Pop_w_5k_Pharm_Acc",
    "Friendship Centres (within 10 km buffer)": "Indigenous_Pop_w_10k_FC_Access",
    "Friendship Centres (within 20 km buffer)": "Indigenous_Pop_w_20k_FC_Access",
    "Number of Indigenous people in selected geography (for reference)": "Indigenous_Population"
})



#-------------------- Section 11 – Population and Household Growth --------------------

_T11_1_DISTINCTIONS = ["First Nations", "Métis", "Inuit", "Other Indigenous", "Total"]
_T11_1_1_PREFIXES = {
    pop: "Indigenous"
    for pop in _T11_1_DISTINCTIONS
}
_T11_1_1_PREFIXES["Full population for comparison"] = "Full"

_T11_1_1_SUFFIXES = {
    "First Nations": {year: " - FN" for year in PROJECTION_YEARS},
    "Métis": {year: " - Metis" for year in PROJECTION_YEARS},
    "Inuit": {year: " - Inuit" for year in PROJECTION_YEARS},
    "Other Indigenous": {"2021": " - Other Indigenous",
                         "2026": " - Other Indigenous",
                         "2031": " - Other Indigenous",
                         "2046": " - Other"},
    "Total": {year: " - All Indigenous" for year in PROJECTION_YEARS},
    "Full population for comparison": {year: "" for year in PROJECTION_YEARS}
}

TABLE_11_1_1_COL_MAP = strip_map({
    pop: {
        year: f"{_T11_1_1_PREFIXES[pop]} Pop in {year}{suffix_map[year]}"
        for year in PROJECTION_YEARS
    }
    for pop, suffix_map in _T11_1_1_SUFFIXES.items()
})

TABLE_11_1_2_COL_MAP = {
    pop: {
        col: name for col, name in col_map.items()
    }
    for pop, col_map in TABLE_11_1_1_COL_MAP.items()
}
TABLE_11_1_2_COL_MAP["First Nations"]["Avg. Indigenous HH size (Province, 2021)"] = "Average HH Size 2021_First Nations"
TABLE_11_1_2_COL_MAP["Métis"]["Avg. Indigenous HH size (Province, 2021)"] = "Average HH Size 2021_Metis"
TABLE_11_1_2_COL_MAP["Inuit"]["Avg. Indigenous HH size (Province, 2021)"] = "Average HH Size 2021_Inuit"
TABLE_11_1_2_COL_MAP["Other Indigenous"]["Avg. Indigenous HH size (Province, 2021)"] = "Average HH Size 2021_Indigenous"
TABLE_11_1_2_COL_MAP["Total"]["Avg. Indigenous HH size (Province, 2021)"] = None
TABLE_11_1_2_COL_MAP["Full population for comparison"]["Avg. Indigenous HH size (Province, 2021)"] = "Average HH Size 2021_non-Indigenous"