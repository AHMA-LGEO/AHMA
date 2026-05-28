"""
Section 7 preparation and layout - Shelter Costs and Rental Market
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
    format_dollar,
)
from .text_content import (
    SECTION_7_TITLE, TABLE_7_1_TITLE,
    TABLE_7_3_TITLE, TABLE_7_3_1_TITLE,
    TABLE_7_3_2_TITLE, TABLE_7_3_3_TITLE
    )

from dashboard_helpers.config import (
    CHART_COLORS, PLOT_CONFIG, YEARS_2016_TO_2023,
    YEARS_2016_2021, YEARLY_INTERVALS_2016_TO_2023,
    TABLE_FONT
    )

from .export_helpers import with_export_btn


class Section7Prep:
    """Prepare and format Section 7 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def create_table_7_1_layout(self, geocode: int, show_both: bool = False):
        """Create Dash DataTable for Table 7.1 and 7.2: median shelter cost (2016, 2021)."""

        df = self.data_loader.get_table('table_7_1_7_2_dwelllings', geocode, check_columns=YEARS_2016_2021)

        if df.empty:
            return html.Div([
                html.H4(SECTION_7_TITLE, className='table-title'),
                html.H6(TABLE_7_1_TITLE, className='table-title'),
                html.Div(
                "No data for median shelter cost (2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df= df.fillna("N/A")
        
        _LABEL_COL = 'Households by Tenure:'
        _SECTION_HEADER = 'Median Shelter Cost of Dwelling'

        
        indg = (
            df[df['Household Type'] == 'Indigenous HHs']
            [[_LABEL_COL] + YEARS_2016_2021]
            .rename(columns={y: f'indg_{y}' for y in YEARS_2016_2021})
        )
        non_indg = (
            df[df['Household Type'] == 'Non-Indigenous HHs']
            [[_LABEL_COL] + YEARS_2016_2021]
            .rename(columns={y: f'non_indg_{y}' for y in YEARS_2016_2021})
        )

        table_df = indg.merge(non_indg, on=_LABEL_COL, how='left')

        val_cols = [f'indg_{y}' for y in YEARS_2016_2021]
        if show_both:
            val_cols += [f'non_indg_{y}' for y in YEARS_2016_2021]

        
        for col in val_cols:
            table_df[col] = table_df[col].map(format_dollar)

        
        rows = [blank_row(_LABEL_COL, val_cols, _SECTION_HEADER)]
        rows += table_df[[_LABEL_COL] + val_cols].to_dict('records')
        display_df = pd.DataFrame(rows, dtype=object)

        columns = [
            {"name": ["", "Census Year", ""], "id": _LABEL_COL}
        ] + [
            {"name": [geo_name, "Indigenous HHs", y], "id": f"indg_{y}"}
            for y in YEARS_2016_2021
        ]
        if show_both:
            columns += [
                {"name": [geo_name, "Non-Indigenous HHs", y], "id": f"non_indg_{y}"}
                for y in YEARS_2016_2021
            ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-7-1',
            columns=columns,
            data=display_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(display_df)
                + make_special_row_styles(display_df, _LABEL_COL,
                                          geo_headers={_SECTION_HEADER},
                                          total_labels={}
                                          )
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            html.H4(SECTION_7_TITLE, className='table-title'),
            html.H6(TABLE_7_1_TITLE, className='table-title'),
            with_export_btn(table, 'table-7-1'),
        ], className='pg2-table-lgeo')
    

    def create_chart_7_3_1(self, geocode: int):
        """Create pie chart for Table 7.3.1 Primary and Secondary Rental Units (2021)."""
        df = self.data_loader.get_table('table_7_3_1_rental_units', geocode, check_columns=['2021'])
        labels = "Rental Type"

        if df.empty:
            return html.Div([
                html.H4(TABLE_7_3_TITLE, className='table-title'),
                html.H6(TABLE_7_3_1_TITLE, className='table-title'),
                html.Div(
                "No chart for Primary and Secondary Rental Units (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)


        fig = go.Figure(go.Pie(
            labels=df[labels],
            values=df["2021"],
            marker=dict(colors=CHART_COLORS, line=dict(color="white")),
            # text=text,
            # textinfo="text",
            # insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>Count of people: %{value:,}<br>% of people: %{percent}<extra></extra>",
        ))

        fig.update_layout(
            title=dict(
                text=f"2021 Share of Primary and Secondary Rental Units<br><sup>{geo_name}</sup>",
                x=0.5, xanchor="center",
                font=dict(size=15, family=TABLE_FONT),
            ),
            paper_bgcolor="white",
            showlegend=False,
            margin=dict(t=90, b=40, l=20, r=20),
            height=550,
        )

        return html.Div([
            html.H4(TABLE_7_3_TITLE, className='table-title'),
            html.H6(TABLE_7_3_1_TITLE, className='table-title'),
            dcc.Graph(id='chart-7-3-1', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')

    

    def create_table_7_3_1_layout(self, geocode: int):
        """Create Dash DataTable for Table 7.3.1: Primary and Secondary Rental Units (2016, 2021)."""

        df = self.data_loader.get_table('table_7_3_1_rental_units', geocode, check_columns=YEARS_2016_2021)

        if df.empty or df.isnull().values.all():
            return html.Div([
                html.Div(
                "No data for Primary and Secondary Rental Units (2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = 'Number of primary and secondary rental units'
        _SUB_COL = 'sub_type'

        rows = (
            df.set_index('Rental Type')[YEARS_2016_2021]
            .reset_index()
            .rename(columns={'Rental Type': _SUB_COL})
        )
        rows[_SUB_COL] = rows[_SUB_COL].replace(
            {"Primary Renters": "Primary", "Secondary Renters": "Secondary"}
        )
        for col in YEARS_2016_2021:
            rows[col] = rows[col].map(format_number)

        # Label column: show on first row only to simulate a merged cell
        rows.insert(0, _LABEL_COL, '')
        rows.iloc[0, rows.columns.get_loc(_LABEL_COL)] = _LABEL_COL
        table_df = rows.reset_index(drop=True)

        columns = [
            {"name": ["", ""], "id": _LABEL_COL},
            {"name": [geo_name, ""], "id": _SUB_COL},
            {"name": [geo_name, "2016"], "id": "2016"},
            {"name": [geo_name, "2021"], "id": "2021"},
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-7-3-1',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, [_SUB_COL] + YEARS_2016_2021, label_width='40%', label_min_width='200px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-7-3-1'),
        ], className='pg2-table-lgeo')
    

    def create_chart_7_3_2(self, geocode: int):
        """Create bar chart for Table 7.3.2 Change in Average Rents."""
        df = self.data_loader.get_table('table_7_3_2_2_change_in_average_rent', geocode, 
                                        check_columns=YEARLY_INTERVALS_2016_TO_2023)

        if df.empty:
            return html.Div([
                html.H6(TABLE_7_3_2_TITLE, className='table-title'),
                html.Div(
                "No chart for Change in Average Rents between 2016 and 2023.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        fig = go.Figure()
        change_in_rent = df[YEARLY_INTERVALS_2016_TO_2023].values.tolist()[0]

        fig.add_trace(go.Bar(
            x=YEARLY_INTERVALS_2016_TO_2023,
            y=change_in_rent,
            marker_color=CHART_COLORS[0],
            customdata= df[YEARLY_INTERVALS_2016_TO_2023].applymap(format_dollar).values.flatten(),
            hovertemplate='<b>Year: %{x}</b><br>Rent Delta: %{customdata}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(text=f'Change in Average Monthly Rent($) (2016-2023) - {geo_name}', x=0.5, xanchor='center'),
            xaxis_title='Year',
            yaxis=dict(
                title='Change in Average Monthly Rent',
                tickprefix='$',
                tickformat=',.0f',
                gridcolor='#E5E5E5',
            ),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H6(TABLE_7_3_2_TITLE, className='table-desc'),
            dcc.Graph(id='chart-7-3-2', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_7_3_2_layout(self, geocode: int):
        """Create Dash DataTable for Table 7.3.2: Change in average rents between 2016 and 2023."""

        df = self.data_loader.get_table('table_7_3_2_1_average_rent', geocode, 
                                        check_columns=YEARS_2016_TO_2023)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Average rents between 2016 and 2023.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")
        _LABEL_COL = 'Statistic'

        rows = df.set_index(_LABEL_COL)[YEARS_2016_TO_2023].reset_index()

        for col in YEARS_2016_TO_2023:
            rows[col] = rows[col].map(format_dollar)

        # rows.insert(0, _LABEL_COL, '')

        table_df = rows.reset_index(drop=True)

        columns = [
            {"name": ["", ""], "id": _LABEL_COL}
        ] + [
            {"name": [geo_name, y], "id": y} for y in YEARS_2016_TO_2023
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-7-3-2',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, YEARS_2016_TO_2023, label_width='40%', label_min_width='200px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-7-3-2'),
        ], className='pg2-table-lgeo')


    def create_chart_7_3_3(self, geocode: int):
        """Create bar chart for Table 7.3.3 Change in Vacancy Rates."""
        df = self.data_loader.get_table('table_7_3_3_1_vacancy_rate', geocode, 
                                        check_columns=YEARLY_INTERVALS_2016_TO_2023)

        if df.empty:
            return html.Div([
                html.H6(TABLE_7_3_3_TITLE, className='table-title'),
                html.Div(
                "No chart for Change in Vacancy Rates between 2016 and 2023.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        fig = go.Figure()
        change_in_vacancy = df[YEARS_2016_TO_2023].values.tolist()[0]

        fig.add_trace(go.Bar(
            x=YEARS_2016_TO_2023,
            y=change_in_vacancy,
            marker_color=CHART_COLORS[0],
            customdata= df[YEARS_2016_TO_2023].applymap(lambda x: format_percent(x, precision=1)).values.flatten(),
            hovertemplate='<b>Year: %{x}</b><br>Vacancy Rate: %{customdata}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(text=f'Vacancy Rate (2016-2023) - {geo_name}', x=0.5, xanchor='center'),
            xaxis_title='Year',
            yaxis=dict(
                title='Vacancy Rate (%)',
                ticksuffix='%',
                tickformat='.0f',
                dtick=1,
                gridcolor='#E5E5E5',
            ),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
        )

        return html.Div([
            html.H6(TABLE_7_3_3_TITLE, className='table-desc'),
            dcc.Graph(id='chart-7-3-3', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_7_3_3_layout(self, geocode: int):
        """Create Dash DataTable for Table 7.3.3: Change in vacancy rates between 2016 and 2023."""

        df = self.data_loader.get_table('table_7_3_3_1_vacancy_rate', geocode, 
                                        check_columns=YEARS_2016_TO_2023)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Vacancy rates between 2016 and 2023.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")
        _LABEL_COL = 'Statistic'

        rows = df.set_index(_LABEL_COL)[YEARS_2016_TO_2023].reset_index()

        for col in YEARS_2016_TO_2023:
            rows[col] = rows[col].map(lambda x: format_percent(x, precision=1))

        # rows.insert(0, _LABEL_COL, '')

        table_df = rows.reset_index(drop=True)

        columns = [
            {"name": ["", ""], "id": _LABEL_COL}
        ] + [
            {"name": [geo_name, y], "id": y} for y in YEARS_2016_TO_2023
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-7-3-3',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, YEARS_2016_TO_2023, label_width='40%', label_min_width='200px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-7-3-3'),
        ], className='pg2-table-lgeo')


# For testing
# if __name__ == '__main__':
#     s = Section7Prep()
#     s.create_table_7_1_layout(5915022)