"""
Section 5 preparation and layout - Income.
"""
import pandas as pd
import numpy as np
from dash import dash_table, html, dcc
import plotly.graph_objects as go

from .data_loader import get_data_loader
from .table_styles import (
    blank_row,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    make_special_row_styles,
    make_style_cell,
    format_number,
    format_dollar,
    format_percent
)
from .text_content import SECTION_5_TITLE, TABLE_5_1_TITLE, TABLE_5_4_TITLE

from dashboard_helpers.config import (
    CHART_COLORS, PLOT_CONFIG, YEARS, YEARS_2016_2021,
    YEARS_MINUS_2011, COMMUNITIES)

from .export_helpers import with_export_btn


class Section5Prep:
    """Prepare and format Section 5 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_5_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 5.1: HART income & shelter cost of Indigenous Households."""
        df = self.data_loader.get_table('table_5_1_income_shelter_cost', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        
        value_cols = ['% of Total Indigenous HHs', 'Annual HH Income', 
                      'Affordable Shelter Cost (2020 CAD$)']

        table_df = df.set_index('Income Category')[value_cols].reset_index()

        table_df['% of Total Indigenous HHs'] = table_df['% of Total Indigenous HHs'].apply(format_percent)

        columns = [{"name": [geo_name, "Income Category"], "id": "Income Category"}] + [
            {"name": [geo_name, col], "id": col} for col in value_cols
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-5-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Income Category', total_labels={'Area Median Household Income'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Income Category'
            ),
            style_cell_conditional=make_style_cell('Income Category', value_cols, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H3(SECTION_5_TITLE, className='table-title'),
            html.H4(TABLE_5_1_TITLE, className='table-title'),
            with_export_btn(table, 'table-5-1'),
        ], className='pg2-table-lgeo')
    
    def create_table_5_4_layout(self, geocode: int):
        """Create Dash DataTable for Table 5.4: Median Household & Per Person Income (2016, 2021)."""
        df = self.data_loader.get_table('table_5_4_median_income', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        result = (df.set_index('Household/person identity')[YEARS_2016_2021]
                  .reset_index()
                  .rename(columns={'Household/person identity': 'Census Year'}))
        

        for col in YEARS_2016_2021:
            result[col] = result[col].apply(format_dollar)

        rows = [blank_row('Census Year', YEARS_2016_2021, 'Median Annual Household Income')]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            tenure = row['Census Year']
            if tenure == 'Non-Indigenous household' in str(tenure):
                rows.append(blank_row('Census Year'))
                rows.append(blank_row('Census Year', YEARS_2016_2021, 'Median Annual Per Person Income'))

        table_df = pd.DataFrame(rows, dtype=object)

        columns = [{"name": [geo_name, "Census Year"], "id": "Census Year"}] + [
            {"name": [geo_name, col], "id": col} for col in YEARS_2016_2021
        ]

        section_headers = {
            'Median Annual Household Income',
            'Median Annual Per Person Income'
        }

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-5-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Census Year', section_headers=section_headers)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Census Year'
            ),
            style_cell_conditional=make_style_cell('Census Year', YEARS_2016_2021, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_5_4_TITLE, className='table-title'),
            with_export_btn(table, 'table-5-4'),
        ], className='pg2-table-lgeo')
    

    def create_table_5_5_layout(self, geocode: int, show_both: bool = False):
        """Create Dash DataTable for Table 5.5: Households by Number of Household Maintainers (2016, 2021)."""
        df = self.data_loader.get_table('table_5_5_5_6_number_hh_maintainers', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        _LABEL_COL = 'Households by Number of Household Maintainers'
        _HH_TYPES = [('Indigenous HHs', 'indg'), ('Non-Indigenous HHs', 'non_indg')]

        formatted_df = [
            df[(df['Household Type'] == ht) & (df['Census Year'] == year)]
            [[_LABEL_COL, 'HHs', '% of Total']]
            .set_index(_LABEL_COL)
            .rename(columns={'HHs': f'{prefix}_{year}_hhs', '% of Total': f'{prefix}_{year}_pct'})
            for ht, prefix in _HH_TYPES
            for year in YEARS_2016_2021
        ]
        result = pd.concat(formatted_df, axis=1).reset_index()

        for _, prefix in _HH_TYPES:
            for year in YEARS_2016_2021:
                result[f'{prefix}_{year}_hhs'] = result[f'{prefix}_{year}_hhs'].apply(format_number)
                result[f'{prefix}_{year}_pct'] = result[f'{prefix}_{year}_pct'].apply(format_percent)

        indg_cols = [f'indg_{y}_{m}' for y in YEARS_2016_2021 for m in ('hhs', 'pct')]
        non_indg_cols = [f'non_indg_{y}_{m}' for y in YEARS_2016_2021 for m in ('hhs', 'pct')]
        all_val_cols = indg_cols + non_indg_cols

        rows = [blank_row(_LABEL_COL, all_val_cols, _LABEL_COL)]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            if row[_LABEL_COL] == 'TOTAL':
                rows.append(blank_row(_LABEL_COL, all_val_cols))

        df_display = pd.DataFrame(rows, dtype=object)

        # 4-level columns: [geo_name, HH type, year, metric]
        columns = [
            {"name": [geo_name, "Census Year", "", ""], "id": _LABEL_COL}
        ] + [
            {"name": [geo_name, ht, year, metric], "id": f"{prefix}_{year}_{suffix}"}
            for ht, prefix in _HH_TYPES
            for year in YEARS_2016_2021
            for metric, suffix in [("HHs", "hhs"), ("% of Total", "pct")]
        ]

        data_cols = [_LABEL_COL] + all_val_cols
        if not show_both:
            data_cols = [_LABEL_COL] + indg_cols
            columns = [c for c in columns if c['id'] in data_cols]
        df_display = df_display[data_cols]

        base_style = get_base_table_style()
        val_cols = [c for c in data_cols if c != _LABEL_COL]

        table = dash_table.DataTable(
            id='table-5-5',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL, geo_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=4
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-5-5'),
        ], className='pg2-table-lgeo')
