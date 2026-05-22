"""
Section 9 preparation and layout - Systemic Pathways and Indigenous Homelessness.
"""
import pandas as pd
from dash import dash_table, html, dcc
import plotly.graph_objects as go

from .data_loader import get_data_loader
from .table_styles import (
    blank_row,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    make_special_row_styles,
    get_special_row_styles_9_1,
    get_special_row_styles_9_3,
    make_style_cell,
    format_number,
    format_percent
)
from .text_content import SECTION_9_TITLE, TABLE_9_1_TITLE, TABLE_9_2_TITLE, TABLE_9_3_TITLE
from .export_helpers import with_export_btn
from dashboard_helpers.config import CHART_COLORS, TABLE_FONT, PLOT_CONFIG, PIT_YEARS

_FY_YEARS = [f"FY{i:02d}" for i in range(9, 25)]
AGE_GROUPS = ["Under 30", "30-49", "50+"]


# ── Table 9.3 constants ──────────────────────────────────────────────────────
_ATTR_RENAME_9_3 = {
    "Total number of Indigenous people who experienced homelessness":                   "Total",
    "All Respondents Sheltered":                                                        "Sheltered",
    "All Respondents Unsheltered":                                                      "Unsheltered",
    "Length of time experiencing homelessness - 12+ months":                            "12+ months",
    "Length of time experiencing homelessness - 6-12 months":                           "6-12 months",
    "Length of time experiencing homelessness - <6 months":                             "<6 months",
    "Length of time experiencing homelessness - Other/Unknown":                         "Other",
    "Reason for housing loss - Not enough income %":                                    "Not enough income",
    "Reason for housing loss - Substance use issue %":                                  "Substance use issue",
    "Reason for housing loss - Conflict with landlord %":                               "Conflict with landlord",
    "Reason for housing loss - Conflict with spouse/partner %":                         "Conflict with spouse/partner",
    "Reason for housing loss - Mental health issue %":                                  "Mental health issue",
    "Reason for housing loss - Other %":                                                "Other",
    "% who experienced homelessness for the first time as a youth (Indigenous)":        "Indigenous respondents",
    "% who experienced homelessness for the first time as a youth (Non-Indigenous)":    "Non-Indigenous respondents",
    "% of youth who were in foster care (Indigenous)":                                  "Indigenous respondents",
    "% of youth who were in foster care (Non-Indigenous)":                              "Non-Indigenous respondents",
}

_NUMBER_ATTRS_9_3 = {"First Nations", "Métis", "Inuit", "Other/Multiple Indigenous Communities", 
                     "Total number of Indigenous people who experienced homelessness"}

# Ordered display structure: (section_header_or_None, [raw_attr_names])
_ROW_STRUCTURE_9_3 = [
    ("Number of Indigenous people who experienced homelessness (PEH)", [
        ("None", [
            "First Nations",
            "Métis",
            "Inuit",
            "Other/Multiple Indigenous Communities",
            "Total number of Indigenous people who experienced homelessness",
        ]),
        ("None", "% of PEH who were Indigenous"),
    ]),
    
    ("All respondents", [
        ("Where PEH stayed the night of the PIT count", [
            "All Respondents Sheltered",
            "All Respondents Unsheltered",
        ]),

        ("Length of time experiencing homelessness", [
            "Length of time experiencing homelessness - 12+ months",
            "Length of time experiencing homelessness - 6-12 months",
            "Length of time experiencing homelessness - <6 months",
            "Length of time experiencing homelessness - Other/Unknown",
            ]),

        ("Reason for housing loss", [
            "Reason for housing loss - Not enough income %",
            "Reason for housing loss - Substance use issue %",
            "Reason for housing loss - Conflict with landlord %",
            "Reason for housing loss - Conflict with spouse/partner %",
            "Reason for housing loss - Mental health issue %",
            "Reason for housing loss - Other %",
            ]),

        ("None", "% who identified eviction as cause of most recent housing loss"),

        ("% who experienced homelessness for the first time as a youth", [
            "% who experienced homelessness for the first time as a youth (Indigenous)",
            "% who experienced homelessness for the first time as a youth (Non-Indigenous)",
            ]),

        ("% of youth who were in foster care, youth group home, or an independent Living Agreement as a youth", [
            "% of youth who were in foster care (Indigenous)",
            "% of youth who were in foster care (Non-Indigenous)",
        ]),
        
        ("None", "% with acquired brain injury"),
    ]),
]


