"""
Section 12 preparation and layout - Housing Targets.
"""
import pandas as pd
from dash import dash_table, html

from .data_loader import get_data_loader
from .table_styles import (
    blank_row,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    make_special_row_styles,
    make_style_cell,
    format_number
)
from .text_content import SECTION_12_TITLE, TABLE_12_1_TITLE, TABLE_12_2_TITLE, TABLE_12_2_NOTE
from .export_helpers import with_export_btn
from dashboard_helpers.config import TABLE_FONT

class Section12Prep:
    """Prepare and format Section 12 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_12_1_layout(self):
        """Add static screenshots from AHMA's reports."""
        return html.Div([
            html.H4(SECTION_12_TITLE, className='table-title'),
            html.H5(TABLE_12_1_TITLE, className='table-title'),
            html.Img(src='./assets/Section 12.1 Table 4.png', className='footer-image'),
            html.Img(src='./assets/Section 12.1 Table 6.png', className='footer-image')
        ])

    def create_table_12_2_layout(self, geocode: int):
        """Create Dash DataTable for Table 12.2: Indigenous Housing Target."""

        df = self.data_loader.get_table('table_12_2_indigenous_housing_target', geocode, 
                                        check_columns=['# of HHs (2034)'])

        if df.empty:
            return html.Div([
                html.H5(TABLE_12_2_TITLE, className='table-title'),
                html.Div(
                "No data for Indigenous Housing Targets.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = "Calculation of Indigenous Housing Target"
        _VAL_COL = "# of HHs (2034)"
        _TOTAL_ATTR = "Total Indigenous Housing Need - 2034"

        result = (df.set_index(_LABEL_COL)[_VAL_COL]
                  .reset_index()
                  .rename(columns={_LABEL_COL: ""}))
                  
        result[_VAL_COL] = result[_VAL_COL].apply(format_number)
        total_row = result[result[""] == _TOTAL_ATTR]

        rows = [blank_row("", [_VAL_COL], _LABEL_COL)]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            attr = row[""] # Assigning blank column name in result df above
            if attr == _TOTAL_ATTR:
                rows.append(blank_row("", [_VAL_COL]))
                rows.append(blank_row("", [_VAL_COL], 'Breakdown of Affordable Housing Solutions Needed'))

        table_df = pd.DataFrame(rows, dtype=object)
        table_df = pd.concat([table_df, total_row], ignore_index=True)

        columns = [{"name": [geo_name, ""], "id": ""}] + [
            {"name": [geo_name, _VAL_COL], "id": _VAL_COL}
        ]

        section_headers = {
            'Calculation of Indigenous Housing Target',
            'Breakdown of Affordable Housing Solutions Needed',
        }

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-12-2',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, "", section_headers=section_headers,
                                          total_labels={"Total Indigenous Housing Need - 2034"})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=""
            ),
            style_cell_conditional=make_style_cell("", [_VAL_COL], label_width='65%'),
            **base_style
        )

        return html.Div([
            html.H5(TABLE_12_2_TITLE, className='table-title'),
            with_export_btn(table, 'table-12-2'),
            html.I(TABLE_12_2_NOTE),
        ], className='pg2-table-lgeo')