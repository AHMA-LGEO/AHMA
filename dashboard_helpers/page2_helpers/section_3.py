"""
Section 3 preparation and layout - Demographics.
"""
import pandas as pd
import numpy as np
from dash import dash_table, html, dcc
import plotly.graph_objects as go

from .data_loader import get_data_loader
from .table_styles import (
    blank_row,
    make_special_row_styles,
    make_style_cell,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    format_number,
    format_percent
)
from .text_content import (
    TABLE_3_1_TITLE, CHART_3_2_TITLE,
    TABLE_3_3_TITLE, TABLE_3_4_TITLE,
    TABLE_3_5_TITLE, TABLE_3_6_TITLE,
    CHART_3_6_DESC, TABLE_3_6_NOTE)

from .export_helpers import with_export_btn

from dashboard_helpers.config import (
    TABLE_FONT, CHART_COLORS, PLOT_CONFIG,
    YEARS, YEARS_MINUS_2011, COMMUNITIES)



_AGE_GROUPS_3_2_3_3 = ['0 - 14', '15 - 24', '25 - 34', '35 - 44', '45 - 54', '55 - 64', '65+']
_AGE_GROUPS_3_4 = ['Under 15', '15 - 24', '25 - 34', '35 - 44', '45 - 54', '55 - 64', '65+']
_PRIORITY_POP_GROUPS = [
            'Youth-led (under 30)', 'Senior-led (65+)', 'Single-mother-led',
            'Single-father-led', 'HH with physical limitation', 'HH with cognitive limitation',
            'HH with mental or addictions limitation', 'HH is gender diverse',
        ]