class Section9Prep:
    """Prepare and format Section 9 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_9_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 9.1 and 9.1.1: Indigenous People Released from Corrections (2008-2024)."""

        df_9_1 = self.data_loader.get_table('table_9_1_number_corrections', geocode, check_columns=_FY_YEARS)
        df_9_1_1 = self.data_loader.get_table('table_9_1_1_percent_corrections', geocode)

        if df_9_1.empty:
            return html.Div([
                html.Div(
                "No data for Indigenous People Released from Corrections (2008-2024).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df_9_1 = df_9_1.fillna("N/A")
        df_9_1_1 = df_9_1_1.fillna("N/A")
        
        # _AGE_GROUPS = ["Under 30", "30-49", "50+", "Total"]

        for col in _FY_YEARS:
            df_9_1.loc[:, col] = df_9_1.loc[:, col].map(format_number)
            df_9_1_1.loc[:, col] = df_9_1_1.loc[:, col].map(format_percent)

        label_col_1 = 'Number of people released who identify as indigenous'
        label_col_2 = 'Percentage of people released who identify as indigenous'

        rows = (
            # [blank_row('Age', _FY_YEARS, label_col_1)]
            # + 
            df_9_1[['Age'] + _FY_YEARS].to_dict('records')
            + [blank_row('Age', _FY_YEARS)]
            + [blank_row('Age', _FY_YEARS, label_col_2)]
            + df_9_1_1[['Age'] + _FY_YEARS].to_dict('records')
        )

        df_display = pd.DataFrame(rows, columns=['Age'] + _FY_YEARS)

        columns = [{"name": [geo_name, label_col_1], "id": "Age"}] + [
            {"name": [geo_name, y], "id": y} for y in _FY_YEARS
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-9-1',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + get_special_row_styles_9_1(df_display)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Age'
            ),
            style_cell_conditional=make_style_cell('Age', _FY_YEARS, label_width='20%'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-9-1'),
        ], className='pg2-table-lgeo')
    

    def create_chart_9_1(self, geocode: int):
        """Area chart for for Table 9.1 Indigenous People Released from Corrections (2008-2024)."""
        filtered = self.data_loader.get_table('table_9_1_number_corrections', geocode)

        if filtered.empty or filtered.isnull().values.all():
            return html.Div([
                html.H4(SECTION_9_TITLE, className='table-title'),
                html.H6(TABLE_9_1_TITLE, className='table-title'),
                html.Div(
                "No chart for Indigenous People Released from Corrections (2008-2024).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        plot_df = filtered[filtered['Age'] != 'Total']

        colors = {t: CHART_COLORS[i % len(CHART_COLORS)] for i, t in enumerate(AGE_GROUPS)}

        fig = go.Figure()
        for index, row in plot_df.iterrows():
            age_cat = row['Age']
            fig.add_trace(go.Scatter(
                x=_FY_YEARS, 
                y=row[_FY_YEARS], 
                name=age_cat,
                mode='lines',
                stackgroup='age_stack',
                line=dict(color=colors.get(age_cat, 'gray'), width=1),
                fillcolor=colors.get(age_cat),
                legendrank=len(colors) - index,
                hovertemplate=f'<br>Year: %{{x}}<br>Number of Indigenous People: %{{y}}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f"Number of Indigenous People<br>Released from Corrections by Age Group<br><sup>{geo_name}</sup>",
                x=0.5, xanchor="center",
                font=dict(size=15, family=TABLE_FONT),
            ),
            xaxis=dict(
                title='Fiscal Year',
                tickson='labels',
                automargin=True,
                range=[-0.5, len(_FY_YEARS) - 1.0],  # adds left/right padding
            ),

            yaxis=dict(
                title='# Indigenous People',
                gridcolor='#E5E5E5',
                automargin=True,
                rangemode='tozero',
            ),
            plot_bgcolor='white',
            paper_bgcolor="white",
            font=dict(family=TABLE_FONT),
            height=550,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H4(SECTION_9_TITLE, className='table-title'),
            html.H6(TABLE_9_1_TITLE, className='table-title'),
            dcc.Graph(id='chart-9-1', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')


    def create_table_9_2_layout(self, geocode: int):
        """Create Dash DataTable for Table 9.2: Indigenous Children Ageing out of Care or Youth Agreements."""

        df = self.data_loader.get_table('table_9_2_ageing_out_of_care', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        value_cols = ['Indigenous',	'Total Population', '% Indigenous']

        table_df = df.set_index('Exit Reason')[value_cols].reset_index()

        for col in value_cols:
            table_df[col] = table_df[col].apply(format_number)


        columns = [{"name": [geo_name, "Data from MCFD Region - FY2024"], "id": "Exit Reason"}] + [
            {"name": [geo_name, col], "id": col} for col in value_cols
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-9-2',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Exit Reason', total_labels={'Total Children Ageing Out of Care'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Exit Reason'
            ),
            style_cell_conditional=make_style_cell('Exit Reason', value_cols, label_width='40%'),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_9_2_TITLE, className='table-title'),
            with_export_btn(table, 'table-9-2'),
        ], className='pg2-table-lgeo')
    

    def create_table_9_3_layout(self, geocode: int):
        """Create Dash DataTable for Table 9.3: Indigenous Homelessness (2021, 2023, 2025)."""
        df = self.data_loader.get_table('table_9_3_indig_homelessness', geocode, check_columns=PIT_YEARS)

        if df.empty:
            return html.Div([
                html.H4(TABLE_9_3_TITLE, className='table-title'),
                html.Div(
                "No data for Indigenous Homelessness (2021, 2023, 2025).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        _LABEL_COL = 'Attribute'
        attr_idx = df.set_index(_LABEL_COL)

        def _attr_row(attr):
            if attr not in attr_idx.index:
                return None
            raw = attr_idx.loc[attr]
            fmt = format_number if attr in _NUMBER_ATTRS_9_3 else format_percent
            return {_LABEL_COL: _ATTR_RENAME_9_3.get(attr, attr), **{y: fmt(raw[y]) for y in PIT_YEARS}}

        rows = []
        for top_header, top_items in _ROW_STRUCTURE_9_3:
            rows.append(blank_row(_LABEL_COL, PIT_YEARS, top_header))

            if top_items and isinstance(top_items[0], str):
                # Flat list of attribute keys (first section)
                for attr in top_items:
                    r = _attr_row(attr)
                    if r:
                        rows.append(r)
                rows.append(blank_row(_LABEL_COL, PIT_YEARS))
            else:
                # Nested: list of (sub_header, sub_content) tuples
                for sub_header, sub_content in top_items:
                    if sub_header != "None":
                        rows.append(blank_row(_LABEL_COL, PIT_YEARS, sub_header))
                    attrs = [sub_content] if isinstance(sub_content, str) else sub_content
                    for attr in attrs:
                        r = _attr_row(attr)
                        if r:
                            rows.append(r)
                    rows.append(blank_row(_LABEL_COL, PIT_YEARS))

        df_display = pd.DataFrame(rows, columns=[_LABEL_COL] + PIT_YEARS).fillna("N/A")

        columns = [{"name": [geo_name, ""], "id": _LABEL_COL}] + [
            {"name": [geo_name, y], "id": y} for y in PIT_YEARS
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-9-3',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + get_special_row_styles_9_3(df_display)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=2
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, PIT_YEARS, label_width='30%'),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_9_3_TITLE, className='table-title'),
            with_export_btn(table, 'table-9-3'),
        ], className='pg2-table-lgeo')