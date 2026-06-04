"""
Section 11 preparation and layout - Population and household growth.
"""
import pandas as pd
import numpy as np
from dash import dash_table, html, dcc
import plotly.graph_objects as go

from .data_loader import get_data_loader
from .table_styles import (
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    make_special_row_styles,
    make_style_cell,
    format_number,
    format_percent
)
from .text_content import SECTION_11_TITLE, TABLE_11_1_TITLE

from dashboard_helpers.config import TABLE_FONT, TABLE_COLORS

from .export_helpers import with_export_btn

SECTION_11_YEARS = ['2021', '2026', '2031', '2046']

class Section11Prep:
    """Prepare and format Section 11 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_11_1_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 11.1.1: Projected Population of Indigenous People."""
        
        df = self.data_loader.get_table('table_11_1_1_projected_pop', geocode, check_columns=SECTION_11_YEARS)

        if df.empty:
            return html.Div([
                html.H4(SECTION_11_TITLE, className='table-title'),
                html.H5(TABLE_11_1_TITLE, className='table-title'),
                html.Div(
                "No data for projected population of indigenous population.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = 'Population Count'
        metrics = ['Estimate', 'Projection', '% Change from 2021']
        # communities = [comm + "-led Households by Size (number of people)"  for comm in COMMUNITIES]

        metrics_df = []
        for metric in metrics:
            metric_df = (
                df[df['Metric'] == metric]
                .set_index(_LABEL_COL)[SECTION_11_YEARS]
                .rename(columns={y: f'{y}_{metric[0]}' for y in SECTION_11_YEARS})
            )
            metrics_df.append(metric_df)

        table_df = pd.concat(metrics_df, axis=1).reset_index()

        # Column order: year, community (2021_E, 2036_P, 2036_%, 2041_P, ...)
        val_cols = (
            ['2021_E'] +
            [
                col
                for y in SECTION_11_YEARS[1:]
                for col in (f'{y}_P', f'{y}_%')
            ]
        )

        table_df = table_df[[_LABEL_COL] + val_cols]

        # print(table_df, val_cols)

        for col in val_cols:
            if '%' in col:
                table_df[col] = table_df[col].map(format_percent)
            else:
                table_df[col] = table_df[col].map(format_number)

        # print(table_df, val_cols)

        # 3-level columns: [geo_name, year, community]
        columns = (
            [{"name": [geo_name, "Census Year", "Household Count"], "id": _LABEL_COL}]
            +
            [{"name": [geo_name, "2021", "Estimate"], "id": "2021_E"}]
            +
            [
                {
                    "name": [geo_name, y, metric],
                    "id": f"{y}_{metric[0]}"
                }
                for y in SECTION_11_YEARS[1:]
                for metric in ["Projection", "% Change from 2021"]
            ]
        )

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-11-1-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, _LABEL_COL, 
                                          geo_headers={_LABEL_COL}, total_labels={'Total', 'Full population for comparison'})
            ),
            style_header_conditional=(generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=3,
                left_align_cells=[{'column_id':_LABEL_COL, 'header_index': 1},
                                  {'column_id':_LABEL_COL, 'header_index': 2}]
                ) + [
                {
                    'if': {'column_id': _LABEL_COL, 'header_index': 1},
                    'borderBottom': f"1px solid {TABLE_COLORS['border']}",
                }
            ]
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='20%'),
            **base_style
        )

        return html.Div([
            html.H4(SECTION_11_TITLE, className='table-title'),
            html.H5(TABLE_11_1_TITLE, className='table-title'),
            with_export_btn(table, 'table-11-1-1'),
        ], className='pg2-table-lgeo')
    

    def create_table_11_1_2_layout(self, geocode: int):
        """Create Dash DataTable for Table 11.1.2: Projected Population of Indigenous Households."""
        df = self.data_loader.get_table('table_11_1_2_projected_hh', geocode, check_columns=SECTION_11_YEARS)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for projected households for indigenous population.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = 'Household Count'
        metrics = ['Estimate', 'Projection', '% Change from 2021']
        years_plus_avg = ['Avg. Indigenous HH size (Province, 2021)'] + SECTION_11_YEARS

        metrics_df = []
        for metric in metrics:
            metric_df = (
                df[df['Metric'] == metric]
                .set_index(_LABEL_COL)[years_plus_avg]
                .rename(columns={
                    'Avg. Indigenous HH size (Province, 2021)': 'Avg',
                    **{y: f'{y}_{metric[0]}' for y in SECTION_11_YEARS}
                    })
            )

            # keep Avg only once
            if metric != 'Estimate':
                metric_df = metric_df.drop(columns='Avg', errors='ignore')

            metrics_df.append(metric_df)

        table_df = pd.concat(metrics_df, axis=1).reset_index()

        # Column order: year, community (2021_E, 2036_P, 2036_%, 2041_P, ...)
        val_cols = (
            ['Avg'] + ['2021_E'] +
            [
                col
                for y in SECTION_11_YEARS[1:]
                for col in (f'{y}_P', f'{y}_%')
            ]
        )

        table_df = table_df[[_LABEL_COL] + val_cols]
        # print(table_df, val_cols)

        for col in val_cols:
            if '%' in col:
                table_df[col] = table_df[col].map(format_percent)
            elif 'Avg' in col:
                table_df[col] = table_df[col].map(lambda x: format_number(x, decimals=1))
            else:
                table_df[col] = table_df[col].map(format_number)

        # print(table_df, val_cols)

        # 3-level columns: [geo_name, year, community]
        columns = (
            [{"name": [geo_name, "Census Year", "Population Count"], "id": _LABEL_COL}]

            # Avg column (blank top/year header)
            + [{
                "name": [geo_name, "Census Year", "Avg. Indigenous HH size (Province, 2021)"],
                "id": "Avg"
            }]

            +
            [{"name": [geo_name, "2021", "Estimate"], "id": "2021_E"}]
            +
            [
                {
                    "name": [geo_name, y, metric],
                    "id": f"{y}_{metric[0]}"
                }
                for y in SECTION_11_YEARS[1:]
                for metric in ["Projection", "% Change from 2021"]
            ]
        )

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-11-1-2',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, _LABEL_COL, 
                                          geo_headers={_LABEL_COL}, total_labels={'Total', 'Full population for comparison'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=3,
                left_align_cells=[{'column_id':_LABEL_COL, 'header_index': 1},
                                  {'column_id':_LABEL_COL, 'header_index': 2}]
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='15%'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-11-1-2'),
        ], className='pg2-table-lgeo')