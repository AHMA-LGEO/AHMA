"""
Section 5 preparation and layout - Income.
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
    make_centered_merged_row_styles,
    make_style_cell,
    merge_columns,
    format_number,
    format_dollar,
    format_percent
)
from .text_content import (
    SECTION_5_TITLE, TABLE_5_1_TITLE, 
    TABLE_5_2_TITLE, TABLE_5_4_TITLE
    )

from dashboard_helpers.config import (
    CHART_COLORS, PLOT_CONFIG, YEARS_2016_2021,
    YEARS_MINUS_2011, COMMUNITIES, TABLE_FONT
    )

from .export_helpers import with_export_btn


class Section5Prep:
    """Prepare and format Section 5 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_5_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 5.1: HART income & shelter cost of Indigenous Households."""
        
        value_cols = ['% of Total Indigenous HHs', 'Annual HH Income', 
                      'Affordable Shelter Cost (2020 CAD$)']
        
        df = self.data_loader.get_table('table_5_1_income_shelter_cost', geocode, check_columns=value_cols)

        if df.empty:
            return html.Div([
                html.H4(SECTION_5_TITLE, className='table-title'),
                html.H6(TABLE_5_1_TITLE, className='table-title'),
                html.Div(
                "No data for HART income & shelter cost of Indigenous Households.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        df = df.fillna("N/A")

        table_df = df.set_index('Income Category')[value_cols].reset_index()

        table_df['% of Total Indigenous HHs'] = table_df['% of Total Indigenous HHs'].apply(format_percent)

        # Not assigning "N/A" to Area Median Household Income row
        table_df.at[0, "% of Total Indigenous HHs"] = ""

        columns = [{"name": [geo_name, "Income Category"], "id": "Income Category"}] + [
            {"name": [geo_name, col], "id": col} for col in value_cols
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-5-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Income Category', total_labels={'Area Median Household Income'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Income Category'
            ),
            style_cell_conditional=make_style_cell('Income Category', value_cols, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H4(SECTION_5_TITLE, className='table-title'),
            html.H6(TABLE_5_1_TITLE, className='table-title'),
            with_export_btn(table, 'table-5-1'),
        ], className='pg2-table-lgeo')
    

    def create_table_5_2_layout(self, geocode: int, show_both: bool = False):
        """Create Dash DataTable for Table 5.2: Households by AMHI Income (2006, 2016, 2021)."""
        df = self.data_loader.get_table('table_5_2_hh_amhi_income', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Households by AMHI Income (2006, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        df = df.fillna("N/A")

        filtered = df.copy()
        _LABEL_COL = 'Households by Income'

        dollar_mask = filtered[_LABEL_COL].str.contains('Area Median', na=False)
        for year in YEARS_MINUS_2011:
            filtered.loc[dollar_mask, year] = filtered.loc[dollar_mask, year].apply(
                lambda v: format_dollar(v)
            )
            filtered.loc[~dollar_mask, year] = filtered.loc[~dollar_mask, year].apply(
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

        median_row = []
        rows = [blank_row(_LABEL_COL, all_val_cols, _LABEL_COL)]
        for _, row in result.iterrows():
            income = row[_LABEL_COL]
            
            if income == "Area Median Household income (all HHs)":
                median_row.append(row.to_dict())
            else:
                rows.append(row.to_dict())
            
                if 'Total' in str(income):
                    rows.append(blank_row(_LABEL_COL))

        rows.extend(median_row)

        df_display = pd.DataFrame(rows, dtype=object)
    
        columns = [
            {"name": [geo_name, "", "Census Year"], "id": _LABEL_COL}
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
            id='table-5-2',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL, 
                                          section_headers={_LABEL_COL}, 
                                          total_labels={'Total', 'Area Median Household income (all HHs)'})
            ),
            style_header_conditional=generate_style_header_conditional(columns, is_multiindex=True, first_col_id=_LABEL_COL),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-5-2'),
        ], className='pg2-table-lgeo')
    

    def create_chart_5_2(self, geocode: int):
        """Create stacked bar chart for Table 5.2 Households by AMHI Income."""
        filtered = self.data_loader.get_table('table_5_2_hh_amhi_income', geocode, check_columns=YEARS_MINUS_2011)

        if filtered.empty:
            return html.Div([
                html.H4(TABLE_5_2_TITLE, className='table-title'),
                html.Div(
                "No chart for Households by AMHI Income.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs'].copy()
        hh_size_col = 'Households by Income'

        count_rows = indg[~indg[hh_size_col].isin(['Total', 'Area Median Household income (all HHs)'])].copy()

        total_rows = indg[indg[hh_size_col] == 'Total'].copy()
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        count_indexed = count_rows.set_index(hh_size_col)[YEARS_MINUS_2011]
        totals_series = (
            pd.to_numeric(total_rows[YEARS_MINUS_2011].iloc[0], errors='coerce').fillna(0)
            if not total_rows.empty else pd.Series(0.0, index=YEARS_MINUS_2011)
        )

        income_list = count_rows[hh_size_col].unique()
        colors = {t: CHART_COLORS[i % len(CHART_COLORS)] for i, t in enumerate(income_list)}

        fig = go.Figure()
        for i, income in enumerate(income_list):
            counts = pd.to_numeric(count_indexed.loc[income], errors='coerce').fillna(0)
            percentages = (
                counts / totals_series.replace(0, float('nan')) * 100
            ).fillna(0).tolist()

            fig.add_trace(go.Bar(
                name=income,
                x=YEARS_MINUS_2011,
                y=percentages,
                marker_color=colors[income],
                legendrank=len(income) - i,
                # text=[f"{p:.1f}%" for p in percentages],
                textposition='inside',
                hovertemplate=f'<b>{income}</b><br>Year: %{{x}}<br>Percentage: %{{y:.1f}}%<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=f'Indigenous Households by Income - {geo_name}', x=0.5, xanchor='center'),
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
            html.H4(TABLE_5_2_TITLE, className='table-title'),
            dcc.Graph(id='chart-5-2', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    
    def create_table_5_3_layout(self, geocode: int):
        """Create Dash DataTable for Table 5.3 with households by income by Indigenous communities."""
        df = self.data_loader.get_table('table_5_3_hh_amhi_income_breakdown', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for households by income by Indigenous communities.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = 'Households by Income'

        community_df = []
        for community in COMMUNITIES:
            indig_df = (
                df[df['Distinction'] == community]
                .set_index(_LABEL_COL)[YEARS_MINUS_2011]
                .rename(columns={y: f'{y}_{community[0]}' for y in YEARS_MINUS_2011})
            )
            community_df.append(indig_df)

        table_df = pd.concat(community_df, axis=1).reset_index()

        # Column order: year, community (2006_f, 2006_m, 2006_i, 2016_f, ...)
        val_cols = [f'{y}_{c[0]}' for y in YEARS_MINUS_2011 for c in COMMUNITIES]

        dollar_mask = table_df[_LABEL_COL].str.contains('Area Median', na=False)
        for col in val_cols:
            table_df.loc[dollar_mask, col] = table_df.loc[dollar_mask, col].apply(format_dollar)
            table_df.loc[~dollar_mask, col] = table_df.loc[~dollar_mask, col].apply(format_number)

        # Prepend section header row
        median_row = []
        rows = [blank_row(_LABEL_COL, val_cols, _LABEL_COL)]
        for _, row in table_df.iterrows():
            income = row[_LABEL_COL]
            
            if income == "Area Median Household income (all HHs)":
                median_row.append(row.to_dict())
            else:
                rows.append(row.to_dict())
            
                if 'Total' in str(income):
                    rows.append(blank_row(_LABEL_COL))

        rows.extend(median_row)

        formatted_df = pd.DataFrame(rows, dtype=object)

        # 3-level columns: [geo_name, year, community]
        columns = [{"name": [geo_name, "Census Year", ""], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()

        # Row index 8th is median household income
        formatted_df = merge_columns(formatted_df, rows=[8], value_cols=val_cols, group_size=3)

        table = dash_table.DataTable(
            id='table-5-3',
            columns=columns,
            data=formatted_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(formatted_df)
                + make_special_row_styles(formatted_df, _LABEL_COL, 
                                          section_headers={_LABEL_COL}, 
                                          total_labels={'Total', 'Area Median Household income (all HHs)'})
                + make_centered_merged_row_styles(rows=[8], value_cols=val_cols, group_size=3)
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
    
    
    
    def create_table_5_4_layout(self, geocode: int):
        """Create Dash DataTable for Table 5.4: Median Household & Per Person Income (2016, 2021)."""
        df = self.data_loader.get_table('table_5_4_median_income', geocode, check_columns=YEARS_2016_2021)

        if df.empty:
            return html.Div([
                html.H4(TABLE_5_4_TITLE, className='table-title'),
                html.Div(
                "No data for Median Household & Per Person Income (2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        result = (df.set_index('Household/person identity')[YEARS_2016_2021]
                  .reset_index()
                  .rename(columns={'Household/person identity': 'Census Year'}))
        

        for col in YEARS_2016_2021:
            result[col] = result[col].apply(format_dollar)

        rows = [blank_row('Census Year', YEARS_2016_2021, 'Median Annual Household Income')]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            tenure = row['Census Year']
            if tenure == 'Non-Indigenous household' in str(tenure):
                rows.append(blank_row('Census Year'))
                rows.append(blank_row('Census Year', YEARS_2016_2021, 'Median Annual Per Person Income'))

        table_df = pd.DataFrame(rows, dtype=object)

        columns = [{"name": [geo_name, "Census Year"], "id": "Census Year"}] + [
            {"name": [geo_name, col], "id": col} for col in YEARS_2016_2021
        ]

        section_headers = {
            'Median Annual Household Income',
            'Median Annual Per Person Income'
        }

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-5-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Census Year', section_headers=section_headers)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Census Year'
            ),
            style_cell_conditional=make_style_cell('Census Year', YEARS_2016_2021, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_5_4_TITLE, className='table-title'),
            with_export_btn(table, 'table-5-4'),
        ], className='pg2-table-lgeo')
    

    def create_table_5_5_layout(self, geocode: int, show_both: bool = False):
        """Create Dash DataTable for Table 5.5: Households by Number of Household Maintainers (2016, 2021)."""
        df = self.data_loader.get_table('table_5_5_5_6_number_hh_maintainers', geocode, 
                                        check_columns=['HHs', '% of Total'])

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Households by Number of Household Maintainers (2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = 'Households by Number of Household Maintainers'
        _HH_TYPES = [('Indigenous HHs', 'indg'), ('Non-Indigenous HHs', 'non_indg')]

        formatted_df = [
            df[(df['Household Type'] == ht) & (df['Census Year'] == year)]
            [[_LABEL_COL, 'HHs', '% of Total']]
            .set_index(_LABEL_COL)
            .rename(columns={'HHs': f'{prefix}_{year}_hhs', '% of Total': f'{prefix}_{year}_pct'})
            for ht, prefix in _HH_TYPES
            for year in YEARS_2016_2021
        ]
        result = pd.concat(formatted_df, axis=1).reset_index()

        for _, prefix in _HH_TYPES:
            for year in YEARS_2016_2021:
                result[f'{prefix}_{year}_hhs'] = result[f'{prefix}_{year}_hhs'].apply(format_number)
                result[f'{prefix}_{year}_pct'] = result[f'{prefix}_{year}_pct'].apply(format_percent)

        indg_cols = [f'indg_{y}_{m}' for y in YEARS_2016_2021 for m in ('hhs', 'pct')]
        non_indg_cols = [f'non_indg_{y}_{m}' for y in YEARS_2016_2021 for m in ('hhs', 'pct')]
        all_val_cols = indg_cols + non_indg_cols

        rows = [blank_row(_LABEL_COL, all_val_cols, _LABEL_COL)]
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            if row[_LABEL_COL] == 'Total':
                rows.append(blank_row(_LABEL_COL, all_val_cols))

        df_display = pd.DataFrame(rows, dtype=object)

        # 4-level columns: [geo_name, HH type, year, metric]
        columns = [
            {"name": [geo_name, "", "Census Year", ""], "id": _LABEL_COL}
        ] + [
            {"name": [geo_name, ht, year, metric], "id": f"{prefix}_{year}_{suffix}"}
            for ht, prefix in _HH_TYPES
            for year in YEARS_2016_2021
            for metric, suffix in [("HHs", "hhs"), ("% of Total", "pct")]
        ]

        data_cols = [_LABEL_COL] + all_val_cols
        if not show_both:
            data_cols = [_LABEL_COL] + indg_cols
            columns = [c for c in columns if c['id'] in data_cols]
        df_display = df_display[data_cols]

        base_style = get_base_table_style()
        val_cols = [c for c in data_cols if c != _LABEL_COL]

        table = dash_table.DataTable(
            id='table-5-5',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL, section_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=4
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-5-5'),
        ], className='pg2-table-lgeo')


# For testing
# if __name__ == "__main__":
#     t = Section5Prep()
#     t.create_table_5_1_layout(5915022)