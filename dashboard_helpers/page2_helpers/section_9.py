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
    make_style_cell,
    format_number,
    format_percent,
)
from .text_content import SECTION_9_TITLE, TABLE_9_1_TITLE
from .export_helpers import with_export_btn
from dashboard_helpers.config import CHART_COLORS, TABLE_FONT, PLOT_CONFIG, YEARS, YEARS_MINUS_2011

_FY_YEARS = [f"FY{i:02d}" for i in range(9, 25)]
AGE_GROUPS = ["Under 30", "30-49", "50+"]

class Section9Prep:
    """Prepare and format Section 9 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_9_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 9.1 and 9.1.1: Indigenous People Released from Corrections (2008-2024)."""

        df_9_1 = self.data_loader.get_table('table_9_1_number_corrections', geocode)
        df_9_1_1 = self.data_loader.get_table('table_9_1_1_percent_corrections', geocode)

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        
        # _AGE_GROUPS = ["Under 30", "30-49", "50+", "Total"]

        for col in _FY_YEARS:
            df_9_1[col] = df_9_1[col].map(format_number)
            df_9_1_1[col] = df_9_1_1[col].map(format_percent)

        label_col_1 = 'Number of people released who identify as indigenous'
        label_col_2 = 'Percentage of people released who identify as indigenous'

        rows = (
            [blank_row('Age', _FY_YEARS, label_col_1)]
            + df_9_1[['Age'] + _FY_YEARS].to_dict('records')
            + [blank_row('Age', _FY_YEARS)]
            + [blank_row('Age', _FY_YEARS, label_col_2)]
            + df_9_1_1[['Age'] + _FY_YEARS].to_dict('records')
        )

        df_display = pd.DataFrame(rows, columns=['Age'] + _FY_YEARS)

        columns = [{"name": ["", ""], "id": "Age"}] + [
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
                + make_special_row_styles(df_display, 'Age',
                                          total_labels={'Total'},
                                          section_headers={label_col_1, label_col_2})
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

        if filtered.empty:
            return go.Figure()

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
            xaxis_title='Fiscal Year',
            yaxis_title='# Indigenous People',
            paper_bgcolor="white",
            font=dict(family=TABLE_FONT),
            margin=dict(t=90, b=40, l=20, r=20),
            height=550,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H3(SECTION_9_TITLE, className='table-title'),
            html.H4(TABLE_9_1_TITLE, className='table-title'),
            dcc.Graph(id='chart-9-1', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
