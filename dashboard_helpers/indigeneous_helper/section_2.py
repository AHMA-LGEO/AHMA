"""
Section 2 preparation and layout - Indigenous Nations / Territories and Métis Communities.
"""
import re
import pandas as pd
from dash import html, dcc

from dashboard_helpers.content_helpers.data_loader import get_data_loader
from dashboard_helpers.content_helpers.text_content import (
    TABLE_2_1_TITLE,
    TABLE_2_2_DESC,
    TABLE_2_1_P1,
    TABLE_2_1_P2,
    TABLE_2_1_P3,
    TABLE_2_1_P4,
    TABLE_2_1_NOTE,
    SECTION_2_P1,
    SECTION_2_P2,
    SECTION_2_LINK_1,
    SECTION_2_LINK_2,
    SECTION_2_LINK_3,
    SECTION_2_NOTE_P1,
    SECTION_2_NOTE_P2,
    SECTION_2_NOTE_P3
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

        count_badge = html.P(
            f"The following {count} nations and communities have their traditional territories intersecting with the selected census boundary:",
            style={'fontFamily': TABLE_FONT, 'color': '#000000', 'fontWeight': 'bold'}
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
            html.Div([
                html.P(TABLE_2_1_P1),
                html.P(TABLE_2_1_P2),
                html.P(TABLE_2_1_P3),
                html.P(TABLE_2_1_P4),
                html.I(TABLE_2_1_NOTE)
            ], className="pg2-text-content-lgeo"),
            html.Br(),
            count_badge,
            body
        ], className='pg2-table-lgeo')

    
    ##### Table 2.2 – Métis Communities #####
    def _get_metis(self, geocode: int) -> list:
        """Return a deduplicated, sorted list of Métis community names."""
        filtered = self.data_loader.get_table('table_2_2_metis_community', geocode)

        if filtered.empty:
            return []

        return sorted({
            re.sub(r',\s*', ', ', str(v)).strip()
            for v in filtered['Metis Community']
            if pd.notna(v) and str(v).strip()
        })

    def prepare_table_2_2_layout(self, geocode: int):
        """Build the Table 2.2 layout: count badge + Métis communities DataTable."""
        communities = self._get_metis(geocode)

        if not communities:
            body = html.Div(
                "No data available for the selected geography.",
                style={'fontFamily': TABLE_FONT, 'color': '#666', 'padding-bottom': '1.5rem'}
            )
        else:
            body = html.Div(
                # f"{', '.join(communities)}",
                ', '.join(map(str.strip, communities)),
                style={'fontFamily': TABLE_FONT, 'color': '#000000', 'padding-bottom': '1.5rem'}
            )

        return html.Div([
            html.P(TABLE_2_2_DESC, className='table-desc', 
                   style={'fontFamily': TABLE_FONT, 'color': '#000000', 'fontWeight': 'bold'}),
            body,
            html.Br(),
            html.Div([
                html.P(SECTION_2_P1, style={'fontFamily': TABLE_FONT, 'color': '#000000', 'fontWeight': 'bold'}),
                html.P(SECTION_2_P2),
                html.Div(dcc.Markdown(SECTION_2_LINK_1)),
                html.Div(dcc.Markdown(SECTION_2_LINK_2)),
                html.Div(dcc.Markdown(SECTION_2_LINK_3)),
                html.Br(),
                html.I(dcc.Markdown(SECTION_2_NOTE_P1), style={'fontFamily': TABLE_FONT, 'color': '#000000', 'fontWeight': 'bold'}),
                html.I(dcc.Markdown(SECTION_2_NOTE_P2)),
                html.I(dcc.Markdown(SECTION_2_NOTE_P3)),
            ], className="pg2-text-content-lgeo")
        ], className='pg2-table-lgeo')
