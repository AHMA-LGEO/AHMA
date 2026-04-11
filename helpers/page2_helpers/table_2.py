"""
Section 2 preparation and layout - Indigenous Nations / Territories and Métis Communities.
"""
import pandas as pd
from dash import dash_table, html
import dash_bootstrap_components as dbc

from .data_loader import Page2DataLoader
from .table_styles import (
    generate_style_data_conditional,
    get_base_table_style,
)
from .text_content import (
    TABLE_2_1_TITLE,
    TABLE_2_2_DESC
)
from helpers.config import TABLE_FONT


class Table2Prep:
    """Prepare and format Section 2 layouts."""

    def __init__(self):
        self.data_loader = Page2DataLoader()

    # ------------------------------------------------------------------
    # Section 2.1 – Indigenous Nations / Territories
    # ------------------------------------------------------------------

    def _get_nations(self, geocode: int) -> list:
        """
        Return a deduplicated, sorted list of nation names for the geocode.

        The source table is wide: one row per geocode with Nation1…Nation21
        columns
        """
        df = self.data_loader.get_table('table_2_1_indigenous_territory')
        filtered = self.data_loader.filter_by_geocode(df, geocode)

        if filtered.empty:
            return []

        nation_cols = [c for c in filtered.columns if c.lower().startswith('nation')]
        values = filtered[nation_cols].values.flatten()
        return sorted({
            str(v).strip()
            for v in values
            if pd.notna(v) and str(v).strip() != ''
        })

    def create_section_2_1_layout(self, geocode: int):
        """
        Build the Section 2.1 layout: count badge + nations DataTable.

        Args:
            geocode: Integer geographic code

        Returns:
            Dash HTML Div
        """
        nations = self._get_nations(geocode)
        count = len(nations)
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        count_badge = html.Div(
        #     [
        #     html.Span(
        #         f"{count} Indigenous Nation{'s' if count != 1 else ''} / {'Territories' if count != 1 else 'Territory'}",
        #         style={
        #             'backgroundColor': TABLE_COLORS['geography'],
        #             'color': '#FFFFFF',
        #             'fontWeight': 'bold',
        #             'fontFamily': TABLE_FONT,
        #             'padding': '6px 14px',
        #             'borderRadius': '4px',
        #             'display': 'inline-block',
        #             'marginBottom': '12px',
        #         }
        #     )
        # ]
        f"The following {count} nations and communities have their traditional intersecting with the selected census boundary:",
        style={'fontFamily': TABLE_FONT, 'color': '#000000'}
        )

        if not nations:
            body = html.Div(
                "No data available for the selected geography.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
            )
        else:
            # df_display = pd.DataFrame({'Indigenous Nation / Territory': nations})
            # base_style = get_base_table_style()
            # base_style['style_header'] = {
            #     **base_style.get('style_header', {}),
            #     'textAlign': 'left',
            #     'backgroundColor': TABLE_COLORS['geography'],
            #     'color': '#FFFFFF',
            # }
            # body = dash_table.DataTable(
            #     id='table-2-1',
            #     columns=[{'name': geo_name, 'id': 'Indigenous Nation / Territory'}],
            #     data=df_display.to_dict('records'),
            #     style_data_conditional=generate_style_data_conditional(df_display),
            #     style_cell_conditional=[{
            #         'if': {'column_id': 'Indigenous Nation / Territory'},
            #         'textAlign': 'left',
            #     }],
            #     **base_style,
            # )
            body = html.Div(
                f"{', '.join(nations)}",
                style={'fontFamily': TABLE_FONT, 'color': '#000000'}
            )

        return html.Div([
            html.H4(TABLE_2_1_TITLE, className='table-title'),
            # html.H6(TABLE_2_1_DESC, className='table-desc'),
            count_badge,
            body,
        ], className='pg2-table-lgeo')

    # ------------------------------------------------------------------
    # Section 2.2 – Métis Communities
    # ------------------------------------------------------------------

    def _get_metis(self, geocode: int) -> list:
        """Return a deduplicated, sorted list of Métis community names."""
        df = self.data_loader.get_table('table_2_2_metis_community')
        filtered = self.data_loader.filter_by_geocode(df, geocode)

        if filtered.empty:
            return []

        return sorted({
            str(v).strip()
            for v in filtered['Metis Community']
            if pd.notna(v) and str(v).strip() != ''
        })

    def create_section_2_2_layout(self, geocode: int):
        """
        Build the Section 2.2 layout: count badge + Métis communities DataTable.

        Args:
            geocode: Integer geographic code

        Returns:
            Dash HTML Div
        """
        communities = self._get_metis(geocode)
        # count = len(communities)
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        # count_badge = html.Div([
        #     html.Span(
        #         f"{count} Métis {'Communities' if count != 1 else 'Community'}",
        #         style={
        #             'backgroundColor': TABLE_COLORS['geography'],
        #             'color': '#FFFFFF',
        #             'fontWeight': 'bold',
        #             'fontFamily': TABLE_FONT,
        #             'padding': '6px 14px',
        #             'borderRadius': '4px',
        #             'display': 'inline-block',
        #             'marginBottom': '12px',
        #         }
        #     )
        # ])

        if not communities:
            body = html.Div(
                "No data available for the selected geography.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
            )
        else:
            # df_display = pd.DataFrame({'Métis Community': communities})
            # base_style = get_base_table_style()
            # base_style['style_header'] = {
            #     **base_style.get('style_header', {}),
            #     'textAlign': 'left',
            #     'backgroundColor': TABLE_COLORS['geography'],
            #     'color': '#FFFFFF',
            # }
            # body = dash_table.DataTable(
            #     id='table-2-2',
            #     columns=[{'name': geo_name, 'id': 'Métis Community'}],
            #     data=df_display.to_dict('records'),
            #     style_data_conditional=generate_style_data_conditional(df_display),
            #     style_cell_conditional=[{
            #         'if': {'column_id': 'Métis Community'},
            #         'textAlign': 'left',
            #     }],
            #     **base_style,
            # )
            body = html.Div(
                f"{', '.join(communities)}",
                style={'fontFamily': TABLE_FONT, 'color': '#000000'}
            )

        return html.Div([
            # html.H4(TABLE_2_2_TITLE, className='table-title'),
            html.Div(TABLE_2_2_DESC, className='table-desc'),
            # count_badge,
            body,
        ], className='pg2-table-lgeo')
