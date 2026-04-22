"""
Section 3 preparation and layout - Demographics.
"""
import pandas as pd
import numpy as np
from dash import dash_table, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from .data_loader import DataLoader
from .table_styles import (
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    get_special_row_styles,
    get_special_row_styles_3_1,
    style_cell_3_1,
    format_number,
    format_percent
)
from .text_content import (
    TABLE_3_1_TITLE, CHART_3_2_TITLE,
    TABLE_3_3_TITLE, TABLE_3_4_TITLE,
    TABLE_3_5_TITLE, TABLE_3_6_TITLE)
from helpers.config import CHART_COLORS


class Section3Prep:
    """Prepare and format Section 3 schemas."""

    def __init__(self):
        self.data_loader = DataLoader()

    def prepare_table_3_1_data(self, geocode: int) -> pd.DataFrame:

        YEAR_COLS = ['2006', '2011', '2016', '2021']

        # Determine geography level and resolve CD geocode for sections 3 & 4
        is_csd = len(str(geocode)) == 7
        cd_geocode = self.data_loader.get_region_geocode(geocode) if is_csd else geocode

        df_3_1_1 = self.data_loader.get_table('table_3_1_1_indigenous_pop', geocode)
        df_3_1_2 = self.data_loader.get_table('table_3_1_2_indigenous_age', geocode)
        df_3_1_3 = self.data_loader.get_table('table_3_1_3_indigenous_location', cd_geocode)
        df_3_1_4 = self.data_loader.get_table('table_3_1_4_indigenous_move', cd_geocode)


        def blank_row(label=''):
            return {'Indicator': label, **{y: '' for y in YEAR_COLS}}

        def get_values(filtered_df, label_col, label_val, pct_row=False):
            """Extract year values for a specific label row, with optional formatting."""
            row = filtered_df[filtered_df[label_col] == label_val]
            result = {}
            for year in YEAR_COLS:
                if row.empty or year not in row.columns:
                    result[year] = None
                    continue
                raw = row[year].iloc[0]
                if pd.isna(raw) or raw is None:
                    result[year] = None
                elif pct_row:
                    result[year] = format_percent(raw)
                else:
                    result[year] = format_number(raw)
            return result

        rows = []

        ##### Section 1: Indigenous Population (by CSD) #####
        label_col_1 = 'Indigenous Population (by CSD)'
        rows.append(blank_row('__geo_header__'))
        rows.append(blank_row(label_col_1))
        for pop_type in ['First Nations', 'Métis', 'Inuit', r'Multiple/Other Responses']:
            vals = get_values(df_3_1_1, label_col_1, pop_type)
            rows.append({'Indicator': pop_type, **vals})
        rows.append({'Indicator': 'TOTAL', **get_values(df_3_1_1, label_col_1, 'TOTAL')})
        rows.append(blank_row())

        ##### Section 2: Age Profile #####
        label_col_2 = 'Age Profile'
        for metric in ['Median Age (years)', '% Under 15 years old', '% 65 years or older']:
            is_pct = metric.startswith('%')
            vals = get_values(df_3_1_2, label_col_2, metric, pct_row=is_pct)
            rows.append({'Indicator': metric, **vals})
        rows.append(blank_row())

        ##### Section 3: Regional Indigenous Households (by CD) #####
        label_col_3 = 'Regional Indigenous Households (by CD)'
        rows.append(blank_row('__cd_header__'))
        rows.append(blank_row(label_col_3))
        for hh_type in ['On Reserve', 'Off Reserve']:
            vals = get_values(df_3_1_3, label_col_3, hh_type)
            rows.append({'Indicator': hh_type, **vals})
        rows.append({'Indicator': 'TOTAL', **get_values(df_3_1_3, label_col_3, 'TOTAL')})
        rows.append(blank_row())

        ##### Section 4: Indigenous-led HH moves (by CD) #####
        label_col_4 = 'Number of Indigenous-led HHs who have moved in last 5 years (by CD)...'
        rows.append(blank_row(label_col_4))
        for move_type in ['...to a Reserve from off-Reserve', '...off a Reserve']:
            vals = get_values(df_3_1_4, label_col_4, move_type)
            rows.append({'Indicator': move_type, **vals})

        return pd.DataFrame(rows, columns=['Indicator'] + YEAR_COLS)

    def create_table_3_1_layout(self, geocode: int):
        """
        Create Dash DataTable layout for Table 3.1 with 2-level column headers:
            Level 0 – geography name (merged across all year columns)
            Level 1 – census year

        Args:
            geocode: Geographic code

        Returns:
            Dash HTML Div with table
        """
        df = self.prepare_table_3_1_data(geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        is_csd = len(str(geocode)) == 7
        cd_geocode = self.data_loader.get_region_geocode(geocode) if is_csd else geocode
        cd_name = self.data_loader.get_geography_name(int(cd_geocode)) if is_csd else geo_name

        year_cols = ['2006', '2011', '2016', '2021']

        # Replace sentinels with display text for rendering
        df_display = df.copy()
        df_display['Indicator'] = df_display['Indicator'].replace({
            '__geo_header__': geo_name,
            '__cd_header__': cd_name,
        })

        # 2-level column definitions
        columns = [
            {"name": ["", ""], "id": "Indicator"}
        ] + [
            {"name": [geo_name, y], "id": y}
            for y in year_cols
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-3-1',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + get_special_row_styles_3_1(df)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Indicator'
            ),
            style_cell_conditional=style_cell_3_1(),
            **base_style
        )

        layout = html.Div([
            html.H4(TABLE_3_1_TITLE, className='table-title'),
            dbc.Button("Export", id="export-table-3-1", className="export-pdf"),
            table
        ], className='pg2-table-lgeo')

        return layout


if __name__ == "__main__":
    t = Section3Prep()
    t.prepare_table_3_1_data(5915022)