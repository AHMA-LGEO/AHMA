"""
Table 8.1 preparation and layout - Core Housing Need Indicators.
"""
import pandas as pd
from dash import dash_table, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from .data_loader import DataLoader
from .table_styles import (
    generate_style_data_conditional,
    generate_style_header_conditional,
    get_base_table_style,
    get_special_row_styles_8_1,
    style_cell_8_1,
    format_number,
    format_percent,
    _T8_BELOW_MULTIPLE,
    _T8_TOTAL,
)
from .text_content import TABLE_8_1_TITLE, TABLE_8_1_DESC
from helpers.config import CHART_COLORS, TABLE_COLORS, TABLE_FONT

YEAR_COLS = ['2006', '2016', '2021']

# Fixed display order for indicators
INDICATOR_ORDER = [
    "Affordability (Households paying >30% of income on shelter)",
    "Adequacy (Households living in dwellings needing Major Repairs)",
    "Suitability (Households living in overcrowded dwellings)",
    _T8_BELOW_MULTIPLE,
    "Acceptable Housing (Affordable, Adequate, and Suitable)",
    "Total households (for reference)",
]

# Labels used in the outer ring of the wedge-pie chart
CHART_DETAIL_LABELS = [
    "Unaffordability",
    "Inadequacy",
    "Unsuitability",
    "Below multiple <br>indicators",
]
CHART_DETAIL_INDICATORS = INDICATOR_ORDER[:4]   # matches labels above

# Colours for the pie chart, updating the following logic for clear understanding of categories
# _PIE_ACCEPTABLE_COLOR = CHART_COLORS[0] # choosing 1st chart color
_PIE_ACCEPTABLE_COLOR = "#9CA37A"
# _PIE_OUTER_COLORS = [CHART_COLORS[i] for i in range(1,5)]
_PIE_OUTER_COLORS = ["#D89A86", "#C97A63", "#b55438", "#5b2a1c"]


