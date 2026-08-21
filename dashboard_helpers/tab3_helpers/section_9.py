"""
Section 9 preparation and layout - Systemic Pathways and Indigenous Homelessness.
"""
import pandas as pd
from dash import dash_table, html, dcc
import plotly.graph_objects as go

from dashboard_helpers.content_helpers.data_loader import get_data_loader
from dashboard_helpers.content_helpers.table_styles import (
    blank_row,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    make_special_row_styles,
    get_special_row_styles_9_1,
    get_special_row_styles_9_3,
    make_style_cell,
    format_number,
    format_percent,
    make_data_table)
from ..content_helpers.text_content import (
    SECTION_9_TITLE, SECTION_9_P1, SECTION_9_P2,
    TABLE_9_1_TITLE, TABLE_9_1_DESC_P1, TABLE_9_1_DESC_P2, TABLE_9_1_DESC_P3,
    TABLE_9_1_LINK_1, TABLE_9_1_LINK_2, TABLE_9_1_LINK_3, TABLE_9_1_LINK_4,
    TABLE_9_2_TITLE, TABLE_9_2_DESC, TABLE_9_2_LINK,
    TABLE_9_3_TITLE, TABLE_9_3_DESC_P1, TABLE_9_3_DESC_P2, TABLE_9_3_DESC_P3,
    TABLE_9_3_LINK_1, TABLE_9_3_LINK_2, TABLE_9_3_LINK_3, TABLE_9_3_LINK_4
    )
from ..content_helpers.export_helpers import with_export_btn
from dashboard_helpers.config import (
    CHART_COLORS, TABLE_FONT, 
    PLOT_CONFIG, PIT_YEARS
    )

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
    "Length of time experiencing homelessness - Other/Unknown":                         "Unknown",
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

