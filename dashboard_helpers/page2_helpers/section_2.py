"""
Section 2 preparation and layout - Indigenous Nations / Territories and Métis Communities.
"""
import pandas as pd
from dash import dash_table, html
import dash_bootstrap_components as dbc

from .data_loader import get_data_loader
from .text_content import (
    TABLE_2_1_TITLE,
    TABLE_2_2_DESC
)
from dashboard_helpers.config import TABLE_FONT


class Section2Prep:
    """Prepare and format Section 2 layouts."""

    def __init__(self):
        self.data_loader = get_data_loader()

    ##### Table 2.1 – Indigenous Nations / Territories #####

    def _get_nations(self, geocode: int) -> list:
        """Return a deduplicated, sorted list of nation names for the geocode."""

        filtered = self.data_loader.get_table('table_2_1_indigenous_territory', geocode)

        if filtered.empty:
            return []

        nation_cols = [c for c in filtered.columns if c.lower().startswith('nation')]
        values = filtered[nation_cols].values.flatten()
        return sorted({
            str(v).strip()
            for v in values
            if pd.notna(v) and str(v).strip() != ''
        })

    def prepare_table_2_1_layout(self, geocode: int):
        """Build the Table 2.1 layout: count badge + nations DataTable."""
        nations = self._get_nations(geocode)

        nation_links = self.data_loader.get_table('table_2_1_1_nation_links')

        count = len(nations)

        count_badge = html.Div(
        f"The following {count} nations and communities have their traditional intersecting with the selected census boundary:",
        style={'fontFamily': TABLE_FONT, 'color': '#000000'}
        )

        if not nations:
            body = html.Div(
                "No data available for the selected geography.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
            )
        else:
            url_map = (
                dict(zip(nation_links['Nation'], nation_links['Nation URL']))
                if not nation_links.empty else {}
            )
            children = []
            for i, nation in enumerate(nations):
                url = url_map.get(nation)
                if url and pd.notna(url) and str(url).strip():
                    children.append(html.A(nation, href=str(url).strip(), target='_blank'))
                else:
                    children.append(html.Span(nation))
                if i < len(nations) - 1:
                    children.append(', ')
            body = html.Div(children, style={'fontFamily': TABLE_FONT, 'color': '#000000'})

        return html.Div([
            html.H4(TABLE_2_1_TITLE, className='table-title'),
            count_badge,
            body,
        ], className='pg2-table-lgeo')

    
    ##### Table 2.2 – Métis Communities #####
    def _get_metis(self, geocode: int) -> list:
        """Return a deduplicated, sorted list of Métis community names."""
        filtered = self.data_loader.get_table('table_2_2_metis_community', geocode)

        if filtered.empty:
            return []

        return sorted({
            str(v).strip()
            for v in filtered['Metis Community']
            if pd.notna(v) and str(v).strip() != ''
        })

    def prepare_table_2_2_layout(self, geocode: int):
        """Build the Table 2.2 layout: count badge + Métis communities DataTable."""
        communities = self._get_metis(geocode)

        if not communities:
            body = html.Div(
                "No data available for the selected geography.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
            )
        else:
            body = html.Div(
                f"{', '.join(communities)}",
                style={'fontFamily': TABLE_FONT, 'color': '#000000'}
            )

        return html.Div([
            html.Div(TABLE_2_2_DESC, className='table-desc'),
            body,
        ], className='pg2-table-lgeo')