class Section3Prep:
    """Prepare and format Section 3 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def prepare_table_3_1_data(self, geocode: int) -> pd.DataFrame:

        # Determine geography level and resolve CD geocode for sections 3 & 4
        is_csd = len(str(geocode)) == 7
        cd_geocode = self.data_loader.get_region_geocode(geocode) if is_csd else geocode

        df_3_1_1 = self.data_loader.get_table('table_3_1_1_indigenous_pop', geocode)
        df_3_1_2 = self.data_loader.get_table('table_3_1_2_indigenous_age', geocode)
        df_3_1_3 = self.data_loader.get_table('table_3_1_3_indigenous_location', cd_geocode)
        df_3_1_4 = self.data_loader.get_table('table_3_1_4_indigenous_move', cd_geocode)

        def get_values(filtered_df, label_col, label_val, pct_row=False):
            """Extract year values for a specific label row with formatting."""
            row = filtered_df[filtered_df[label_col] == label_val]
            if row.empty:
                return {y: None for y in YEARS}
            vals = row[YEARS].iloc[0]
            fmt = format_percent if pct_row else format_number
            return {y: fmt(v) if pd.notna(v) else None for y, v in vals.items()}

        rows = []

        ##### Section 1: Indigenous Population (by CSD) #####
        label_col_1 = 'Indigenous Population (by CSD)'
        rows.append(blank_row('Indicator', YEARS, '__geo_header__'))
        rows.append(blank_row('Indicator', YEARS, label_col_1))
        for pop_type in ['First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']:
            rows.append({'Indicator': pop_type, **get_values(df_3_1_1, label_col_1, pop_type)})
        rows.append({'Indicator': 'TOTAL', **get_values(df_3_1_1, label_col_1, 'TOTAL')})
        rows.append(blank_row('Indicator', YEARS))

        ##### Section 2: Age Profile #####
        label_col_2 = 'Age Profile'
        for metric in ['Median Age (years)', '% Under 15 years old', '% 65 years or older']:
            rows.append({'Indicator': metric, **get_values(df_3_1_2, label_col_2, metric, pct_row=metric.startswith('%'))})
        rows.append(blank_row('Indicator', YEARS))

        ##### Section 3: Regional Indigenous Households (by CD) #####
        label_col_3 = 'Regional Indigenous Households (by CD)'
        rows.append(blank_row('Indicator', YEARS, '__cd_header__'))
        rows.append(blank_row('Indicator', YEARS, label_col_3))
        for hh_type in ['On Reserve', 'Off Reserve']:
            rows.append({'Indicator': hh_type, **get_values(df_3_1_3, label_col_3, hh_type)})
        rows.append({'Indicator': 'TOTAL', **get_values(df_3_1_3, label_col_3, 'TOTAL')})
        rows.append(blank_row('Indicator', YEARS))

        ##### Section 4: Indigenous-led HH moves (by CD) #####
        label_col_4 = 'Number of Indigenous-led HHs who have moved in last 5 years (by CD)...'
        rows.append(blank_row('Indicator', YEARS, label_col_4))
        for move_type in ['...to a Reserve from off-Reserve', '...off a Reserve']:
            rows.append({'Indicator': move_type, **get_values(df_3_1_4, label_col_4, move_type)})

        return pd.DataFrame(rows, columns=['Indicator'] + YEARS)
    

    def create_table_3_1_layout(self, geocode: int):
        """
        Create Dash DataTable layout for Table 3.1 with 2-level column headers"""
        df = self.prepare_table_3_1_data(geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        is_csd = len(str(geocode)) == 7
        cd_geocode = self.data_loader.get_region_geocode(geocode) if is_csd else geocode
        cd_name = self.data_loader.get_geography_name(int(cd_geocode)) if is_csd else geo_name

        # Replace sentinels with display text for rendering
        df_display = df.copy()
        df_display['Indicator'] = df_display['Indicator'].replace({
            '__geo_header__': geo_name,
            '__cd_header__': cd_name,
        })

        columns = [{"name": ["", ""], "id": "Indicator"}] + [
            {"name": [geo_name, y], "id": y} for y in YEARS
        ]

        base_style = get_base_table_style()
        t_3_1_section_headers = {
            'Indigenous Population (by CSD)',
            'Regional Indigenous Households (by CD)',
            'Number of Indigenous-led HHs who have moved in last 5 years (by CD)...',
        }

        table = dash_table.DataTable(
            id='table-3-1',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df, 'Indicator',
                                          geo_headers={'__geo_header__', '__cd_header__'},
                                          section_headers=t_3_1_section_headers)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Indicator'
            ),
            style_cell_conditional=make_style_cell('Indicator', YEARS, label_min_width='200px'),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_3_1_TITLE, className='table-title'),
            with_export_btn(table, 'table-3-1'),
        ], className='pg2-table-lgeo')
    

    def create_chart_3_2(self, geocode: int):
        """Create 100% stacked bar chart for Table 3.2 Indigenous vs Non-Indigenous population by age group (2021)."""
        df = self.data_loader.get_table('table_3_2_3_3_indigenous_age_group', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        age_labels = [
            '0 to 14 years', '15 to 24 years', '25 to 34 years', '35 to 44 years',
            '45 to 54 years', '55 to 64 years', '65 years and over'
        ]

        indexed = df.set_index('Age Group').reindex(_AGE_GROUPS_3_2_3_3)
        indg_pcts = pd.to_numeric(indexed['Indigenous %'], errors='coerce').fillna(0).tolist()
        non_indg_pcts = pd.to_numeric(indexed['Non-Indigenous %'], errors='coerce').fillna(0).tolist()

        fig = go.Figure()
        for i, (label, indg_pct, non_indg_pct) in enumerate(zip(age_labels, indg_pcts, non_indg_pcts)):
            fig.add_trace(go.Bar(
                name=label,
                x=['Indigenous', 'Non-Indigenous'],
                y=[indg_pct, non_indg_pct],
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                legendrank=len(age_labels) - i,
                hovertemplate=f'<b>{label}</b><br>%{{x}}<br>%{{y:.1f}}%<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f'Indigenous and Non-Indigenous Populations by Age Groups,<br>2021 Census<br>[{geo_name}]',
                x=0.5, xanchor='center'
            ),
            barmode='stack',
            yaxis=dict(title='Percentage of Population', ticksuffix='%', range=[0, 100], dtick=10, gridcolor='#E5E5E5'),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H4(CHART_3_2_TITLE, className='table-title'),
            dcc.Graph(id='chart-3-2', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')


    def create_chart_3_3(self, geocode: int):
        """Create stacked bar chart for Table 3.3 Indigenous population by identity and age group (2021)."""
        df = self.data_loader.get_table('table_3_2_3_3_indigenous_age_group', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        identity_cols = ['First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']
        identity_labels = ['First Nations', 'Métis', 'Inuk (Inuit)', 'Multiple/Other Indigenous responses']

        indexed = df.set_index('Age Group').reindex(_AGE_GROUPS_3_2_3_3)

        fig = go.Figure()
        for i, (col, label) in enumerate(zip(identity_cols, identity_labels)):
            counts = pd.to_numeric(indexed[col], errors='coerce').fillna(0).tolist()
            fig.add_trace(go.Bar(
                name=label,
                x=_AGE_GROUPS_3_2_3_3,
                y=counts,
                legendrank=len(identity_cols) - i,
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                hovertemplate=f'<b>{label}</b><br>Age: %{{x}}<br>Count: %{{y:,.0f}}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f'Indigenous Populations by Age Group & Identity,<br>2021 Census<br>[{geo_name}]',
                x=0.5, xanchor='center'
            ),
            barmode='stack',
            xaxis_title='Age Group',
            yaxis=dict(title='Population Count', gridcolor='#E5E5E5'),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H4(TABLE_3_3_TITLE, className='table-title'),
            dcc.Graph(id='chart-3-3', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_3_3_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.3: population by identity and age group (2021)."""
        df = self.data_loader.get_table('table_3_2_3_3_indigenous_age_group', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        value_cols = ['Indigenous Count', 'First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']
        display_cols = ['Indigenous', 'First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']

        table_df = (
            df.set_index('Age Group')[value_cols]
            .reindex(_AGE_GROUPS_3_2_3_3)
            .rename(columns=dict(zip(value_cols, display_cols)))
            .reset_index()
        )
        totals = table_df[display_cols].apply(pd.to_numeric, errors='coerce').sum()

        for col in display_cols:
            table_df[col] = table_df[col].apply(format_number)

        # Append total row
        total_row = pd.DataFrame([{'Age Group': 'Total', **{c: format_number(totals[c]) for c in display_cols}}])
        table_df = pd.concat([table_df, total_row], ignore_index=True)

        columns = [{"name": [geo_name, "Age Group - Census 2021"], "id": "Age Group"}] + [
            {"name": [geo_name, col], "id": col} for col in display_cols
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-3-3',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Age Group', total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Age Group'
            ),
            style_cell_conditional=make_style_cell('Age Group', display_cols, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-3-3'),
        ], className='pg2-table-lgeo')
    

    def create_chart_3_4(self, geocode: int):
        """Create stacked bar chart for Table 3.4 Indigenous population by gender (2021)."""
        df = self.data_loader.get_table('table_3_4_indigenous_age_gender', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        identity_cols = ['Men+', 'Women+']

        indexed = df.set_index('Age Group - Census 2021').reindex(_AGE_GROUPS_3_4)

        fig = go.Figure()
        for i, col in enumerate(identity_cols):
            counts = pd.to_numeric(indexed[col], errors='coerce').fillna(0).tolist()
            fig.add_trace(go.Bar(
                name=col,
                x=_AGE_GROUPS_3_4,
                y=counts,
                legendrank=len(identity_cols) - i,
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                hovertemplate=f'<b>{col}</b><br>Age: %{{x}}<br>Count: %{{y:,.0f}}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f'Indigenous Populations by Age Groups & Gender,<br>2021 Census<br>[{geo_name}]',
                x=0.5, xanchor='center'
            ),
            barmode='stack',
            xaxis_title='Age Group',
            yaxis=dict(title='Population Count', gridcolor='#E5E5E5'),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H4(TABLE_3_4_TITLE, className='table-title'),
            dcc.Graph(id='chart-3-4', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_3_4_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.4: population by gender (2021)."""
        df = self.data_loader.get_table('table_3_4_indigenous_age_gender', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        value_cols = ['Indigenous', 'Men+', 'Women+']

        table_df = (
            df.set_index('Age Group - Census 2021')[value_cols]
            .reindex(_AGE_GROUPS_3_4)
            .reset_index()
            .rename(columns={'Age Group - Census 2021': 'Age Group'})
        )

        totals = table_df[value_cols].apply(pd.to_numeric, errors='coerce').sum()

        for col in value_cols:
            table_df[col] = table_df[col].apply(format_number)

        # Append total row
        total_row = pd.DataFrame([{'Age Group': 'Total', **{c: format_number(totals[c]) for c in value_cols}}])
        table_df = pd.concat([table_df, total_row], ignore_index=True)

        columns = [{"name": [geo_name, "Age Group - Census 2021"], "id": "Age Group"}] + [
            {"name": [geo_name, col], "id": col} for col in value_cols
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-3-4',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Age Group', total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Age Group'
            ),
            style_cell_conditional=make_style_cell('Age Group', value_cols, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-3-4'),
        ], className='pg2-table-lgeo')
    

    def create_table_3_5_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.5: Priority Population (2006, 2016, 2021)."""
        df = self.data_loader.get_table('table_3_5_indigenous_priority_pop', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        _LABEL_COL = 'Number of Indigenous HHs'

        table_df = (
            df.set_index('Metric')[YEARS_MINUS_2011]
            .reindex(_PRIORITY_POP_GROUPS)
            .reset_index()
            .rename(columns={'Metric': _LABEL_COL})
        )

        for col in YEARS_MINUS_2011:
            table_df[col] = table_df[col].apply(format_number)

        # Prepend section header row
        header = pd.DataFrame([blank_row(_LABEL_COL, YEARS_MINUS_2011, _LABEL_COL)])
        table_df = pd.concat([header, table_df], ignore_index=True)

        columns = [{"name": ["", ""], "id": _LABEL_COL}] + [
            {"name": [geo_name, y], "id": y} for y in YEARS_MINUS_2011
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-3-5',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, _LABEL_COL,
                                          geo_headers={_LABEL_COL},
                                          total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, YEARS_MINUS_2011, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_3_5_TITLE, className='table-title'),
            with_export_btn(table, 'table-3-5'),
        ], className='pg2-table-lgeo')

    def create_table_3_5_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.5.1 with Priority Population by Indigenous Community (2006, 2016, 2021).:
            Level 0 - geography name
            Level 1 - census year
            Level 2 - Indigenous Community
        """
        df = self.data_loader.get_table('table_3_5_1_indigenous_priority_pop_breakdown', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        _LABEL_COL = 'Number of HHs'

        community_df = []
        for community in COMMUNITIES:
            indig_df = (
                df[df['Indigenous Community'] == community]
                .set_index('Number of Indigenous HHs')[YEARS_MINUS_2011]
                .reindex(_PRIORITY_POP_GROUPS)
                .rename(columns={y: f'{y}_{community[0]}' for y in YEARS_MINUS_2011})
            )
            community_df.append(indig_df)

        table_df = (
            pd.concat(community_df, axis=1)
            .reset_index()
            .rename(columns={'Number of Indigenous HHs': _LABEL_COL})
        )

        # Column order: year, community (2006_f, 2006_m, 2006_i, 2016_f, ...)
        val_cols = [f'{y}_{c[0]}' for y in YEARS_MINUS_2011 for c in COMMUNITIES]

        for col in val_cols:
            table_df[col] = table_df[col].apply(format_number)

        # Prepend section header row
        header = pd.DataFrame([blank_row(_LABEL_COL, val_cols, _LABEL_COL)])
        table_df = pd.concat([header, table_df], ignore_index=True)

        # 3-level columns: [geo_name, year, community]
        columns = [{"name": ["", "", ""], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-3-5-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, _LABEL_COL, geo_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-3-5-1'),
        ], className='pg2-table-lgeo')
    

    def create_chart_3_6(self, geocode: int):
        """Create donut chart for Table 3.6 Indigenous ancestry distribution (2021)."""

        df = self.data_loader.get_table('table_3_6_indigenous_pop_ancestry', geocode)
        labels = "Indigenous Ancestry, 2021"
        df = df[df[labels] != 'Total - Indigenous ancestry responses for the population in private households - 25% sample data']

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        top_labels = (df.nlargest(10, "# of People")[labels].tolist())

        text = [
            lbl if lbl in top_labels else ""
            for lbl in df[labels]
        ]

        fig = go.Figure(go.Pie(
            labels=df[labels],
            values=df["# of People"],
            marker=dict(colors=CHART_COLORS, line=dict(color="white")),
            hole=0.3,
            text=text,
            textinfo="text",
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>Count of people: %{value:,}<br>% of people: %{percent}<extra></extra>",
        ))

        fig.update_layout(
            title=dict(
                text=f"2021 Indigenous Ancestry<br><sup>{geo_name}</sup>",
                x=0.5, xanchor="center",
                font=dict(size=15, family=TABLE_FONT),
            ),
            paper_bgcolor="white",
            showlegend=False,
            margin=dict(t=90, b=40, l=20, r=20),
            height=550,

            annotations=[
                dict(
                    text="Indigenous<br>Distribution",
                    x=0.5, y=0.5,
                    font=dict(size=14, family=TABLE_FONT),
                    showarrow=False,
                    align="center"
                )
            ]
        )

        return html.Div([
            html.H4(TABLE_3_6_TITLE, className='table-title'),
            html.I(CHART_3_6_DESC),
            dcc.Graph(id='chart-3-6', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')


    def create_table_3_6_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.6: population by indigenous ancestry (2021)."""

        df = self.data_loader.get_table('table_3_6_indigenous_pop_ancestry', geocode)

        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        value_col = '# of People'
        index_col = 'Indigenous Ancestry, 2021'
        total_id = 'Total - Indigenous ancestry responses for the population in private households - 25% sample data'
        table_df = (
            df.set_index(index_col)[value_col]
            .reset_index()
        )

        table_df[value_col] = table_df[value_col].apply(format_number)

        # move total row at the bottom
        mask = table_df[index_col] == total_id
        table_df = pd.concat(
            [table_df[~mask], table_df[mask]],
            ignore_index=True
        )
        table_df.loc[table_df[index_col] == total_id, index_col] = "Total*"

        columns = [{"name": [geo_name, index_col], "id": "Indigenous Ancestry, 2021"}] + [
            {"name": [geo_name, value_col], "id": value_col} 
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-3-6',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, index_col, total_labels={'Total*'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=index_col
            ),
            style_cell_conditional=make_style_cell(index_col, value_col, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-3-6'),
            html.I(TABLE_3_6_NOTE),
        ], className='pg2-table-lgeo')
    

if __name__ == "__main__":
    t = Section3Prep()
    t.create_table_3_6_layout(5915022)
