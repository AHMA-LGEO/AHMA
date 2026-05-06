"""
Section 8 preparation and layout - Core Housing Need Indicators.
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
    get_special_row_styles_8_1,
    format_number,
    format_percent,
    _T8_BELOW_MULTIPLE,
    _T8_TOTAL,
)
from .text_content import SECTION_8_TITLE, TABLE_8_1_TITLE, TABLE_8_7_TITLE
from .export_helpers import with_export_btn
from dashboard_helpers.config import CHART_COLORS, TABLE_FONT, PLOT_CONFIG, YEARS, YEARS_MINUS_2011



# Fixed display order for indicators
INDICATOR_ORDER = [
    "Affordability (Households paying >30% of income on shelter)",
    "Adequacy (Households living in dwellings needing Major Repairs)",
    "Suitability (Households living in overcrowded dwellings)",
    _T8_BELOW_MULTIPLE,
    "Acceptable Housing (Affordable, Adequate, and Suitable)",
    _T8_TOTAL,
]

# Labels used in the outer ring of the wedge-pie chart
CHART_DETAIL_LABELS = [
    "Unaffordability",
    "Inadequacy",
    "Unsuitability",
    "Below multiple <br>indicators",
]
CHART_DETAIL_INDICATORS = INDICATOR_ORDER[:4]

# Going with colors that makes sense for acceptable and unacceptable housing needs, 
# instead of selected first 5 colors from color pallete
_PIE_ACCEPTABLE_COLOR = "#9CA37A"
_PIE_OUTER_COLORS = ["#D89A86", "#C97A63", "#b55438", "#5b2a1c"]



class Section8Prep:
    """Prepare and format Section 8 schemas."""

    def __init__(self):
        self.data_loader = get_data_loader()

    def prepare_table_8_1_data(self, geocode: int) -> pd.DataFrame:
        filtered = self.data_loader.get_table('table_8_1_core_housing_need', geocode)

        if filtered.empty:
            return pd.DataFrame()

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs']
        non_indg = filtered[filtered['Household Type'] == 'Non-Indigenous HHs']
        _LABEL_COL = 'Indicator'

        indg_cols = [f'indg_{y}' for y in YEARS_MINUS_2011]
        non_indg_cols = [f'non_indg_{y}' for y in YEARS_MINUS_2011]
        all_val_cols = indg_cols + non_indg_cols

        indg_idx = indg.set_index([_LABEL_COL, 'Metric'])
        non_indg_idx = non_indg.set_index([_LABEL_COL, 'Metric'])

        def _fmt_vals(idx_df, indicator, metric, fmt_fn, prefix):
            try:
                row = idx_df.loc[(indicator, metric)]
                return {f'{prefix}_{y}': fmt_fn(row[y]) for y in YEARS_MINUS_2011}
            except KeyError:
                return {f'{prefix}_{y}': 'NA' for y in YEARS_MINUS_2011}

        rows = []
        for indicator in INDICATOR_ORDER:
            indg_count_vals = _fmt_vals(indg_idx, indicator, 'Number of households', format_number, 'indg')
            non_indg_count_vals = _fmt_vals(non_indg_idx, indicator, 'Number of households', format_number, 'non_indg')

            if indicator == _T8_TOTAL:
                rows.append({_LABEL_COL: indicator, **indg_count_vals, **non_indg_count_vals})
                rows.append(blank_row(_LABEL_COL))
                continue

            indg_pct_vals = _fmt_vals(indg_idx, indicator, '% of households', format_percent, 'indg')
            non_indg_pct_vals = _fmt_vals(non_indg_idx, indicator, '% of households', format_percent, 'non_indg')

            # Section header row
            rows.append(blank_row(_LABEL_COL, all_val_cols, indicator))

            count_label = '__below_count__' if indicator == _T8_BELOW_MULTIPLE else 'Number of households'
            rows.append({_LABEL_COL: count_label, **indg_count_vals, **non_indg_count_vals})

            pct_label = '__below_pct__' if indicator == _T8_BELOW_MULTIPLE else '% of households'
            rows.append({_LABEL_COL: pct_label, **indg_pct_vals, **non_indg_pct_vals})

            rows.append(blank_row(_LABEL_COL))

        return pd.DataFrame(rows, dtype=object)

    def create_table_8_1_layout(self, geocode: int, show_both: bool = False):
        """
        Create Dash DataTable for Table 8.1 with Core Housing Needs indicators (2006, 2016, 2021).:
            Level 0 - geography name
            Level 1 - Indigenous HHs | Non-Indigenous HHs (toggled)
            Level 2 - census year
        """
        df = self.prepare_table_8_1_data(geocode)
        if df.empty or df.isnull().values.all():
            return html.Div([
                html.Div(
                "No data for Core Housing Needs indicators (2006, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("NA")

        _LABEL_COL = "Indicator"

        columns = [
            {"name": ["", _LABEL_COL, ""], "id": _LABEL_COL}
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

        # Replace internal tags with display text
        df_display = df[data_cols].copy()
        df_display[_LABEL_COL] = df_display[_LABEL_COL].replace({
            '__below_count__': 'Number of households',
            '__below_pct__': '% of households',
        })

        base_style = get_base_table_style()
        data_cols.remove(_LABEL_COL)

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
                columns, is_multiindex=True, first_col_id=_LABEL_COL
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='200px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-8-1'),
        ], className='pg2-table-lgeo')
    

    def create_chart_8_1(self, geocode: int):
        """Sunburst (nested-pie) chart for for Table 8.1 2021 Indigenous Core Housing Need."""
        filtered = self.data_loader.get_table('table_8_1_core_housing_need', geocode)

        if filtered.empty or filtered.isnull().values.all():
            return html.Div([
                html.H4(SECTION_8_TITLE, className='table-title'),
                html.H6(TABLE_8_1_TITLE, className='table-desc'),
                html.Div(
                "No chart for 2021 Indigenous Core Housing Need.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs']
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        indg_pct_idx = indg[indg['Metric'] == '% of households'].set_index('Indicator')['2021']

        def _pct(indicator):
            try:
                return float(indg_pct_idx.loc[indicator])
            except (KeyError, ValueError, TypeError):
                return 0.0

        acceptable_pct = _pct("Acceptable Housing (Affordable, Adequate, and Suitable)")
        unacceptable_pct = max(0.0, 100.0 - acceptable_pct)

        raw_details = [_pct(ind) for ind in CHART_DETAIL_INDICATORS]
        total_raw = sum(raw_details)
        scaled_details = (
            [v * unacceptable_pct / total_raw for v in raw_details]
            if total_raw > 0 else [unacceptable_pct / 4] * 4
        )

        labels  = ["Housing", "Acceptable", "Unacceptable"] + CHART_DETAIL_LABELS
        parents = ["", "Housing", "Housing"] + ["Unacceptable"] * len(CHART_DETAIL_LABELS)
        values  = [acceptable_pct + unacceptable_pct, acceptable_pct, unacceptable_pct] + scaled_details
        colors  = ["#FFFFFF", _PIE_ACCEPTABLE_COLOR, "#5e2a1c"] + _PIE_OUTER_COLORS

        text = [
            lbl if lbl == "Housing"
            else f"{lbl}<br>{val:.0f}%"
            if (i < 3 or raw_details[i - 3] > 0) else ""
            for i, (lbl, val) in enumerate(zip(labels, values))
        ]

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors, line=dict(color="white")),
            text=text,
            texttemplate="%{text}",
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>%{value:.0f}% of total HHs<extra></extra>",
        ))

        fig.update_layout(
            title=dict(
                text=f"2021 Indigenous Households in Unacceptable Housing<br><sup>{geo_name}</sup>",
                x=0.5, xanchor="center",
                font=dict(size=15, family=TABLE_FONT),
            ),
            paper_bgcolor="white",
            font=dict(family=TABLE_FONT),
            margin=dict(t=90, b=40, l=20, r=20),
            height=550,
        )
        fig.update_traces(leaf=dict(opacity=0.9))

        return html.Div([
            html.H4(SECTION_8_TITLE, className='table-title'),
            html.H6(TABLE_8_1_TITLE, className='table-desc'),
            dcc.Graph(id='chart-8-1', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    
    
    def create_table_8_7_layout(self, geocode: int):
        """Create pie chart for Table 8.7 Housing Deficit by Income and HH size (2021)."""
        df = self.data_loader.get_table('table_8_7_housing_deficit', geocode)

        if df.empty or df.isnull().values.all():
            return html.Div([
                html.H4(TABLE_8_7_TITLE, className='table-title'),
                html.Div(
                "No data for Housing Deficit by Income and HH size (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("NA")

        hh_cols = ['1 pp', '2 pp', '3 pp', '4 pp', '5+ pp', 'Total']

        table_df = df.set_index('Income Type')[hh_cols].reset_index()

        table_df = table_df.applymap(format_number)

        columns = [{"name": [geo_name, "2021 Affordable Housing Deficit - Indigenous HHs in Core Housing Need"], "id": "Income Type"}] + [
            {"name": [geo_name, col], "id": col} for col in hh_cols
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-8-7',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, 'Income Type', total_labels={'Total'}, total_col=True)
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id='Income Type'
            ),
            style_cell_conditional=make_style_cell('Income Type', hh_cols, label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H4(TABLE_8_7_TITLE, className='table-title'),
            with_export_btn(table, 'table-8-7'),
        ], className='pg2-table-lgeo')
