"""
Section 12 preparation and layout - Housing Targets.
"""
import pandas as pd
from dash import dash_table, html

from dashboard_helpers.content_helpers.data_loader import get_data_loader
from dashboard_helpers.content_helpers.table_styles import (
    blank_row,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    make_special_row_styles,
    make_style_cell,
    format_number,
    make_data_table)
from ..content_helpers.text_content import (
    SECTION_12_TITLE, SECTION_12_P1,
    TABLE_12_1_TITLE, TABLE_12_1_DESC_P1, TABLE_12_1_DESC_P2, TABLE_12_1_DESC_P3,
    TABLE_12_2_TITLE, TABLE_12_2_DESC, 
    # TABLE_12_2_NOTE
    )
from ..content_helpers.export_helpers import with_export_btn
from dashboard_helpers.config import TABLE_COLORS, TABLE_FONT

class Section12Prep:
    """Prepare and format Section 12 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_12_1_layout(self):
        """Static tables from AHMA provincial report: Table 4 and Table 6."""

        base_style = get_base_table_style()

        _LABEL_4 = "Households in Core Need 2021"
        _VAL_4   = "Number"

        table4_rows = [
            {_LABEL_4: _LABEL_4 + " ", _VAL_4: "17,145"},
            {_LABEL_4: "Subtract: Households in Subsidized Housing (affordability needs substantively met)", _VAL_4: "- 2,845"},
            {_LABEL_4: "Subtotal:",  _VAL_4: "14,300"},
            # blank_row(_LABEL_4, [_VAL_4]),
            {_LABEL_4: "Add: Households Experiencing Homelessness",  _VAL_4: "+ 4,541"},
            {_LABEL_4: "Subtotal:", _VAL_4: "18,841"},
            # blank_row(_LABEL_4, [_VAL_4]),
            {_LABEL_4: "Add: Projected Households with Incomes Below Core Need Threshold Unable to Find Appropriate Housing in the Market (15.5% of 27,407)", 
             _VAL_4: "+4,248"},
            # blank_row(_LABEL_4, [_VAL_4]),
            {_LABEL_4: "Total Need for Affordable Housing Solutions", _VAL_4: "23,089"},
        ]
        table4_df = pd.DataFrame(table4_rows, dtype=object)

        columns4 = [
            {"name": _LABEL_4, "id": _LABEL_4},
            {"name": _VAL_4, "id": _VAL_4},
        ]

        table4 = make_data_table(
            id='table-12-1-4',
            columns=columns4,
            data=table4_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table4_df)
                + make_special_row_styles(
                    table4_df, _LABEL_4,
                    section_headers={"Subtotal:", _LABEL_4 + " "},
                    total_labels={"Total Need for Affordable Housing Solutions"},
                )
            ),
            style_header_conditional=generate_style_header_conditional(
                columns4, is_multiindex=False, first_col_id=_LABEL_4,
            ) + [
                {'if': {'column_id': _LABEL_4}, 'backgroundColor': TABLE_COLORS['columns'],
                                                'textAlign': 'left',  'paddingLeft': '12px'},
                {'if': {'column_id': _VAL_4},   'textAlign': 'right', 'paddingRight': '12px'},
            ],
            style_cell_conditional=make_style_cell(_LABEL_4, [_VAL_4], label_width='75%'),
            **base_style
        )

        
        _LABEL_6 = "Affordable Housing Solutions"
        _VAL_6   = "Number"

        table6_rows = [
            # blank_row(_LABEL_6, [_VAL_6], "AFFORDABLE HOUSING SOLUTION"),
            {_LABEL_6: "Rent/affordability assistance",    _VAL_6: "8,900"},
            {_LABEL_6: "Supportive housing",               _VAL_6: "4,700"},
            {_LABEL_6: "Affordable homeownership",         _VAL_6: "950"},
            {_LABEL_6: "Independent subsidized housing",   _VAL_6: "8,500"},
            # blank_row(_LABEL_6, [_VAL_6]),
            {_LABEL_6: "Total Affordable Housing Solutions", _VAL_6: "23,000 (rounded)"},
        ]
        table6_df = pd.DataFrame(table6_rows, dtype=object)

        columns6 = [
            {"name": _LABEL_6, "id": _LABEL_6},
            {"name": _VAL_6,   "id": _VAL_6},
        ]

        table6 = make_data_table(
            id='table-12-1-6',
            columns=columns6,
            data=table6_df.to_dict('records'),
            merge_duplicate_headers=False,
            style_data_conditional=(
                generate_style_data_conditional(table6_df)
                + make_special_row_styles(
                    table6_df, _LABEL_6,
                    total_labels={"Total Affordable Housing Solutions"},
                )
            ),
            style_header_conditional=generate_style_header_conditional(
                columns6, is_multiindex=False, first_col_id=_LABEL_6,
            ) + [
                {'if': {'column_id': _LABEL_6}, 'backgroundColor': TABLE_COLORS['columns'],
                                                'textAlign': 'left',  'paddingLeft': '12px'},
                {'if': {'column_id': _VAL_6},   'textAlign': 'right', 'paddingRight': '12px'},
            ],
            style_cell_conditional=make_style_cell(_LABEL_6, [_VAL_6], label_width='75%'),
            **base_style
        )

        return html.Div([
            html.H4(SECTION_12_TITLE, className='table-title'),
            html.Div([html.P(SECTION_12_P1)], className='pg2-text-content-lgeo'),
            html.H5(TABLE_12_1_TITLE, className='table-title'),
            html.Div([html.P(TABLE_12_1_DESC_P1),
                      html.P(TABLE_12_1_DESC_P2),
                      html.P(TABLE_12_1_DESC_P3)], className='pg2-text-content-lgeo'),
            with_export_btn(table4, 'table-12-1-4',
                            title=f"AHMA's provincial results for 2034 - Households in Core Need 2021"),
            html.Br(),
            html.Br(),
            with_export_btn(table6, 'table-12-1-6',
                            title=f"AHMA's provincial results for 2034 - Affordable Housing Solutions"),
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
        _BREAKDOWN_LABEL = "Breakdown of Affordable Housing Solutions Needed"

        result = (df.set_index(_LABEL_COL)[_VAL_COL]
                  .reset_index()
                  .rename(columns={_LABEL_COL: ""}))

        result[_VAL_COL] = result[_VAL_COL].apply(format_number)
        total_row = result[result[""] == _TOTAL_ATTR]
        total_idx = total_row.index[0]

        # Split into two visual tables so each gets its own merged geography
        # header; the Total row closes the first and repeats to close the second.
        calc_df = result.loc[:total_idx].reset_index(drop=True)
        breakdown_df = pd.concat(
            [result.loc[total_idx + 1:], total_row], ignore_index=True
        )

        base_style = get_base_table_style()

        def build_table(table_id, label_header, table_df):
            columns = [{"name": [geo_name, label_header], "id": ""}] + [
                {"name": [geo_name, _VAL_COL], "id": _VAL_COL}
            ]
            table = make_data_table(
                id=table_id,
                columns=columns,
                data=table_df.to_dict('records'),
                merge_duplicate_headers=True,
                style_data_conditional=(
                    generate_style_data_conditional(table_df)
                    + make_special_row_styles(table_df, "", total_labels={_TOTAL_ATTR})
                ),
                style_header_conditional=generate_style_header_conditional(
                    columns, is_multiindex=True, first_col_id="", n_header_rows=2,
                    left_align_cells={'column_id': '', 'header_index': 1}
                ) + [
                    {'if': {'header_index': 1, 'column_id': _VAL_COL},
                     'textAlign': 'right', 'paddingRight': '12px'},
                ],
                style_cell_conditional=make_style_cell("", [_VAL_COL], label_width='65%'),
                **base_style
            )
            return table, columns

        calc_table, calc_columns = build_table('table-12-2', _LABEL_COL, calc_df)
        breakdown_table, _ = build_table('table-12-2-breakdown', _BREAKDOWN_LABEL, breakdown_df)

        # Both sections go into one sheet, separated by the breakdown's own header.
        export_data = (
            calc_df.to_dict('records')
            + [blank_row("", [_VAL_COL])]
            + [{"": _BREAKDOWN_LABEL, _VAL_COL: _VAL_COL}]
            + breakdown_df.to_dict('records')
        )

        return html.Div([
            html.H5(TABLE_12_2_TITLE, className='table-title'),
            html.Div([html.P(TABLE_12_2_DESC)], className='pg2-text-content-lgeo'),
            with_export_btn(calc_table, 'table-12-2',
                            export_data=export_data, export_columns=calc_columns,
                            title=f"Indigenous Housing Target - Urban, Rural and Northern (off-reserve) - {geo_name}"),
            html.Br(),
            breakdown_table,
            #html.I(TABLE_12_2_NOTE),
        ], className='pg2-table-lgeo')