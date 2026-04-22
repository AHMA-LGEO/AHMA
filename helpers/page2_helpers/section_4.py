"""
Table 4.1 and 4.2 preparation and layout - Housing Tenure.
"""
import pandas as pd
import numpy as np
from dash import dash_table, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from .data_loader import DataLoader
from .table_styles import (
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    get_special_row_styles,
    style_cell_4_1,
    format_number,
    format_percent
)
from .text_content import TABLE_4_1_TITLE, TABLE_4_1_DESC
from helpers.config import CHART_COLORS, PLOT_CONFIG


class Section4Prep:
    """Prepare and format Section 4 schemas."""

    def __init__(self):
        self.data_loader = DataLoader()

    def prepare_table_4_1_data(self, geocode: int) -> pd.DataFrame:
        filtered = self.data_loader.get_table('table_4_1_housing_tenure', geocode)

        if filtered.empty:
            return pd.DataFrame()

        year_cols = ['2006', '2011', '2016', '2021']

        # Format values in place for each household type
        for ht in filtered['Household Type'].unique():
            mask = filtered['Household Type'] == ht
            for year in year_cols:
                filtered.loc[mask, year] = filtered[mask].apply(
                    lambda row, y=year: self._format_cell(row['Households by Tenure'], row[y]),
                    axis=1
                )

        # Split by household type and prefix year columns
        indg = (
            filtered[filtered['Household Type'] == 'Indigenous HHs']
            [['Households by Tenure'] + year_cols]
            .rename(columns={y: f'indg_{y}' for y in year_cols})
        )
        non_indg = (
            filtered[filtered['Household Type'] == 'Non-Indigenous HHs']
            [['Households by Tenure'] + year_cols]
            .rename(columns={y: f'non_indg_{y}' for y in year_cols})
        )

        result = indg.merge(non_indg, on='Households by Tenure', how='left')

        # Fill any NaN in non-indigenous columns (tenure types absent from that group)
        non_indg_cols = [f'non_indg_{y}' for y in year_cols]
        result[non_indg_cols] = result[non_indg_cols].fillna('NA')

        # Build final row list with helper/separator rows inserted
        indg_cols = [f'indg_{y}' for y in year_cols]
        all_val_cols = indg_cols + non_indg_cols

        def blank_row(label=''):
            return {'Households by Tenure': label, **{c: '' for c in all_val_cols}}

        rows = [blank_row('Households by Tenure')]   # section header row
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            tenure = row['Households by Tenure']
            if tenure == 'TOTAL':
                rows.append(blank_row())             # separator after TOTAL
            elif 'without a mortgage' in str(tenure):
                rows.append(blank_row())             # separator after % of Owners without a mortgage

        return pd.DataFrame(rows, dtype=object)

    def create_table_4_1_layout(self, geocode: int, show_both: bool = False):
        """
        Create Dash DataTable layout for Table 4.1 with 3-level column headers:
            Level 0 – geography name (merged across all year columns)
            Level 1 – "Indigenous HHs" / "Non-Indigenous HHs"
            Level 2 – census year

        Args:
            geocode:   Geographic code
            show_both: If True, append Non-Indigenous HHs columns

        Returns:
            Dash HTML Div with table
        """
        df = self.prepare_table_4_1_data(geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        year_cols = ['2006', '2011', '2016', '2021']

        # 3-level column definitions
        columns = [
            {"name": ["", "Census Year", ""], "id": "Households by Tenure"}
        ] + [
            {"name": [geo_name, "Indigenous HHs", y], "id": f"indg_{y}"}
            for y in year_cols
        ]

        if show_both:
            columns += [
                {"name": [geo_name, "Non-Indigenous HHs", y], "id": f"non_indg_{y}"}
                for y in year_cols
            ]

        # Keep only the columns being displayed
        data_cols = ['Households by Tenure'] + [f'indg_{y}' for y in year_cols]
        if show_both:
            data_cols += [f'non_indg_{y}' for y in year_cols]
        df_display = df[data_cols]

        base_style = get_base_table_style()
        style_cell_conditional = style_cell_4_1(show_both)

        table = dash_table.DataTable(
            id='table-4-1',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + get_special_row_styles(df_display)
            ),
            style_header_conditional=generate_style_header_conditional(columns, is_multiindex=True),
            style_cell_conditional=style_cell_conditional,
            **base_style
        )

        layout = html.Div([
            dbc.Button("Export", id="export-table-4-1", className="export-pdf"),
            table
        ], className='pg2-table-lgeo')

        return layout


    def create_chart_4_1(self, geocode: int):
        """
        Create stacked bar chart for housing tenure over time.

        Args:
            geocode: Geographic code
            show_both: If True, show both Indigenous and Non-Indigenous

        Returns:
            Plotly Figure object
        """
        # Load data
        filtered = self.data_loader.get_table('table_4_1_housing_tenure', geocode)

        if filtered.empty:
            return go.Figure()

        # Charts always show Indigenous HHs only — filter once up front
        indg = filtered[filtered['Household Type'] == 'Indigenous HHs'].copy()

        years = ['2006', '2011', '2016', '2021']

        # Pull owner count and the two mortgage % rows for derivation
        owner_raw = indg[indg['Households by Tenure'] == 'Owner']
        pct_with = indg[
            indg['Households by Tenure'].str.contains('with mortgage', na=False) &
            indg['Households by Tenure'].str.contains('%', na=False)
        ]
        pct_without = indg[
            indg['Households by Tenure'].str.contains('without a mortgage', na=False) &
            indg['Households by Tenure'].str.contains('%', na=False)
        ]

        def _derive(label, pct_df):
            """Owner count × mortgage % """
            row = {'Households by Tenure': label}
            for year in years:
                try:
                    owner_count = float(owner_raw[year].iloc[0])
                    pct = float(pct_df[year].iloc[0])
                    row[year] = round(owner_count * pct / 100)
                except (IndexError, ValueError, TypeError):
                    row[year] = 0
            return row

        # Count rows: exclude % rows, TOTAL, and 'Owner' (split into two derived rows)
        count_rows = indg[
            ~indg['Households by Tenure'].str.contains('%', na=False) &
            (indg['Households by Tenure'] != 'TOTAL') &
            (indg['Households by Tenure'] != 'Owner')
        ].copy()

        derived = pd.DataFrame([
            _derive('Owner with a mortgage', pct_with),
            _derive('Owner without a mortgage', pct_without),
        ])
        count_rows = pd.concat([derived, count_rows], ignore_index=True)

        # Totals row for denominator (Indigenous only)
        total_rows = indg[indg['Households by Tenure'] == 'TOTAL'].copy()

        # Geography name
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        # Create stacked bar chart
        fig = go.Figure()

        tenure_list = count_rows['Households by Tenure'].unique()
        colors = {
            tenure: CHART_COLORS[i % len(CHART_COLORS)]
            for i, tenure in enumerate(tenure_list)
        }

        for tenure in tenure_list:
            tenure_data = count_rows[count_rows['Households by Tenure'] == tenure]

            percentages = []
            for year in years:
                count = tenure_data[year].iloc[0] if not tenure_data.empty else 0
                total = total_rows[year].iloc[0] if not total_rows.empty else 0

                try:
                    pct = (float(count) / float(total)) * 100 if float(total) > 0 else 0
                except (ValueError, TypeError):
                    pct = 0

                percentages.append(pct)

            fig.add_trace(go.Bar(
                name=tenure,
                x=years,
                y=percentages,
                marker_color=colors.get(tenure, '#95A5A6'),
                text=[f"{p:.1f}%" for p in percentages],
                textposition='inside',
                hovertemplate=f'<b>{tenure}</b><br>Year: %{{x}}<br>Percentage: %{{y:.1f}}%<extra></extra>'
            ))

        geo_name_display = geo_name or str(geocode)
        title_text = f'Indigenous Households by Tenure — {geo_name_display}'

        fig.update_layout(
            title=dict(text=title_text, x=0.5, xanchor='center'),
            xaxis_title='Census Year',
            yaxis=dict(
                title='Percentage of Households',
                ticksuffix='%',
                range=[0, 100],
                dtick=10,
                gridcolor='#E5E5E5',
            ),
            barmode='stack',
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Bahnschrift"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5
            )
        )


        chart_layout = html.Div([
            html.H4(TABLE_4_1_TITLE, className='table-title'),
            html.H6(TABLE_4_1_DESC, className='table-desc'),
            dcc.Graph(id='chart-4-1',figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
        
        return chart_layout

    def _format_cell(self, tenure_type: str, value):
        """Format cell based on tenure type."""
        if pd.isna(value):
            return 'NA'

        # Percentage rows
        if 'of Owners' in tenure_type or 'of Renters' in tenure_type:
            return format_percent(value, multiply=False)
        else:
            # Count rows
            return format_number(value, decimals=0)
        

# if __name__ == "__main__":
#     t = Table4Prep()
#     t.create_chart_4_1(5915022)
