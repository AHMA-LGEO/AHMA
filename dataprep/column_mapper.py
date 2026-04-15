from dataprep.utils import strip_map


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
        "2016": None, # no data in 2006
        "2021": "  HH is gender diverse (HH includes  a same-gender, transgender or non-binary couple or includes a transgender or non-binary person who are not in a census family)_Indigenous household",
    },
})

TABLE_4_1_COL_MAP = strip_map({
    "Owner": {
        "2006": {
            "Indigenous HHs": "Owners_Aboriginal household",
            "Non-Indigenous HHs": "Owners_Non-Aboriginal HH"
        },
        "2011": {
            "Indigenous HHs": "Owner_Indigenous"
        },
        "2016": {
            "Indigenous HHs": "Owner_Aboriginal household",
            "Non-Indigenous HHs": "Owner_Non-Aboriginal household"
        },
        "2021": {
            "Indigenous HHs": "Owner_Indigenous household",
            "Non-Indigenous HHs": "Owner_Non-Indigenous household"
        }
    },
    "Renter": {
        "2006": {
            "Indigenous HHs": "Renter_Aboriginal household",
            "Non-Indigenous HHs": "Renter_Non-Aboriginal HH"
        },
        "2011": {
            "Indigenous HHs": "Renter_Indigenous"
        },
        "2016": {
            "Indigenous HHs": "Renter_Aboriginal household",
            "Non-Indigenous HHs": "Renter_Non-Aboriginal household"
        },
        "2021": {
            "Indigenous HHs": "Renter_Indigenous household",
            "Non-Indigenous HHs": "Renter_Non-Indigenous household"
        }
    },
    "Dwelling provided by local government or First Nation": {
        "2006": {
            "Indigenous HHs": "Dwelling provided by the local government, First Nation or Indian band_Aboriginal household",
            "Non-Indigenous HHs": "Dwelling provided by the local government, First Nation or Indian band_Non-Aboriginal HH"
        },
        "2011": {
            "Indigenous HHs": "Band housing_Indigenous"
        },
        "2016": {
            "Indigenous HHs": "Dwelling provided by the local government, First Nation or Indian band_Aboriginal household",
            "Non-Indigenous HHs": "Dwelling provided by the local government, First Nation or Indian band_Non-Aboriginal household"
        },
        "2021": {
            "Indigenous HHs": "Dwelling provided by the local government, First Nation or Indian band_Indigenous household",
            "Non-Indigenous HHs": None  # Not available in 2021 for non-indigenous
        }
    },
    "TOTAL": {
        "2006": {
            "Indigenous HHs": "Total – Housing tenure and presence of mortgage_Aboriginal household",
            "Non-Indigenous HHs": "Total – Housing tenure and presence of mortgage_Non-Aboriginal HH"
        },
        "2011": {
            "Indigenous HHs": "Total number of private Aboriginal households by tenure_Indigenous"
        },
        "2016": {
            "Indigenous HHs": "Total - Tenure including presence of mortgage payments and subsidized housing_Aboriginal household",
            "Non-Indigenous HHs": "Total - Tenure including presence of mortgage payments and subsidized housing_Non-Aboriginal household"
        },
        "2021": {
            "Indigenous HHs": "Total - Tenure including presence of mortgage payment and subsidized housing_Indigenous household",
            "Non-Indigenous HHs": "Total - Tenure including presence of mortgage payment and subsidized housing_Non-Indigenous household"
        }
    },
    "% of Owners with mortgage": {
        "2006": {
            "Indigenous HHs": None,  # Calculate from with/without mortgage
            "Non-Indigenous HHs": None
        },
        "2011": {
            "Indigenous HHs": "% of owner households with a mortgage_Indigenous"
        },
        "2016": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        },
        "2021": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        }
    },
    "% of Owners without a mortgage": {
        "2006": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        },
        "2011": {
            "Indigenous HHs": "% of owner households WITHOUT a mortgage_Indigenous"
        },
        "2016": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        },
        "2021": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        }
    },
    "% of Renters in subsidized housing": {
        "2006": {
            "Indigenous HHs": None,  # Not available
            "Non-Indigenous HHs": None
        },
        "2011": {
            "Indigenous HHs": "% of tenant households in subsidized housing_Indigenous"
        },
        "2016": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        },
        "2021": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        }
    },
    "% of Renters not in subsidized housing": {
        "2006": {
            "Indigenous HHs": None,  # Not available
            "Non-Indigenous HHs": None
        },
        "2011": {
            "Indigenous HHs": "% of tenant households NOT in subsidized housing_Indigenous"
        },
        "2016": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        },
        "2021": {
            "Indigenous HHs": None,  # Calculate
            "Non-Indigenous HHs": None
        }
    }
})

# Columns needed for calculations
TABLE_4_1_CALC_COLS = strip_map({
    "2006": {
        "Indigenous HHs": {
            "owner_with_mortgage": "Owner - with mortgage_Aboriginal household",
            "owner_without_mortgage": "Owner - without mortgage_Aboriginal household"
        },
        "Non-Indigenous HHs": {
            "owner_with_mortgage": "Owner - with mortgage_Non-Aboriginal HH",
            "owner_without_mortgage": "Owner - without mortgage_Non-Aboriginal HH"
        }
    },
    "2016": {
        "Indigenous HHs": {
            "owner_with_mortgage": "Owner - with mortgage_Aboriginal household",
            "owner_without_mortgage": "Owner - without mortgage_Aboriginal household",
            "renter_subsidized": "Renter - subsidized housing_Aboriginal household",
            "renter_not_subsidized": "Renter - not subsidized housing_Aboriginal household"
        },
        "Non-Indigenous HHs": {
            "owner_with_mortgage": "Owner - with mortgage_Non-Aboriginal household",
            "owner_without_mortgage": "Owner - without mortgage_Non-Aboriginal household",
            "renter_subsidized": "Renter - subsidized housing_Non-Aboriginal household",
            "renter_not_subsidized": "Renter - not subsidized housing_Non-Aboriginal household"
        }
    },
    "2021": {
        "Indigenous HHs": {
            "owner_with_mortgage": "Owner - with mortgage_Indigenous household",
            "owner_without_mortgage": "Owner - without mortgage_Indigenous household",
            "renter_subsidized": "Renter - subsidized housing_Indigenous household",
            "renter_not_subsidized": "Renter - not subsidized housing_Indigenous household"
        },
        "Non-Indigenous HHs": {
            "owner_with_mortgage": "Owner - with mortgage_Non-Indigenous household",
            "owner_without_mortgage": "Owner - without mortgage_Non-Indigenous household",
            "renter_subsidized": "Renter - subsidized housing_Non-Indigenous household",
            "renter_not_subsidized": "Renter - not subsidized housing_Non-Indigenous household"
        }
    }
})


TABLE_4_2_COL_MAP = strip_map({
    "Owner": {
        "First Nations": "Owner_First Nations-led",
        "Métis": "Owner_Metis-led",
        "Inuit": "Owner_Inuit-led"
    },
    "Renter": {
        "First Nations": "Renter_First Nations-led",
        "Métis": "Renter_Metis-led",
        "Inuit": "Renter_Inuit-led"
    },
    "Dwelling provided by local government or First Nation": {
        "First Nations": "Dwelling provided by the local government, First Nation or Indian band_First Nations-led",
        "Métis": "Dwelling provided by the local government, First Nation or Indian band_Metis-led",
        "Inuit": "Dwelling provided by the local government, First Nation or Indian band_Inuit-led"
    }
})


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


