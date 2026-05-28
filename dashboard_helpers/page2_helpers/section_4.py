"""
Section 4 preparation and layout - Housing Tenure.
"""

import pandas as pd
import numpy as np
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
    format_percent
)
from .text_content import SECTION_4_TITLE, TABLE_4_1_TITLE, TABLE_4_1_DESC, TABLE_4_3_TITLE

from dashboard_helpers.config import (
    CHART_COLORS, PLOT_CONFIG, YEARS,
    YEARS_MINUS_2011, COMMUNITIES, TABLE_FONT)

from .export_helpers import with_export_btn


class Section4Prep:
    """Prepare and format Section 4 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def prepare_table_4_1_data(self, geocode: int) -> pd.DataFrame:
        filtered = self.data_loader.get_table('table_4_1_housing_tenure', geocode, check_columns=YEARS)

        if filtered.empty:
            return pd.DataFrame()

        filtered = filtered.copy()

        pct_mask = filtered['Households by Tenure'].str.contains('of Owners|of Renters', na=False)
        for year in YEARS:
            filtered.loc[pct_mask, year] = filtered.loc[pct_mask, year].apply(
                lambda v: format_percent(v, multiply=False)
            )
            filtered.loc[~pct_mask, year] = filtered.loc[~pct_mask, year].apply(
                lambda v: format_number(v, decimals=0)
            )

        # Split by household type and prefix year columns
        indg = (
            filtered[filtered['Household Type'] == 'Indigenous HHs']
            [['Households by Tenure'] + YEARS]
            .rename(columns={y: f'indg_{y}' for y in YEARS})
        )
        non_indg = (
            filtered[filtered['Household Type'] == 'Non-Indigenous HHs']
            [['Households by Tenure'] + YEARS]
            .rename(columns={y: f'non_indg_{y}' for y in YEARS})
        )

        result = indg.merge(non_indg, on='Households by Tenure', how='left')

        non_indg_cols = [f'non_indg_{y}' for y in YEARS]
        result[non_indg_cols] = result[non_indg_cols].fillna('N/A')

        indg_cols = [f'indg_{y}' for y in YEARS]
        all_val_cols = indg_cols + non_indg_cols

        rows = [blank_row('Households by Tenure', all_val_cols, 'Households by Tenure')]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            tenure = row['Households by Tenure']
            if tenure == 'Total' or 'without a mortgage' in str(tenure):
                rows.append(blank_row('Households by Tenure'))

        return pd.DataFrame(rows, dtype=object)
    

    def create_table_4_1_layout(self, geocode: int, show_both: bool = False):
        """
        Create Dash DataTable layout for Table 4.1 with Households by Tenure (2006, 2011, 2016, 2021).:
            Level 0 - geography name (merged across all year columns)
            Level 1 - "Indigenous HHs" / "Non-Indigenous HHs"
            Level 2 - census year
        """
        df = self.prepare_table_4_1_data(geocode)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Households by Tenure (2006, 2011, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")
        _LABEL_COL = "Households by Tenure"
        

        columns = [
            {"name": [geo_name, "", "Census Year"], "id": _LABEL_COL}
        ] + [
            {"name": [geo_name, "Indigenous HHs", y], "id": f"indg_{y}"}
            for y in YEARS
        ]
        if show_both:
            columns += [
                {"name": [geo_name, "Non-Indigenous HHs", y], "id": f"non_indg_{y}"}
                for y in YEARS
            ]
        

        data_cols = [_LABEL_COL] + [f'indg_{y}' for y in YEARS]
        if show_both:
            data_cols += [f'non_indg_{y}' for y in YEARS]
        df_display = df[data_cols]

        base_style = get_base_table_style()
        data_cols.remove(_LABEL_COL)
        # print(data_cols)

        table = dash_table.DataTable(
            id='table-4-1',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL, section_headers={_LABEL_COL}, 
                                          geo_headers={"Indigenous HHs", "Non-Indigenous HHs"}
                                          )
            ),
            style_header_conditional=generate_style_header_conditional(columns, is_multiindex=True,
                                                                       first_col_id=_LABEL_COL, n_header_rows=3),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-4-1'),
        ], className='pg2-table-lgeo')


    def create_chart_4_1(self, geocode: int):
        """Create stacked bar chart for Table 4.1 for housing tenure over time."""
        filtered = self.data_loader.get_table('table_4_1_housing_tenure', geocode, check_columns=YEARS)
        
        if filtered.empty:
            return html.Div([
                html.H3(SECTION_4_TITLE, className='table-title'),
                html.H4(TABLE_4_1_TITLE, className='table-title'),
                html.H6(TABLE_4_1_DESC, className='table-desc'),
                html.Div(
                "No chart for housing tenure over time (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs'].copy()
        _LABEL_COL = "Households by Tenure"

        # Pull owner count and the two mortgage % rows for derivation
        owner_raw = indg[indg[_LABEL_COL] == 'Owner']
        pct_with = indg[
            indg[_LABEL_COL].str.contains('with mortgage', na=False) &
            indg[_LABEL_COL].str.contains('%', na=False)
        ]
        pct_without = indg[
            indg[_LABEL_COL].str.contains('without a mortgage', na=False) &
            indg[_LABEL_COL].str.contains('%', na=False)
        ]

        def _derive(label, pct_df):
            """Owner count x mortgage % """
            owner_counts = (
                pd.to_numeric(owner_raw[YEARS].iloc[0], errors='coerce').fillna(0)
                if not owner_raw.empty else pd.Series(0.0, index=YEARS)
            )
            pcts = (
                pd.to_numeric(pct_df[YEARS].iloc[0], errors='coerce').fillna(0)
                if not pct_df.empty else pd.Series(0.0, index=YEARS)
            )
            derived = (owner_counts * pcts / 100).round().astype(int)
            return {_LABEL_COL: label, **derived.to_dict()}

        # Count rows: exclude % rows, Total, and 'Owner' (split into two derived rows)
        count_rows = indg[
            ~indg[_LABEL_COL].str.contains('%', na=False) &
            (indg[_LABEL_COL] != 'Total') &
            (indg[_LABEL_COL] != 'Owner')
        ].copy()

        derived = pd.DataFrame([
            _derive('Owner with a mortgage', pct_with),
            _derive('Owner without a mortgage', pct_without),
        ])
        count_rows = pd.concat([derived, count_rows], ignore_index=True)

        total_rows = indg[indg[_LABEL_COL] == 'Total'].copy()
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        count_indexed = count_rows.set_index(_LABEL_COL)[YEARS]
        totals_series = (
            pd.to_numeric(total_rows[YEARS].iloc[0], errors='coerce').fillna(0)
            if not total_rows.empty else pd.Series(0.0, index=YEARS)
        )

        tenure_list = count_rows[_LABEL_COL].unique()
        colors = {t: CHART_COLORS[i % len(CHART_COLORS)] for i, t in enumerate(tenure_list)}

        fig = go.Figure()
        for i, tenure in enumerate(tenure_list):
            counts = pd.to_numeric(count_indexed.loc[tenure], errors='coerce').fillna(0)
            percentages = (
                counts / totals_series.replace(0, float('nan')) * 100
            ).fillna(0).tolist()

            fig.add_trace(go.Bar(
                name=tenure,
                x=YEARS,
                y=percentages,
                marker_color=colors[tenure],
                legendrank=len(tenure) - i,
                # text=[f"{p:.1f}%" for p in percentages],
                textposition='inside',
                hovertemplate=f'<b>{tenure}</b><br>Year: %{{x}}<br>Percentage: %{{y:.1f}}%<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=f'Indigenous Households by Tenure - {geo_name}', x=0.5, xanchor='center'),
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
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H3(SECTION_4_TITLE, className='table-title'),
            html.H4(TABLE_4_1_TITLE, className='table-title'),
            html.H6(TABLE_4_1_DESC, className='table-desc'),
            dcc.Graph(id='chart-4-1', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_4_2_layout(self, geocode: int):
        """Create Dash DataTable for Table 4.2 with housing tenure over time by Indigenous communities."""
        df = self.data_loader.get_table('table_4_2_housing_tenure_breakdown', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for housing tenure over time by Indigenous communities.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")
        _LABEL_COL = 'Households by Tenure'
        

        community_df = []
        for community in COMMUNITIES:
            indig_df = (
                df[df['Indigenous Community'] == community]
                .set_index(_LABEL_COL)[YEARS_MINUS_2011]
                .rename(columns={y: f'{y}_{community[0]}' for y in YEARS_MINUS_2011})
            )
            community_df.append(indig_df)

        table_df = (
            pd.concat(community_df, axis=1)
            .reset_index()
        )

        # Column order: year, community (2006_f, 2006_m, 2006_i, 2016_f, ...)
        val_cols = [f'{y}_{c[0]}' for y in YEARS_MINUS_2011 for c in COMMUNITIES]

        pct_mask = table_df[_LABEL_COL].str.contains('of Owners|of Renters', na=False)
        for col in val_cols:
            table_df.loc[pct_mask, col] = table_df.loc[pct_mask, col].apply(
                lambda v: format_percent(v, multiply=False)
            )
            table_df.loc[~pct_mask, col] = table_df.loc[~pct_mask, col].apply(format_number)

        # Prepend section header row

        rows = [blank_row(_LABEL_COL, val_cols, _LABEL_COL)]
        for _, row in table_df.iterrows():
            rows.append(row.to_dict())
            tenure = row['Households by Tenure']
            if tenure == 'Total' or 'without a mortgage' in str(tenure):
                rows.append(blank_row('Households by Tenure'))

        formatted_df = pd.DataFrame(rows, dtype=object)

        # 3-level columns: [geo_name, year, community]
        columns = [{"name": ["", "", ""], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-4-2',
            columns=columns,
            data=formatted_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(formatted_df)
                + make_special_row_styles(formatted_df, _LABEL_COL, geo_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-4-2'),
        ], className='pg2-table-lgeo')
    

    def create_table_4_3_layout(self, geocode: int, show_both: bool = False):
        """Create Dash DataTable for Table 4.3 with households by household size"""
        df = self.data_loader.get_table('table_4_3_hh_by_household_size', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for households by household size.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        filtered = df.copy()
        _LABEL_COL = 'Households by Size (number of people)'

        dec_mask = filtered[_LABEL_COL].str.contains('Average', na=False)
        for year in YEARS_MINUS_2011:
            filtered.loc[dec_mask, year] = filtered.loc[dec_mask, year].apply(
                lambda v: format_number(v, decimals=1)
            )
            filtered.loc[~dec_mask, year] = filtered.loc[~dec_mask, year].apply(
                lambda v: format_number(v, decimals=0)
            )

        # Split by household type and prefix year columns
        indg = (
            filtered[filtered['Household Type'] == 'Indigenous HHs']
            [[_LABEL_COL] + YEARS_MINUS_2011]
            .rename(columns={y: f'indg_{y}' for y in YEARS_MINUS_2011})
        )
        non_indg = (
            filtered[filtered['Household Type'] == 'Non-Indigenous HHs']
            [[_LABEL_COL] + YEARS_MINUS_2011]
            .rename(columns={y: f'non_indg_{y}' for y in YEARS_MINUS_2011})
        )

        result = indg.merge(non_indg, on=_LABEL_COL, how='left')

        non_indg_cols = [f'non_indg_{y}' for y in YEARS_MINUS_2011]
        result[non_indg_cols] = result[non_indg_cols].fillna('N/A')

        indg_cols = [f'indg_{y}' for y in YEARS_MINUS_2011]
        all_val_cols = indg_cols + non_indg_cols

        rows = [blank_row(_LABEL_COL, all_val_cols, _LABEL_COL)]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            tenure = row[_LABEL_COL]
            if tenure == 'Total' in str(tenure):
                rows.append(blank_row(_LABEL_COL))

        df_display = pd.DataFrame(rows, dtype=object)
    
        columns = [
            {"name": ["", "Census Year", ""], "id": _LABEL_COL}
        ] + [
            {"name": [geo_name, "Indigenous HHs", y], "id": f"indg_{y}"}
            for y in YEARS_MINUS_2011
        ]
        if show_both:
            columns += [
                {"name": [geo_name, "Non-Indigenous HHs", y], "id": f"non_indg_{y}"}
                for y in YEARS_MINUS_2011
            ]

        data_cols = [_LABEL_COL] + [f'indg_{y}' for y in YEARS_MINUS_2011]
        if show_both:
            data_cols += [f'non_indg_{y}' for y in YEARS_MINUS_2011]
        df_display = df_display[data_cols]

        base_style = get_base_table_style()
        data_cols.remove(_LABEL_COL)

        table = dash_table.DataTable(
            id='table-4-3',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL, 
                                          geo_headers={_LABEL_COL}, total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(columns, is_multiindex=True, first_col_id=_LABEL_COL),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-4-3'),
        ], className='pg2-table-lgeo')
    

    def create_chart_4_3(self, geocode: int):
        """Create stacked bar chart for Table 4.3 households by household size."""
        filtered = self.data_loader.get_table('table_4_3_hh_by_household_size', geocode, check_columns=YEARS_MINUS_2011)

        if filtered.empty:
            return html.Div([
                html.H4(TABLE_4_3_TITLE, className='table-title'),
                html.Div(
                "No chart for households by household size.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs'].copy()
        hh_size_col = 'Households by Size (number of people)'

        count_rows = indg[~indg[hh_size_col].isin(['Total', 'Average Household Size'])].copy()

        total_rows = indg[indg[hh_size_col] == 'Total'].copy()
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        count_indexed = count_rows.set_index(hh_size_col)[YEARS_MINUS_2011]
        totals_series = (
            pd.to_numeric(total_rows[YEARS_MINUS_2011].iloc[0], errors='coerce').fillna(0)
            if not total_rows.empty else pd.Series(0.0, index=YEARS_MINUS_2011)
        )

        tenure_list = count_rows[hh_size_col].unique()
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
                legendrank=len(tenure) - i,
                # text=[f"{p:.1f}%" for p in percentages],
                textposition='inside',
                hovertemplate=f'<b>{tenure}</b><br>Year: %{{x}}<br>Percentage: %{{y:.1f}}%<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=f'Indigenous Households by Household Size - {geo_name}', x=0.5, xanchor='center'),
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
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H4(TABLE_4_3_TITLE, className='table-title'),
            dcc.Graph(id='chart-4-3', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_4_4_layout(self, geocode: int):
        """Create Dash DataTable for Table 4.4 with households by household size by Indigenous communities."""
        df = self.data_loader.get_table('table_4_4_hh_by_household_size_breakdown', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for households by household size by Indigenous communities.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = 'Households by Size (number of people)'
        communities = [comm + "-led Households by Size (number of people)"  for comm in COMMUNITIES]

        community_df = []
        for community in communities:
            indig_df = (
                df[df['Household Type'] == community]
                .set_index(_LABEL_COL)[YEARS_MINUS_2011]
                .rename(columns={y: f'{y}_{community[0]}' for y in YEARS_MINUS_2011})
            )
            community_df.append(indig_df)

        table_df = pd.concat(community_df, axis=1).reset_index()

        # Column order: year, community (2006_f, 2006_m, 2006_i, 2016_f, ...)
        val_cols = [f'{y}_{c[0]}' for y in YEARS_MINUS_2011 for c in COMMUNITIES]

        dec_mask = table_df[_LABEL_COL].str.contains('Average', na=False)
        for col in val_cols:
            table_df.loc[dec_mask, col] = table_df.loc[dec_mask, col].apply(
                lambda v: format_number(v, decimals=1)
            )
            table_df.loc[~dec_mask, col] = table_df.loc[~dec_mask, col].apply(format_number)

        # Prepend section header row

        rows = [blank_row(_LABEL_COL, val_cols, _LABEL_COL)]
        for _, row in table_df.iterrows():
            rows.append(row.to_dict())
            tenure = row[_LABEL_COL]
            if tenure == 'Total' in str(tenure):
                rows.append(blank_row(_LABEL_COL))

        formatted_df = pd.DataFrame(rows, dtype=object)

        # 3-level columns: [geo_name, year, community]
        columns = [{"name": ["", "", ""], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-4-4',
            columns=columns,
            data=formatted_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(formatted_df)
                + make_special_row_styles(formatted_df, _LABEL_COL, 
                                          geo_headers={_LABEL_COL}, total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-4-4'),
        ], className='pg2-table-lgeo')

    def prepare_table_4_5_data(self, geocode: int):
        df = self.data_loader.get_table('table_4_5_1_4_5_2_hh_by_family_type', geocode, check_columns=YEARS_MINUS_2011)

        _LABEL_COL = 'Family Type'

        pct_mask = df[_LABEL_COL].str.contains('%', na=False)
        for year in YEARS_MINUS_2011:
            df.loc[pct_mask, year] = df.loc[pct_mask, year].apply(
                lambda v: format_percent(v, multiply=False)
            )
            df.loc[~pct_mask, year] = df.loc[~pct_mask, year].apply(
                lambda v: format_number(v, decimals=0)
            )

        indg = (
            df[df['Household Type'] == 'Indigenous HHs'].copy()
            .reset_index(drop=True)
            .rename(columns={y: f'indg_{y}' for y in YEARS_MINUS_2011})
        )
        non_indg = (
            df[df['Household Type'] == 'Non-Indigenous HHs'].copy()
            .reset_index(drop=True)
            .rename(columns={y: f'non_indg_{y}' for y in YEARS_MINUS_2011})
        )

        drop_cols = ['pk','Geocode','Geography','Household Type']
        result = indg.drop(columns=drop_cols).merge(non_indg.drop(columns=drop_cols), on=_LABEL_COL, how='left')
        all_val_cols = [c for c in result if c != _LABEL_COL]

        rows = [blank_row(_LABEL_COL, all_val_cols, f"Households by {_LABEL_COL}")]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            famtype = row[_LABEL_COL]
            if '%' in str(famtype):
                rows.append(blank_row(_LABEL_COL))

        return pd.DataFrame(rows, dtype=object)

    def create_table_4_5_layout(self, geocode: int, show_both: bool=True) -> html.Div:
        """techinically starts out life as table 4.5.1 and 4.5.2"""
        # TODO: CR WIP
        #  -> Establish for sure that we don't need "show_both" arg
        #

        df = self.prepare_table_4_5_data(geocode)

        if df.empty:
            return html.Div([
                html.Div(
                    "No data for households by family type by Indigenous communities.",
                    style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")
        _LABEL_COL = 'Family Type'

        if show_both: # TODO - we probably won't need this switch, but keeping for now in case
            hh_types = ["Indigenous HHs", "Non-Indigenous HHs"]
            prefixes = ['indg', 'non_indg']
            # df_display = pd.concat([indg[YEARS_MINUS_2011], non_indg[YEARS_MINUS_2011]], axis=1, ignore_index=True)
        else:
            hh_types = ["Indigenous HHs"]
            prefixes = ['indg']

        columns = [
                      {"name": [geo_name, "", "Census Year"], "id": _LABEL_COL}
                  ] + [
                      {"name": [geo_name, y, hh_type], "id": f"{pref}_{y}"}
                      for y in YEARS_MINUS_2011
                      for hh_type, pref in zip(hh_types, prefixes)
                  ]
        data_cols = [f"{pref}_{y}" for y in YEARS_MINUS_2011 for pref in prefixes]
        df_display = df[[_LABEL_COL] + data_cols]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-4-5',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL,
                                          geo_headers={'Households by Family Type'}, total_labels={'Total Households for reference'})
            ),
            style_header_conditional=generate_style_header_conditional(columns, is_multiindex=True, first_col_id=_LABEL_COL),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='160px'),
            **base_style
        )
        return html.Div([
            with_export_btn(table, 'table-4-5'),
        ], className='pg2-table-lgeo')

    def prepare_table_4_6_data(self, geocode):
        df = self.data_loader.get_table('table_4_5_3_hh_by_family_type_distinction', geocode, check_columns=YEARS_MINUS_2011)

        _LABEL_COL = 'Family Type'

        pct_mask = df[_LABEL_COL].str.contains('%', na=False)
        for year in YEARS_MINUS_2011:
            df.loc[pct_mask, year] = df.loc[pct_mask, year].apply(
                lambda v: format_percent(v, multiply=False)
            )
            df.loc[~pct_mask, year] = df.loc[~pct_mask, year].apply(
                lambda v: format_number(v, decimals=0)
            )

        community_df = []
        for community in COMMUNITIES:
            indig_df = (
                df[df['Household Type'] == f"{community}-led"]
                .set_index(_LABEL_COL)[YEARS_MINUS_2011]
                .rename(columns={y: f'{y}_{community[0]}' for y in YEARS_MINUS_2011})
            )
            community_df.append(indig_df)

        all_val_cols = [f'{y}_{community[0]}' for y in YEARS_MINUS_2011 for community in COMMUNITIES]
        table_df = (
            pd.concat(community_df, axis=1)
            .reset_index()
        )

        rows = [blank_row(_LABEL_COL, all_val_cols, f"Households by {_LABEL_COL}")]
        for _, row in table_df.iterrows():
            rows.append(row.to_dict())
            famtype = row[_LABEL_COL]
            if '%' in str(famtype):
                rows.append(blank_row(_LABEL_COL))

        return pd.DataFrame(rows, dtype=object), all_val_cols

    def create_table_4_6_layout(self, geocode: int) -> html.Div:
        # TODO CR - techinically starts out life as table 4.5.3
        df, data_cols = self.prepare_table_4_6_data(geocode)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for households by family type by Indigenous community.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")
        _LABEL_COL = 'Family Type'

        # 3-level columns: [geo_name, year, community]
        columns = [{"name": ["", "", ""], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()
        table = dash_table.DataTable(
            id='table-4-5',
            columns=columns,
            data=df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df)
                + make_special_row_styles(df, _LABEL_COL,
                                          geo_headers={'Households by Family Type'}, total_labels={'Total Households for reference'})
            ),
            style_header_conditional=generate_style_header_conditional(columns, is_multiindex=True, first_col_id=_LABEL_COL),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-4-6'),
        ], className='pg2-table-lgeo')


if __name__ == "__main__":
    t = Section4Prep()
    # t.create_table_4_1_layout(5915022)
    # t.create_table_4_3_layout(5915022)
    # t.create_table_4_5_layout(5915022)
    t.create_table_4_6_layout(5915022)