class Section8Prep:
    def __init__(self):
        self.data_loader = DataLoader()

    def prepare_table_8_1_data(self, geocode: int) -> pd.DataFrame:
        """
        Pivot raw table_8_1_core_housing_need into display format.
        """
        df = self.data_loader.get_table('table_8_1_core_housing_need')
        filtered = self.data_loader.filter_by_geocode(df, geocode)

        if filtered.empty:
            return pd.DataFrame()

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs']
        non_indg = filtered[filtered['Household Type'] == 'Non-Indigenous HHs']

        indg_cols = [f'indg_{y}' for y in YEAR_COLS]
        non_indg_cols = [f'non_indg_{y}' for y in YEAR_COLS]
        all_val_cols = indg_cols + non_indg_cols

        def blank_row(label=''):
            return {'Indicator': label, **{c: '' for c in all_val_cols}}

        def _lookup(subset, indicator, metric):
            mask = (subset['Indicator'] == indicator) & (subset['Metric'] == metric)
            row = subset[mask]
            return row.iloc[0] if not row.empty else None

        rows = []
        for indicator in INDICATOR_ORDER:
            indg_count = _lookup(indg, indicator, 'Number of households')
            indg_pct = _lookup(indg, indicator, '% of households')
            non_indg_count = _lookup(non_indg, indicator, 'Number of households')
            non_indg_pct = _lookup(non_indg, indicator, '% of households')

            if indicator == _T8_TOTAL:
                # Single bold row: indicator name + count values inline, no % row
                total_row = {'Indicator': indicator}
                for y in YEAR_COLS:
                    total_row[f'indg_{y}'] = (
                        format_number(indg_count[y]) if indg_count is not None else 'NA'
                    )
                    total_row[f'non_indg_{y}'] = (
                        format_number(non_indg_count[y]) if non_indg_count is not None else 'NA'
                    )
                rows.append(total_row)
                rows.append(blank_row())
                continue

            # Section header row
            rows.append(blank_row(indicator))

            # Number of households row
            count_row = {'Indicator': 'Number of households'}
            for y in YEAR_COLS:
                count_row[f'indg_{y}'] = (
                    format_number(indg_count[y]) if indg_count is not None else 'NA'
                )
                count_row[f'non_indg_{y}'] = (
                    format_number(non_indg_count[y]) if non_indg_count is not None else 'NA'
                )
            if indicator == _T8_BELOW_MULTIPLE:
                count_row['Indicator'] = '__below_count__'
            rows.append(count_row)

            # % of households row
            pct_row = {'Indicator': '% of households'}
            for y in YEAR_COLS:
                pct_row[f'indg_{y}'] = (
                    format_percent(indg_pct[y]) if indg_pct is not None else 'NA'
                )
                pct_row[f'non_indg_{y}'] = (
                    format_percent(non_indg_pct[y]) if non_indg_pct is not None else 'NA'
                )
            if indicator == _T8_BELOW_MULTIPLE:
                pct_row['Indicator'] = '__below_pct__'
            rows.append(pct_row)

            # Blank separator
            rows.append(blank_row())

        return pd.DataFrame(rows, dtype=object)

    def create_table_8_1_layout(self, geocode: int, show_both: bool = False):
        """
        Create Dash DataTable for Table 8.1 with 3-level column headers:
            Level 0 – geography name
            Level 1 – Indigenous HHs | Non-Indigenous HHs (toggled)
            Level 2 – census year

        Args:
            geocode:   Geographic code
            show_both: If True, include Non-Indigenous columns

        Returns:
            Dash HTML Div
        """
        df = self.prepare_table_8_1_data(geocode)
        if df.empty:
            return html.Div("No data available", className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        columns = [
            {"name": ["", "Indicator", ""], "id": "Indicator"}
        ] + [
            {"name": [geo_name, "Indigenous HHs", y], "id": f"indg_{y}"}
            for y in YEAR_COLS
        ]
        if show_both:
            columns += [
                {"name": [geo_name, "Non-Indigenous HHs", y], "id": f"non_indg_{y}"}
                for y in YEAR_COLS
            ]

        data_cols = ['Indicator'] + [f'indg_{y}' for y in YEAR_COLS]
        if show_both:
            data_cols += [f'non_indg_{y}' for y in YEAR_COLS]

        # Replace internal tags back to display text for the DataTable
        df_display = df[data_cols].copy()
        df_display['Indicator'] = df_display['Indicator'].replace({
            '__below_count__': 'Number of households',
            '__below_pct__': '% of households',
        })

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-8-1',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + get_special_row_styles_8_1(df)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Indicator'
            ),
            style_cell_conditional=style_cell_8_1(show_both),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_8_1_TITLE, className='table-title'),
            html.H6(TABLE_8_1_DESC, className='table-desc'),
            dbc.Button("Export", id="export-table-8-1", className="export-pdf"),
            table
        ], className='pg2-table-lgeo')


    def create_chart_8_1(self, geocode: int):
        """
        Sunburst (nested-pie) chart for 2021 Indigenous Core Housing Need.
        """
        df = self.data_loader.get_table('table_8_1_core_housing_need')
        filtered = self.data_loader.filter_by_geocode(df, geocode)

        if filtered.empty:
            return go.Figure()

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs']
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        def _pct(indicator):
            mask = (indg['Indicator'] == indicator) & (indg['Metric'] == '% of households')
            row = indg[mask]
            if row.empty:
                return 0.0
            try:
                return float(row['2021'].iloc[0])
            except (ValueError, TypeError):
                return 0.0

        acceptable_pct = _pct("Acceptable Housing (Affordable, Adequate, and Suitable)")
        unacceptable_pct = max(0.0, 100.0 - acceptable_pct)

        raw_details = [_pct(ind) for ind in CHART_DETAIL_INDICATORS]
        total_raw = sum(raw_details)
        if total_raw > 0:
            scaled_details = [v * unacceptable_pct / total_raw for v in raw_details]
        else:
            scaled_details = [unacceptable_pct / 4] * 4

        # Sunburst hierarchy:
        #   root → "Acceptable housing"  (leaf, no children)
        #   root → "Unacceptable"        (parent of 4 detail labels)
        #        → CHART_DETAIL_LABELS   (leaves)
        labels  = ["Housing", "Acceptable", "Unacceptable"] + CHART_DETAIL_LABELS
        # parents = ["", ""] + ["Unacceptable"] * len(CHART_DETAIL_LABELS)
        parents = ["", "Housing", "Housing"] + ["Unacceptable"] * len(CHART_DETAIL_LABELS)
        values  = [acceptable_pct + unacceptable_pct, acceptable_pct, unacceptable_pct] + scaled_details

        _UNACCEPTABLE_COLOR = "#5e2a1c"

        colors = ["#FFFFFF", _PIE_ACCEPTABLE_COLOR, _UNACCEPTABLE_COLOR] + _PIE_OUTER_COLORS


        text = [
            lbl
            if lbl == "Housing"
            else f"{lbl}<br>{val:.0f}%"
            if (i < 3 or raw_details[i - 3] > 0) else ""
            for i, (lbl, val) in enumerate(zip(labels, values))
        ]

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors,
                line=dict(color="white"),
            ),
            text=text,
            texttemplate="%{text}",
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>%{value:.0f}% of total HHs<extra></extra>",
        ))

        fig.update_layout(
            title=dict(
                text=(
                    f"2021 Indigenous Households in Unacceptable Housing<br>"
                    f"<sup>{geo_name}</sup>"
                ),
                x=0.5, xanchor="center",
                font=dict(size=15, family=TABLE_FONT),
            ),
            paper_bgcolor="white",
            font=dict(family=TABLE_FONT),
            margin=dict(t=90, b=40, l=20, r=20),
            height=550,
        )
        fig.update_traces(leaf=dict(opacity=0.9))


        return fig
