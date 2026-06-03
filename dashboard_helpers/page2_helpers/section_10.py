"""
Section 10 preparation and layout - Access to Services.
"""
import pandas as pd
import numpy as np
from dash import dash_table, html

from .data_loader import get_data_loader
from .table_styles import (
    blank_row,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    make_special_row_styles,
    make_style_cell,
    merge_columns,
    make_centered_merged_row_styles,
    format_number,
    format_percent
)
from .text_content import SECTION_10_TITLE, TABLE_10_1_TITLE

from dashboard_helpers.config import TABLE_FONT

from .export_helpers import with_export_btn

class Section10Prep:
    """Prepare and format Section 10 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_10_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 10.1: Access to Services."""
        
        value_cols = ['Transit', 'Walking', 'Biking']
        
        df = self.data_loader.get_table('table_10_1_access_services', geocode, check_columns=value_cols)

        if df.empty:
            return html.Div([
                html.H4(SECTION_10_TITLE, className='table-title'),
                html.H5(TABLE_10_1_TITLE, className='table-title'),
                html.Div(
                "No data for Access to Services.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        _LABEL_COL = 'Mode of Transport'
        df = df.fillna("N/A")

        
        # service_mapping = {
        #     'Health Care'                               : 'Health Care*',
        #     'Recreation Centres'                        : 'Recreation Centres*',
        #     'Primary or Secondary Education'            : 'Primary or Secondary Education*',
        #     'Child Care'                                : 'Child Care*',
        #     'Pharmacies (within 3 km buffer)'           : 'Pharmacies** (within 3 km buffer)',
        #     'Pharmacies (within 5 km buffer)'           : 'Pharmacies** (within 5 km buffer)',
        #     'Friendship Centres (within 10 km buffer)'  : 'Friendship Centres*** (within 10 km buffer)',
        #     'Friendship Centres (within 20 km buffer)'  : 'Friendship Centres*** (within 20 km buffer)'
        # }

        table_df = (df.set_index('Service')[value_cols]
                    .reset_index()
                    .rename(columns={'Service': _LABEL_COL})
                    )
        
        # table_df[_LABEL_COL] = table_df[_LABEL_COL].replace(service_mapping)

        number_mask = table_df[_LABEL_COL].str.contains('Number of Indigenous people', na=False)
        for col in value_cols:
            table_df.loc[number_mask, col] = table_df.loc[number_mask, col].apply(format_number)
            table_df.loc[~number_mask, col] = table_df.loc[~number_mask, col].apply(format_percent)


        title_row = '% of Indigenous people with access to services by public transport (2021)'
        rows = [blank_row(_LABEL_COL, value_cols, title_row)]
        for _, row in table_df.iterrows():
            rows.append(row.to_dict())
            tenure = row[_LABEL_COL]
            if tenure == 'Friendship Centres (within 20 km buffer)' in str(tenure):
                rows.append(blank_row(_LABEL_COL))

        formatted_df = pd.DataFrame(rows, dtype=object)

        columns = [{"name": [geo_name, _LABEL_COL], "id": _LABEL_COL}] + [
            {"name": [geo_name, col], "id": col} for col in value_cols
        ]

        base_style = get_base_table_style()

        # Row index 5-6 pharmacies, 7-8 friendship centres, 10 total number of indigenous people
        formatted_df = merge_columns(formatted_df, rows=list(np.arange(5,9)) + [10], value_cols=value_cols)

        table = dash_table.DataTable(
            id='table-10-1',
            columns=columns,
            data=formatted_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(formatted_df)
                + make_special_row_styles(formatted_df, _LABEL_COL, 
                                          section_headers={title_row},
                                          total_labels={'Number of Indigenous people in selected geography (for reference)'})
                + make_centered_merged_row_styles(rows=list(np.arange(5,9)) + [10], value_cols=value_cols)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL,
                left_align_cells={'column_id':_LABEL_COL, 'header_index': 1}
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, value_cols, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H4(SECTION_10_TITLE, className='table-title'),
            html.H5(TABLE_10_1_TITLE, className='table-title'),
            with_export_btn(table, 'table-10-1'),
        ], className='pg2-table-lgeo')