"""
Section 6 preparation and layout - Dwellings.
"""
import re
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
    make_style_cell,
    format_number
)
from ..content_helpers.text_content import (
    SECTION_6_TITLE, SECTION_6_P1, SECTION_6_P2,
    TABLE_6_1_TITLE, CHART_6_1_DESC, TABLE_6_1_DESC,
    TABLE_6_2_DESC,
    TABLE_6_3_TITLE, CHART_6_3_DESC, TABLE_6_3_DESC,
    TABLE_6_4_DESC, 
    TABLE_6_5_TITLE, TABLE_6_5_DESC, TABLE_6_6_DESC
    )

from dashboard_helpers.config import (
    CHART_COLORS, PLOT_CONFIG,
    YEARS_MINUS_2011, COMMUNITIES, TABLE_FONT
    )

from ..content_helpers.export_helpers import with_export_btn

class Section6Prep:
    """Prepare and format Section 6 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_6_primary_layout(self, geocode: int, sql_table_name: str, 
                                      label_col_name: str, show_both: bool = False):
        
        """Create Dash DataTable for Table 6.1 with Households by Number of Bedrooms of Dwelling"""
        """Create Dash DataTable for Table 6.3 with Households by Period of Construction of Dwelling"""
        """Create Dash DataTable for Table 6.5 with Households by Structural Type of Dwelling"""

        # TODO: This optimization can be applied across dashboard, 
        # fetch all heterogenous views at one place and adjust as required per view

        df = self.data_loader.get_table(sql_table_name, geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                f"No data for {label_col_name}.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo'), True

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        filtered = df.copy()

        
        for col in YEARS_MINUS_2011:
            filtered[col] = filtered[col].map(format_number)

        # Split by household type and prefix year columns
        indg = (
            filtered[filtered['Household Type'] == 'Indigenous HHs']
            [[label_col_name] + YEARS_MINUS_2011]
            .rename(columns={y: f'indg_{y}' for y in YEARS_MINUS_2011})
        )
        non_indg = (
            filtered[filtered['Household Type'] == 'Non-Indigenous HHs']
            [[label_col_name] + YEARS_MINUS_2011]
            .rename(columns={y: f'non_indg_{y}' for y in YEARS_MINUS_2011})
        )

        result = indg.merge(non_indg, on=label_col_name, how='left')

        non_indg_cols = [f'non_indg_{y}' for y in YEARS_MINUS_2011]
        result[non_indg_cols] = result[non_indg_cols].fillna('N/A')

        indg_cols = [f'indg_{y}' for y in YEARS_MINUS_2011]
        all_val_cols = indg_cols + non_indg_cols

        blank_df = pd.DataFrame([blank_row(label_col_name, all_val_cols, label_col_name)],
                                dtype=object)

        df_display = pd.concat([blank_df, result.astype(object)], ignore_index=True)
    
        columns = [
            {"name": [geo_name, "", "Census Year"], "id": label_col_name}
        ] + [
            {"name": [geo_name, "Indigenous HHs", y], "id": f"indg_{y}"}
            for y in YEARS_MINUS_2011
        ]
        if show_both:
            columns += [
                {"name": [geo_name, "Non-Indigenous HHs", y], "id": f"non_indg_{y}"}
                for y in YEARS_MINUS_2011
            ]

        data_cols = [label_col_name] + [f'indg_{y}' for y in YEARS_MINUS_2011]
        if show_both:
            data_cols += [f'non_indg_{y}' for y in YEARS_MINUS_2011]
        df_display = df_display[data_cols]

        base_style = get_base_table_style()
        data_cols.remove(label_col_name)
        table_id_regex = re.search(r'(table)_([0-9]+)_([0-9]+)', sql_table_name)
        table_id = f"{table_id_regex.group(1)}-{table_id_regex.group(2)}-{table_id_regex.group(3)}"

        table = dash_table.DataTable(
            id=table_id,
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, label_col_name, 
                                          section_headers={label_col_name}, total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=label_col_name,
                left_align_cells={'column_id': label_col_name, 'header_index': 2}
                ),
            style_cell_conditional=make_style_cell(label_col_name, data_cols, label_min_width='160px'),
            **base_style
        )

        if table_id == 'table-6-5':
            return html.Div([
                with_export_btn(table, table_id),
            ], className='pg2-table-lgeo'), False

        else:
            return html.Div([
                with_export_btn(table, table_id),
            ], className='pg2-table-lgeo'), False
    

    def create_chart_6(self, geocode: int, sql_table_name: str, label_col_name: str):
        """Create stacked bar chart for Table 6.1 households by number of bedrooms."""
        """Create stacked bar chart for Table 6.3 households by period of construction."""

        filtered = self.data_loader.get_table(sql_table_name, geocode, check_columns=YEARS_MINUS_2011)

        chart_id_regex = re.search(r'(table)_([0-9]+)_([0-9]+)', sql_table_name)
        chart_id = f"chart-{chart_id_regex.group(2)}-{chart_id_regex.group(3)}"

        if chart_id == "chart-6-1":
            title_tags = html.Div([
                html.H4(SECTION_6_TITLE, className='table-title'),
                html.Div([html.P(SECTION_6_P1),
                          html.P(SECTION_6_P2)], className='pg2-text-content-lgeo'),
                html.H5(TABLE_6_1_TITLE, className='table-title'),
                html.Div([html.P(CHART_6_1_DESC)], className='pg2-text-content-lgeo'),
            ])
        else:
            title_tags = html.Div([
                html.H5(TABLE_6_3_TITLE, className='table-title'),
                html.Div([html.P(CHART_6_3_DESC)], className='pg2-text-content-lgeo')
            ])


        if filtered.empty:
            return html.Div([
                title_tags,
                html.Div(
                f"No chart for {label_col_name}.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs'].copy()

        count_rows = indg[indg[label_col_name] != 'Total'].copy()

        total_rows = indg[indg[label_col_name] == 'Total'].copy()
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        count_indexed = count_rows.set_index(label_col_name)[YEARS_MINUS_2011]
        totals_series = (
            pd.to_numeric(total_rows[YEARS_MINUS_2011].iloc[0], errors='coerce').fillna(0)
            if not total_rows.empty else pd.Series(0.0, index=YEARS_MINUS_2011)
        )

        tenure_list = count_rows[label_col_name].unique()
        colors = {t: CHART_COLORS[i % len(CHART_COLORS)] for i, t in enumerate(tenure_list)}

        fig = go.Figure()
        for i, tenure in enumerate(tenure_list):
            counts = pd.to_numeric(count_indexed.loc[tenure], errors='coerce').fillna(0)
            percentages = (
                counts / totals_series.replace(0, float('nan')) * 100
            ).fillna(0).tolist()

            fig.add_trace(go.Bar(
                name=tenure,
                x=YEARS_MINUS_2011,
                y=percentages,
                marker_color=colors[tenure],
                legendrank=-(i + 1),
                # text=[f"{p:.1f}%" for p in percentages],
                textposition='inside',
                hovertemplate=f'<b>{tenure}</b><br>Year: %{{x}}<br>Percentage: %{{y:.1f}}%<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=f'Indigenous {label_col_name} - {geo_name}', x=0.5, xanchor='center'),
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
            autosize=True,
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, traceorder="reversed")
        )
        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)

        return html.Div([
            title_tags,
            dcc.Graph(id=chart_id, figure=fig, config=PLOT_CONFIG,
                      config={"responsive": True}, 
                      style={"width": "100%", "height": "100%"})
        ], className='pg2-table-lgeo')
    

    def create_table_6_secondary_layout(self, geocode: int, sql_table_name: str, label_col_name: str):
        """Create Dash DataTable for Table 6.2 with Households by Number of Bedrooms of Dwelling by Indigenous communities."""
        """Create Dash DataTable for Table 6.4 with Households by Period of Construction of Dwelling by Indigenous communities."""
        """Create Dash DataTable for Table 6.6 with Households by Structural Type of Dwelling by Indigenous communities."""

        df = self.data_loader.get_table(sql_table_name, geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                f"No data for {label_col_name} by Indigenous communities.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        community_df = []
        for community in COMMUNITIES:
            indig_df = (
                df[df['Distinction'] == community]
                .set_index(label_col_name)[YEARS_MINUS_2011]
                .rename(columns={y: f'{y}_{community[0]}' for y in YEARS_MINUS_2011})
            )
            community_df.append(indig_df)

        table_df = pd.concat(community_df, axis=1).reset_index()

        # Column order: year, community (2006_f, 2006_m, 2006_i, 2016_f, ...)
        val_cols = [f'{y}_{c[0]}' for y in YEARS_MINUS_2011 for c in COMMUNITIES]
        # print(table_df)

        for col in val_cols:
            table_df[col] = table_df[col].map(format_number)

        # Prepend section header row
        blank_df = pd.DataFrame([blank_row(label_col_name, val_cols, label_col_name)],
                                dtype=object)

        formatted_df = pd.concat([blank_df, table_df.astype(object)], ignore_index=True)


        # 3-level columns: [geo_name, year, community]
        columns = [{"name": [geo_name, "", "Census Year"], "id": label_col_name}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()
        table_id_regex = re.search(r'(table)_([0-9]+)_([0-9]+)', sql_table_name)
        table_id = f"{table_id_regex.group(1)}-{table_id_regex.group(2)}-{table_id_regex.group(3)}"

        table = dash_table.DataTable(
            id=table_id,
            columns=columns,
            data=formatted_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(formatted_df)
                + make_special_row_styles(formatted_df, label_col_name, 
                                          section_headers={label_col_name}, total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=label_col_name, n_header_rows=3,
                left_align_cells={'column_id': label_col_name, 'header_index': 2}
            ),
            style_cell_conditional=make_style_cell(label_col_name, val_cols, label_width='25%', label_min_width='120px'),
            **base_style
        )

        if table_id == 'table-6-2':
            return html.Div([
                html.Div([html.P(TABLE_6_2_DESC)], className='pg2-text-content-lgeo'),
                with_export_btn(table, table_id),
        ], className='pg2-table-lgeo')

        elif table_id == 'table-6-4':
            return html.Div([
                html.Div([html.P(TABLE_6_4_DESC)], className='pg2-text-content-lgeo'),
                with_export_btn(table, table_id),
        ], className='pg2-table-lgeo')

        else:
            return html.Div([
                html.Div([html.P(TABLE_6_6_DESC)], className='pg2-text-content-lgeo'),
                with_export_btn(table, table_id),
        ], className='pg2-table-lgeo')