# Ordered display structure, grouped into the separate tables rendered on the
# page. Each group is a list of (top_header, [(sub_header, attrs), ...]) sections;
# sub_header "None" means the attributes hang directly off the top header.
# Groups 2-4 repeat the "All respondents" top header since they continue it.
_ROW_STRUCTURE_9_3 = [
    [
        ("Number of Indigenous people who experienced homelessness", [
            ("None", [
                "First Nations",
                "Métis",
                "Inuit",
                "Other/Multiple Indigenous Communities",
                "Total number of Indigenous people who experienced homelessness",
            ]),
            ("None", "% of people who experienced homelessness who were Indigenous"),
        ]),
    ],

    [
        ("All respondents", [
            ("Where people who experienced homelessness stayed the night of the Point-In-Time Count", [
                "All Respondents Sheltered",
                "All Respondents Unsheltered",
            ]),

            ("Length of time experiencing homelessness", [
                "Length of time experiencing homelessness - 12+ months",
                "Length of time experiencing homelessness - 6-12 months",
                "Length of time experiencing homelessness - <6 months",
                "Length of time experiencing homelessness - Other/Unknown",
                ]),
        ]),
    ],

    [
        ("All respondents", [
            ("Reason for housing loss", [
                "Reason for housing loss - Not enough income %",
                "Reason for housing loss - Substance use issue %",
                "Reason for housing loss - Conflict with landlord %",
                "Reason for housing loss - Conflict with spouse/partner %",
                "Reason for housing loss - Mental health issue %",
                "Reason for housing loss - Other %",
                ]),

            ("None", "% who identified eviction as cause of most recent housing loss"),
        ]),
    ],

    [
        ("All respondents", [
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
    ],
]


class Section9Prep:
    """Prepare and format Section 9 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def _cd_display_name(self, geocode: int) -> str:
        """
        Table 9.1/9.1.1 are only published at the CD level - the raw data already
        repeats the parent CD's figures onto every child CSD - so label the chart
        and table with the CD name instead of the selected CSD's.
        """
        is_csd = len(str(geocode)) == 7
        if is_csd:
            cd_geocode = self.data_loader.get_region_geocode(geocode)
            if cd_geocode:
                return self.data_loader.get_geography_name(int(cd_geocode)) or str(geocode)
        return self.data_loader.get_geography_name(geocode) or str(geocode)

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

        geo_name = self._cd_display_name(geocode)
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

        table = make_data_table(
            id='table-9-1',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + get_special_row_styles_9_1(df_display)
            ),
            style_header_conditional= generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Age', n_header_rows=2,
                left_align_cells={'column_id': 'Age', 'header_index': 1}
                ),
            style_cell_conditional=make_style_cell('Age', _FY_YEARS, label_width='20%'),
            **base_style
        )

        return html.Div([
            html.Div([html.P(TABLE_9_1_DESC_P3)], className='pg2-text-content-lgeo'),
            with_export_btn(table, 'table-9-1',
                            title=f'Indigenous People Released from Corrections by Age Group - {geo_name}'),
        ], className='pg2-table-lgeo')
    

    def create_chart_9_1(self, geocode: int):
        """Area chart for for Table 9.1 Indigenous People Released from Corrections (2008-2024)."""
        filtered = self.data_loader.get_table('table_9_1_number_corrections', geocode)

        if filtered.empty or filtered.isnull().values.all():
            return html.Div([
                html.H4(SECTION_9_TITLE, className='table-title'),
                html.Div([html.P(SECTION_9_P1),
                          html.P(SECTION_9_P2)], className='pg2-text-content-lgeo'),
                html.H5(TABLE_9_1_TITLE, className='table-title'),
                html.Div([dcc.Markdown(TABLE_9_1_DESC_P1),
                          html.Br(),
                        html.P(TABLE_9_1_DESC_P2),
                        html.P(dcc.Markdown(TABLE_9_1_LINK_1)),
                        html.P(dcc.Markdown(TABLE_9_1_LINK_2)),
                        html.P(dcc.Markdown(TABLE_9_1_LINK_3)),
                        html.P(dcc.Markdown(TABLE_9_1_LINK_4))], className='pg2-text-content-lgeo'),
                html.H5(TABLE_9_1_TITLE, className='table-title'),
                html.Div(
                    "No chart for Indigenous People Released from Corrections (2008-2024).",
                    style={'fontFamily': TABLE_FONT, 'color': '#666'}
                    )
            ], className='pg2-table-lgeo')

        geo_name = self._cd_display_name(geocode)
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
                hovertemplate=f'<br>Year: %{{x}}<br>Number of Indigenous People: %{{y:,.0f}}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f"Number of Indigenous People<br>Released from Corrections by Age Group<br><sup>{geo_name}</sup>",
                x=0.5, xanchor="center",
                # font=dict(size=15, family=TABLE_FONT),
            ),
            xaxis=dict(
                title='Fiscal Year',
                tickson='labels',
                automargin=True,
                range=[-0.5, len(_FY_YEARS) - 1.0],  # adds left/right padding
            ),

            yaxis=dict(
                title=dict(text='# Indigenous People', standoff=10),
                gridcolor='#E5E5E5',
                automargin=True,
                rangemode='tozero',
            ),
            plot_bgcolor='white',
            paper_bgcolor="white",
            font=dict(family=TABLE_FONT),
            margin=dict(l=70, r=20, t=70, b=100),
            autosize=True,
            height=560,
            legend=dict(orientation="h", yanchor="top",
                        y=-0.15, xanchor="center", x=0.5)
        )
        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)

        return html.Div([
            html.H4(SECTION_9_TITLE, className='table-title'),
            html.Div([html.P(SECTION_9_P1),
                      html.P(SECTION_9_P2)], className='pg2-text-content-lgeo'),
            html.H5(TABLE_9_1_TITLE, className='table-title'),
            html.Div([dcc.Markdown(TABLE_9_1_DESC_P1),
                      html.Br(),
                      html.P(TABLE_9_1_DESC_P2),
                      html.P(dcc.Markdown(TABLE_9_1_LINK_1)),
                      html.P(dcc.Markdown(TABLE_9_1_LINK_2)),
                      html.P(dcc.Markdown(TABLE_9_1_LINK_3)),
                      html.P(dcc.Markdown(TABLE_9_1_LINK_4))], className='pg2-text-content-lgeo'),
            dcc.Graph(id='chart-9-1', figure=fig, config=PLOT_CONFIG,
                      style={'height': '560px', 'width': '100%'})
        ], className='pg2-table-lgeo')


    def create_table_9_2_layout(self, geocode: int):
        """Create Dash DataTable for Table 9.2: Indigenous Children Ageing out of Care or Youth Agreements."""

        value_cols = ['Indigenous',	'Total Population', '% Indigenous']

        df = self.data_loader.get_table('table_9_2_ageing_out_of_care', geocode, check_columns=value_cols)

        if df.empty:
            return html.Div([
                html.H5(TABLE_9_2_TITLE, className='table-title'),
                html.Div([html.P(TABLE_9_2_DESC),
                          html.P(dcc.Markdown(TABLE_9_2_LINK))], className='pg2-text-content-lgeo'),
                html.Div(
                "No data for Indigenous Children Ageing out of Care or Youth Agreements.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        region_name = df["Geography"].iloc[0]
        df = df.fillna("N/A")

        table_df = df.set_index('Exit Reason')[value_cols].reset_index()

        for col in value_cols:
            fmt = (lambda v: format_percent(v, precision=0)) if col == '% Indigenous' else format_number
            table_df[col] = table_df[col].apply(fmt)


        columns = [{"name": [f"{geo_name} - {region_name} MCFD Region", "Data from MCFD Region - FY2024"], "id": "Exit Reason"}] + [
            {"name": [f"{geo_name} - {region_name} MCFD Region", col], "id": col} for col in value_cols
        ]

        base_style = get_base_table_style()

        table = make_data_table(
            id='table-9-2',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Exit Reason', total_labels={'Total Children Ageing Out of Care'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Exit Reason',
                left_align_cells={'column_id':'Exit Reason', 'header_index': 1}
            ),
            style_cell_conditional=make_style_cell('Exit Reason', value_cols, label_width='40%'),
            **base_style
        )

        return html.Div([
            html.H5(TABLE_9_2_TITLE, className='table-title'),
            html.Div([html.P(TABLE_9_2_DESC),
                      html.P(dcc.Markdown(TABLE_9_2_LINK))], className='pg2-text-content-lgeo'),
            with_export_btn(table, 'table-9-2',
                            title=f'Number of Indigenous Children Ageing out of Care or Youth Agreements (FY24) - {geo_name}'),
        ], className='pg2-table-lgeo')
    

    def create_table_9_3_layout(self, geocode: int):
        """Create Dash DataTable for Table 9.3: Indigenous Homelessness (2021, 2023, 2025)."""
        df = self.data_loader.get_table('table_9_3_indig_homelessness', geocode, check_columns=PIT_YEARS)

        if df.empty:
            return html.Div([
                html.H5(TABLE_9_3_TITLE, className='table-title'),
                html.Div([dcc.Markdown(TABLE_9_3_DESC_P1),
                        html.P(TABLE_9_3_DESC_P2),
                        html.Br(),
                        html.P(TABLE_9_3_DESC_P3),
                        html.P(dcc.Markdown(TABLE_9_3_LINK_1)),
                        html.P(dcc.Markdown(TABLE_9_3_LINK_2)),
                        html.P(dcc.Markdown(TABLE_9_3_LINK_3)),
                        html.P(dcc.Markdown(TABLE_9_3_LINK_4)),], className='pg2-text-content-lgeo'),
                html.Div(
                "No data for Indigenous Homelessness (2021, 2023, 2025).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        region_name = df["Region"].iloc[0]
        df = df.fillna("N/A")

        _LABEL_COL = 'Attribute'
        attr_idx = df.set_index(_LABEL_COL)

        def _attr_row(attr):
            if attr not in attr_idx.index:
                return None
            raw = attr_idx.loc[attr]
            fmt = format_number if attr in _NUMBER_ATTRS_9_3 else format_percent
            return {_LABEL_COL: _ATTR_RENAME_9_3.get(attr, attr), **{y: fmt(raw[y]) for y in PIT_YEARS}}

        def _group_rows(group):
            """Rows for one table - no blank spacers, the table split separates them."""
            out = []
            for top_header, sub_items in group:
                out.append(blank_row(_LABEL_COL, PIT_YEARS, top_header))
                for sub_header, sub_content in sub_items:
                    if sub_header != "None":
                        out.append(blank_row(_LABEL_COL, PIT_YEARS, sub_header))
                    attrs = [sub_content] if isinstance(sub_content, str) else sub_content
                    for attr in attrs:
                        r = _attr_row(attr)
                        if r:
                            out.append(r)
            return out

        columns = [{"name": [f"{geo_name} - {region_name} Point-in-Time Count", "Point-in-Time Count Year"], "id": _LABEL_COL}] + [
            {"name": [f"{geo_name} - {region_name} Point-in-Time Count", y], "id": y} for y in PIT_YEARS
        ]

        base_style = get_base_table_style()

        def _build(table_id, group_df):
            return make_data_table(
                id=table_id,
                columns=columns,
                data=group_df.to_dict('records'),
                merge_duplicate_headers=True,
                style_data_conditional=(
                    generate_style_data_conditional(group_df)
                    + get_special_row_styles_9_3(group_df)
                ),
                style_header_conditional=generate_style_header_conditional(
                    columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=2,
                    left_align_cells={'column_id': _LABEL_COL, 'header_index': 1}
                ),
                style_cell_conditional=make_style_cell(_LABEL_COL, PIT_YEARS, label_width='30%'),
                **base_style
            )

        tables, export_records = [], []
        for i, group in enumerate(_ROW_STRUCTURE_9_3):
            group_df = pd.DataFrame(_group_rows(group),
                                    columns=[_LABEL_COL] + PIT_YEARS).fillna("N/A")
            tables.append(_build('table-9-3' if i == 0 else f'table-9-3-{i + 1}', group_df))
            # The export stays a single sheet covering all four groups.
            if export_records:
                export_records.append(blank_row(_LABEL_COL, PIT_YEARS))
            export_records.extend(group_df.to_dict('records'))

        table_blocks = [with_export_btn(tables[0], 'table-9-3',
                                        export_data=export_records,
                                        export_columns=columns,
                                        title=f'Indigenous Homelessness - {geo_name}')]
        for tbl in tables[1:]:
            table_blocks += [html.Br(), tbl]

        return html.Div([
            html.H5(TABLE_9_3_TITLE, className='table-title'),
            html.Div([dcc.Markdown(TABLE_9_3_DESC_P1),
                      html.P(TABLE_9_3_DESC_P2),
                      html.Br(),
                      html.P(TABLE_9_3_DESC_P3),
                      html.P(dcc.Markdown(TABLE_9_3_LINK_1)),
                      html.P(dcc.Markdown(TABLE_9_3_LINK_2)),
                      html.P(dcc.Markdown(TABLE_9_3_LINK_3)),
                      html.P(dcc.Markdown(TABLE_9_3_LINK_4))
                      ], className='pg2-text-content-lgeo'),
            *table_blocks,
        ], className='pg2-table-lgeo')


# For testing
if __name__ == "__main__":
    t = Section9Prep()
    t.create_table_9_3_layout(59)