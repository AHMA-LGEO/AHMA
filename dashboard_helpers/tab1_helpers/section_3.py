"""
Section 3 preparation and layout - Demographics.
"""
import pandas as pd
from dash import dash_table, html, dcc
import plotly.graph_objects as go

from dashboard_helpers.content_helpers.data_loader import get_data_loader
from dashboard_helpers.content_helpers.table_styles import (
    blank_row,
    make_special_row_styles,
    make_style_cell,
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    format_number,
    format_percent,
    make_data_table)
from ..content_helpers.text_content import (
    SECTION_3_TITLE, SECTION_3_P1, SECTION_3_NOTE,
    TABLE_3_1_TITLE, TABLE_3_1_DESC, 
    CHART_3_2_TITLE, CHART_3_2_DESC,
    TABLE_3_3_TITLE, CHART_3_3_DESC, TABLE_3_3_DESC, TABLE_3_3_NOTE,
    TABLE_3_4_TITLE, CHART_3_4_DESC, CHART_3_4_NOTE, TABLE_3_4_DESC,
    TABLE_3_5_TITLE, 
    TABLE_3_6_TITLE, CHART_3_6_DESC, TABLE_3_6_DESC, TABLE_3_6_NOTE,
    CHART_3_6_NOTE)

from ..content_helpers.export_helpers import with_export_btn

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

        df_3_1_1 = self.data_loader.get_table('table_3_1_1_indigenous_pop', geocode, check_columns=YEARS)
        df_3_1_2 = self.data_loader.get_table('table_3_1_2_indigenous_age', geocode, check_columns=YEARS)
        df_3_1_3 = self.data_loader.get_table('table_3_1_3_indigenous_location', cd_geocode, check_columns=YEARS)
        df_3_1_4 = self.data_loader.get_table('table_3_1_4_indigenous_move', cd_geocode, check_columns=YEARS)

        def get_values(filtered_df, label_col, label_val, pct_row=False):
            """Extract year values for a specific label row with formatting."""
            if filtered_df.empty or label_col not in filtered_df.columns:
                return {y: None for y in YEARS}
            row = filtered_df[filtered_df[label_col] == label_val]
            if row.empty:
                return {y: None for y in YEARS}
            vals = row[YEARS].iloc[0]
            fmt = format_percent if pct_row else format_number
            return {y: fmt(v) if pd.notna(v) else None for y, v in vals.items()}

        rows = []

        ##### Section 1: Indigenous Population (by CSD) #####
        label_col_1 = 'Indigenous Population'
        rows.append(blank_row('Indicator', YEARS, '__geo_header__'))
        rows.append(blank_row('Indicator', YEARS, label_col_1))
        for pop_type in ['First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']:
            rows.append({'Indicator': pop_type, **get_values(df_3_1_1, label_col_1, pop_type)})
        rows.append({'Indicator': 'Total', **get_values(df_3_1_1, label_col_1, 'Total')})
        # rows.append(blank_row('Indicator', YEARS))

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
        rows.append({'Indicator': 'Total', **get_values(df_3_1_3, label_col_3, 'Total')})
        # rows.append(blank_row('Indicator', YEARS))

        ##### Section 4: Indigenous-led HH moves (by CD) #####
        label_col_4 = 'Number of Indigenous-led HHs who have moved in last 5 years (by CD)'
        rows.append(blank_row('Indicator', YEARS, label_col_4))
        for move_type in ['...to a Reserve from off-Reserve', '...off a Reserve']:
            rows.append({'Indicator': move_type, **get_values(df_3_1_4, label_col_4, move_type)})

        return pd.DataFrame(rows, columns=['Indicator'] + YEARS)
    

    def create_table_3_1_layout(self, geocode: int):
        """
        Create Dash DataTable layout for Table 3.1 with 2-level column headers"""
        df = self.prepare_table_3_1_data(geocode)

        if df.empty:
            return html.Div([
                html.H4(SECTION_3_TITLE, className='table-title'),
                html.Div([
                    html.P(SECTION_3_P1),
                    html.I(SECTION_3_NOTE)
                ], className="pg2-text-content-lgeo"),
                html.H5(TABLE_3_1_TITLE, className='table-title'),
                html.Div(
                "No data for Population and Age Distribution for Indigenous Population (2006, 2011, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')
    
        df = df.fillna("N/A")

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        is_csd = len(str(geocode)) == 7
        cd_geocode = self.data_loader.get_region_geocode(geocode) if is_csd else geocode
        cd_name = self.data_loader.get_geography_name(int(cd_geocode)) if is_csd else geo_name

        base_style = get_base_table_style()
        t_3_1_section_headers = {
            'Indigenous Population',
            'Regional Indigenous Households (by CD)',
            'Number of Indigenous-led HHs who have moved in last 5 years (by CD)',
        }

        # Split at the CD banner so each half carries its own export button: the
        # CSD half ends at '% 65 years or older', the CD half runs from the CD
        # banner through '...off a Reserve'.
        cd_matches = df.index[df['Indicator'] == '__cd_header__']
        cd_idx = int(cd_matches[0]) if len(cd_matches) else len(df)

        def _split(start, stop):
            """Slice the sentinel df and drop trailing spacer rows."""
            sub = df.iloc[start:stop]
            while len(sub) and sub.iloc[-1]['Indicator'] == '':
                sub = sub.iloc[:-1]
            return sub.reset_index(drop=True)

        def _build(table_id, sub_df, cols, header_styles):
            disp = sub_df.copy()
            disp['Indicator'] = disp['Indicator'].replace({
                '__geo_header__': geo_name,
                '__cd_header__': cd_name,
            })
            return make_data_table(
                id=table_id,
                columns=cols,
                data=disp.to_dict('records'),
                merge_duplicate_headers=True,
                style_data_conditional=(
                    generate_style_data_conditional(disp)
                    + make_special_row_styles(sub_df, 'Indicator',
                                              col_headers={'__geo_header__', '__cd_header__'},
                                              section_headers=t_3_1_section_headers)
                ),
                style_header_conditional=header_styles,
                style_cell_conditional=make_style_cell('Indicator', YEARS, label_min_width='200px'),
                **base_style
            )

        # CSD half: geography banner sitting over the census-year row.
        csd_cols = [{"name": [geo_name, "Census Year"], "id": "Indicator"}] + [
            {"name": [geo_name, y], "id": y} for y in YEARS
        ]
        csd_table = _build(
            'table-3-1', _split(0, cd_idx), csd_cols,
            generate_style_header_conditional(
                csd_cols, is_multiindex=True, first_col_id='Indicator', n_header_rows=2,
                left_align_cells={'column_id': 'Indicator', 'header_index': 1}
            ),
        )

        # CD half: single header row where the CD name takes the 'Census Year'
        # slot, so the geography banner and the CD label row both drop out.
        cd_cols = [{"name": cd_name, "id": "Indicator"}] + [
            {"name": y, "id": y} for y in YEARS
        ]
        cd_table = _build(
            'table-3-1-cd', _split(cd_idx + 1, len(df)), cd_cols,
            generate_style_header_conditional(cd_cols, is_multiindex=False,
                                              first_col_id='Indicator')
            + [{'if': {'header_index': 0, 'column_id': 'Indicator'},
                'textAlign': 'left', 'paddingLeft': '12px',
                'backgroundColor': '#80885B'}],
        )

        return html.Div([
            html.H4(SECTION_3_TITLE, className='table-title'),
            html.Div([
                html.P(SECTION_3_P1),
                html.I(SECTION_3_NOTE)
            ], className="pg2-text-content-lgeo"),
            html.H5(TABLE_3_1_TITLE, className='table-title'),
            html.Div([html.P(TABLE_3_1_DESC)], className="pg2-text-content-lgeo"),
            with_export_btn(csd_table, 'table-3-1',
                            title=f'Indigenous Populations and Ages - {geo_name}'),
            html.Br(),
            with_export_btn(cd_table, 'table-3-1-cd',
                            title=f'Indigenous Movement On-/Off Reserve Over Time - {cd_name}'),
        ], className='pg2-table-lgeo')
    

    def create_chart_3_2(self, geocode: int):
        """Create 100% stacked bar chart for Table 3.2 Indigenous vs Non-Indigenous population by age group (2021)."""
        df = self.data_loader.get_table('table_3_2_3_3_indigenous_age_group', geocode, 
                                        check_columns=['Indigenous %', 'Non-Indigenous %'])

        if df.empty:
            return html.Div([
                html.H5(CHART_3_2_TITLE, className='table-title'),
                html.Div(
                "No chart for Indigenous vs Non-Indigenous population by age group (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

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
            
            color = CHART_COLORS[i % len(CHART_COLORS)]
            # Build hoverlabel dict conditionally
            hoverlabel = dict(namelength=-1)
            if color == '#80875C':
                hoverlabel['font'] = dict(color='white')

            fig.add_trace(go.Bar(
                name=label,
                x=['Indigenous', 'Non-Indigenous'],
                y=[indg_pct, non_indg_pct],
                marker_color=color,
                legendrank=len(age_labels) - i,
                hoverlabel=hoverlabel,
                hovertemplate=f'<b>{label}</b><br>%{{x}}<br>%{{y:.1f}}%<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f'Indigenous and Non-Indigenous Populations by Age Groups,<br>2021 Census<br>{geo_name}',
                x=0.5, xanchor='center'
            ),
            barmode='stack',
            bargap=0.5,
            yaxis=dict(title='Percentage of Population', ticksuffix='%', range=[0, 100], dtick=10, gridcolor='#E5E5E5'),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            dragmode=False,
        )

        return html.Div([
            html.H5(CHART_3_2_TITLE, className='table-title'),
            html.Div([html.P(CHART_3_2_DESC)], className='pg2-text-content-lgeo'),
            html.Div(
                dcc.Graph(id='chart-3-2', figure=fig, config=PLOT_CONFIG, style={'height': '500px', 'width': '100%'},),
                # Only 2 bars (Indigenous / Non-Indigenous) - full page width is wasted space.
                style={'maxWidth': '1000px', 'margin': '0 auto'}
            )
        ], className='pg2-table-lgeo')


    def create_chart_3_3(self, geocode: int):
        """Create stacked bar chart for Table 3.3 Indigenous population by identity and age group (2021)."""

        identity_cols = ['First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']
        identity_labels = ['First Nations', 'Métis', 'Inuk (Inuit)', 'Multiple/Other Indigenous responses']

        df = self.data_loader.get_table('table_3_2_3_3_indigenous_age_group', geocode, check_columns=identity_cols)

        if df.empty:
            return html.Div([
                html.H5(TABLE_3_3_TITLE, className='table-title'),
                html.Div(
                "No chart for population by identity and age group (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        
        chart_age_groups = ['Under 15' if age == '0 - 14' else age for age in _AGE_GROUPS_3_2_3_3]
        indexed = df.replace("0 - 14", "Under 15").set_index('Age Group').reindex(chart_age_groups)

        fig = go.Figure()
        for i, (col, label) in enumerate(zip(identity_cols, identity_labels)):
            counts = pd.to_numeric(indexed[col], errors='coerce').fillna(0).tolist()
            fig.add_trace(go.Bar(
                name=label,
                x=chart_age_groups,
                y=counts,
                legendrank=-(i + 1),
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                hovertemplate=f'<b>{label}</b><br>Age: %{{x}}<br>Count: %{{y:,.0f}}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f'Indigenous Populations by Age Group & Identity,<br>2021 Census<br>{geo_name}',
                x=0.5, xanchor='center'
            ),
            barmode='stack',
            xaxis_title='Age Group',
            yaxis=dict(title='Population Count', gridcolor='#E5E5E5'),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            dragmode=False,
        )

        return html.Div([
            html.H5(TABLE_3_3_TITLE, className='table-title'),
            html.Div([html.P(CHART_3_3_DESC)], className='pg2-text-content-lgeo'),
            dcc.Graph(id='chart-3-3', figure=fig, config=PLOT_CONFIG, style={'height': '500px', 'width': '100%'},)
        ], className='pg2-table-lgeo')
    

    def create_table_3_3_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.3: population by identity and age group (2021)."""
        value_cols = ['Indigenous Count', 'First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']
        display_cols = ['Indigenous', 'First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']
        
        df = self.data_loader.get_table('table_3_2_3_3_indigenous_age_group', geocode, check_columns=value_cols)

        if df.empty or df.isnull().values.all():
            return html.Div([
                html.Div(
                "No data for population by identity and age group (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        table_df = (
            df.set_index('Age Group')[value_cols]
            .reindex(_AGE_GROUPS_3_2_3_3)
            .rename(columns=dict(zip(value_cols, display_cols)))
            .reset_index()
            .replace("0 - 14", "Under 15")
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

        table = make_data_table(
            id='table-3-3',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Age Group', total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Age Group',
                left_align_cells={'column_id': 'Age Group', 'header_index': 1}
            ),
            style_cell_conditional=make_style_cell('Age Group', display_cols, label_width='10%'),
            **base_style
        )

        return html.Div([
            html.Div([html.P(TABLE_3_3_DESC)], className='pg2-text-content-lgeo'),
            html.Div(with_export_btn(table, 'table-3-3',
                            title=f'Population by Indigenous Identity & Age Group - {geo_name}'),
                            className="d-flex flex-column align-items-center w-100"
                            ),
            html.Div(html.I(TABLE_3_3_NOTE), 
                                 className="d-flex flex-column align-items-center w-100"),
                                #  className="d-flex flex-column align-items-left w-100"
        ], className='pg2-table-lgeo')
    

    def create_chart_3_4(self, geocode: int):
        """Create stacked bar chart for Table 3.4 Indigenous population by gender (2021)."""
        identity_cols = ['Indigenous Men+', 'Indigenous Women+']

        df = self.data_loader.get_table('table_3_4_indigenous_age_gender', geocode, check_columns=identity_cols)

        if df.empty:
            return html.Div([
                html.H5(TABLE_3_4_TITLE, className='table-title'),
                html.Div(
                "No chart for Indigenous population by gender (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

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
                text=f'Indigenous Populations by Age Groups & Gender,<br>2021 Census<br>{geo_name}',
                x=0.5, xanchor='center'
            ),
            barmode='stack',
            xaxis_title='Age Group',
            yaxis=dict(title='Population Count', gridcolor='#E5E5E5'),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            dragmode=False,
        )

        return html.Div([
            html.H5(TABLE_3_4_TITLE, className='table-title'),
            html.Div([html.P(CHART_3_4_DESC),
                      html.I(CHART_3_4_NOTE)], className='pg2-text-content-lgeo'),
            dcc.Graph(id='chart-3-4', figure=fig, config=PLOT_CONFIG, style={'height': '500px', 'width': '100%'},)
        ], className='pg2-table-lgeo')
    

    def create_table_3_4_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.4: population by gender (2021)."""
        value_cols = ['Indigenous', 'Indigenous Men+', 'Indigenous Women+']
        
        df = self.data_loader.get_table('table_3_4_indigenous_age_gender', geocode, check_columns=value_cols)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for population by gender (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')
        
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

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

        table = make_data_table(
            id='table-3-4',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Age Group', total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Age Group', n_header_rows=2,
                left_align_cells={'column_id': 'Age Group', 'header_index': 1}
            ),
            style_cell_conditional=make_style_cell('Age Group', value_cols, 
                                                   label_width='10%'),
            **base_style
        )

        return html.Div([
            html.Div([html.P(TABLE_3_4_DESC)], className='pg2-text-content-lgeo'),
            with_export_btn(table, 'table-3-4',
                            title=f'Population by Gender & Age Group - {geo_name}'),
        ], className='pg2-table-lgeo')
    

    def create_table_3_5_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.5: Priority Population (2006, 2016, 2021)."""
        df = self.data_loader.get_table('table_3_5_indigenous_priority_pop', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.H5(TABLE_3_5_TITLE, className='table-title'),
                html.Div(
                "No data for Priority Population (2006, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

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

        columns = [{"name": [geo_name, "Census Year"], "id": _LABEL_COL}] + [
            {"name": [geo_name, y], "id": y} for y in YEARS_MINUS_2011
        ]

        base_style = get_base_table_style()

        table = make_data_table(
            id='table-3-5',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, _LABEL_COL,
                                          section_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=2,
                left_align_cells={'column_id': _LABEL_COL, 'header_index': 1}
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, YEARS_MINUS_2011, 
                                                   label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H5(TABLE_3_5_TITLE, className='table-title'),
            with_export_btn(table, 'table-3-5',
                            title=f'Priority Population - {geo_name}'),
        ], className='pg2-table-lgeo')

    def create_table_3_5_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.5.1 with Priority Population by Indigenous Community (2006, 2016, 2021).:
            Level 0 - geography name
            Level 1 - census year
            Level 2 - Indigenous Community
        """
        df = self.data_loader.get_table('table_3_5_1_indigenous_priority_pop_breakdown', geocode,
                                        check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Priority Population by Indigenous Community (2006, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

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
        columns = [{"name": [geo_name, "", "Census Year"], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()

        table = make_data_table(
            id='table-3-5-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, _LABEL_COL, section_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL,
                left_align_cells={'column_id': _LABEL_COL, 'header_index': 2}
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='25%', 
                                                   label_min_width='120px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-3-5-1',
                            title=f'Priority Population by Indigenous Identity - {geo_name}'),
        ], className='pg2-table-lgeo')
    

    def _get_table_3_6_data(self, geocode: int):
        """
        Load table 3.6, falling back to the parent CD when a CSD is selected.

        Ancestry is only published at the CD level - CSD rows exist but carry no
        values - so a CSD selection would otherwise render nothing. Returns the
        data alongside the geography name it actually belongs to, so the chart
        title and table header never label CD figures as the CSD's.
        """
        _VAL_COL = "# of People"
        name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = self.data_loader.get_table('table_3_6_indigenous_pop_ancestry', geocode)

        has_data = not df.empty and df[_VAL_COL].notna().any()
        is_csd = len(str(geocode)) == 7
        if has_data or not is_csd:
            return df, name

        cd_geocode = self.data_loader.get_region_geocode(geocode)
        if not cd_geocode:
            return df, name

        cd_df = self.data_loader.get_table('table_3_6_indigenous_pop_ancestry', cd_geocode)
        if cd_df.empty or cd_df[_VAL_COL].isna().all():
            return df, name

        cd_name = self.data_loader.get_geography_name(int(cd_geocode)) or str(cd_geocode)
        return cd_df, cd_name

    def create_chart_3_6(self, geocode: int):
        """Create donut chart for Table 3.6 Indigenous ancestry distribution (2021)."""

        df, geo_name = self._get_table_3_6_data(geocode)
        if df.empty or df["# of People"].isna().all():
            return html.Div([
                html.H5(TABLE_3_6_TITLE, className='table-title'),
                html.Div(
                "No distribution chart available for Indigenous ancestry distribution (2021) for the selected geography.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        labels = "Indigenous Ancestry, 2021"
        df = df[df[labels] != 'Total - Indigenous ancestry responses for the population in private households - 25% sample data']

        # to assign the largest portion the first chart color and so on
        df_sorted = df.sort_values("# of People", ascending=False) 
        top_labels = (df_sorted.nlargest(5, "# of People")[labels].tolist())

        text = [
            lbl if lbl in top_labels else ""
            for lbl in df_sorted[labels]
        ]
        # white_hover_color = "#80875C" in CHART_COLORS

        # Only set font color if #80875C is used
        # hoverlabel = dict(namelength=-1)
        # if white_hover_color:
        #     hoverlabel['font'] = dict(color='white')

        fig = go.Figure(go.Pie(
            labels=df_sorted[labels],
            values=df_sorted["# of People"],
            # marker=dict(colors=color, line=dict(color="white")),
            marker=dict(colors=CHART_COLORS),
            hole=0.3,
            text=text,
            textinfo="text",
            # hoverlabel=hoverlabel,
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>Count of people: %{value:,}<br>% of people: %{percent}<extra></extra>",
            sort=False,
            domain=dict(x=[0.30, 1.0]) 
        ))

        fig.update_layout(
            title=dict(
                text=f"2021 Indigenous Ancestry<br><sup>{geo_name}</sup>",
                x=0.5, xanchor="center",
                # font=dict(size=15, family=TABLE_FONT),
            ),
            paper_bgcolor="white",
            showlegend=False,
            margin=dict(t=90, b=40, l=40, r=20),
            height=550,
            dragmode=False,

            annotations=[
                dict(
                    text="Indigenous<br>Distribution",
                    x=0.65, y=0.5,
                    font=dict(size=14, family=TABLE_FONT),
                    showarrow=False,
                    align="center"
                )
            ]
        )

        return html.Div([
            html.H5(TABLE_3_6_TITLE, className='table-title'),
            html.Div([html.P(CHART_3_6_DESC),
                      html.I(CHART_3_6_NOTE)], className='pg2-text-content-lgeo'),
            dcc.Graph(id='chart-3-6', figure=fig, config=PLOT_CONFIG, style={'height': '550px', 'width': '100%'},)
        ], className='pg2-table-lgeo')


    def create_table_3_6_layout(self, geocode: int):
        """Create Dash DataTable for Table 3.6: population by indigenous ancestry (2021)."""

        df, geo_name = self._get_table_3_6_data(geocode)

        if df.empty or df["# of People"].isna().all():
            return html.Div([
                html.Div(
                "No data available for Indigenous ancestry distribution (2021) for the selected geography.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        df = df.fillna("N/A")

        value_col = '# of People'
        index_col = 'Indigenous Ancestry, 2021'
        total_id = 'Total - Indigenous ancestry responses for the population in private households - 25% sample data'
        table_df = (
            df.set_index(index_col)[value_col]
            .sort_index(ascending=True)
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

        table = make_data_table(
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
            style_cell_conditional=make_style_cell(index_col, [value_col],
                                                   label_width='65%'),
            # style_table={'maxWidth': '600px'},
            # **base_style
            style_table={
                **base_style.get('style_table', {}), 
                'maxWidth': '600px',
                'width': '100%' 
            },
             **{k: v for k, v in base_style.items() if k != 'style_table'}
        )

        return html.Div([
            html.Div([html.P(TABLE_3_6_DESC)], className='pg2-text-content-lgeo'),
            html.Div(
                with_export_btn(table, 'table-3-6', max_width='600px',
                            title=f'Population by Indigenous Ancestry (2021) - {geo_name}'),
                className="d-flex flex-column align-items-center w-100"
            ),
            html.Div(
                html.I(TABLE_3_6_NOTE),
                className="d-flex flex-column align-items-center w-100"
            ),
        ], className='pg2-table-lgeo')
    

# For testing
# if __name__ == "__main__":
#     t = Section3Prep()
#     t.create_table_3_6_layout(5915022)
