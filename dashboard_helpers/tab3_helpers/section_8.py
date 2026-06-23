"""
Section 8 preparation and layout - Core Housing Need Indicators.
"""
import math
import pandas as pd
from dash import dash_table, html, dcc
import plotly.graph_objects as go

from dashboard_helpers.content_helpers.data_loader import get_data_loader
from dashboard_helpers.content_helpers.table_styles import (
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
from ..content_helpers.text_content import (
    SECTION_8_TITLE, SECTION_8_P1, SECTION_8_P2,
    TABLE_8_1_TITLE, CHART_8_1_DESC, TABLE_8_1_DESC,
    TABLE_8_3_TITLE, TABLE_8_3_DESC, 
    TABLE_8_4_DESC, 
    TABLE_8_5_TITLE, CHART_8_5_DESC, TABLE_8_5_DESC,
    TABLE_8_6_DESC, 
    TABLE_8_7_TITLE, TABLE_8_7_DESC
    )
from ..content_helpers.export_helpers import with_export_btn
from dashboard_helpers.config import (
    CHART_COLORS, TABLE_FONT, PLOT_CONFIG, 
    YEARS_MINUS_2011, COMMUNITIES)



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
        filtered = self.data_loader.get_table('table_8_1_core_housing_need', geocode, check_columns=YEARS_MINUS_2011)

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
                return {f'{prefix}_{y}': 'N/A' for y in YEARS_MINUS_2011}

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

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Core Housing Needs indicators (2006, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo'), True

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = "Indicator"

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
                columns, is_multiindex=True, first_col_id=_LABEL_COL,
                left_align_cells={'column_id':_LABEL_COL, 'header_index': 2}
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='200px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-8-1'),
        ], className='pg2-table-lgeo'), False
    

    def create_chart_8_1(self, geocode: int):
        """Sunburst (nested-pie) chart for for Table 8.1 2021 Indigenous Core Housing Need."""
        filtered = self.data_loader.get_table('table_8_1_core_housing_need', geocode)

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs']
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)

        indg_pct_idx = indg[indg['Metric'] == '% of households'].set_index('Indicator')['2021']

        def _pct(indicator):
            try:
                return float(indg_pct_idx.loc[indicator])
            except (KeyError, ValueError, TypeError):
                return 0.0

        acceptable_pct = _pct("Acceptable Housing (Affordable, Adequate, and Suitable)")

        if math.isnan(acceptable_pct):
            return html.Div([
                html.H4(SECTION_8_TITLE, className='table-title'),
                html.Div([html.P(SECTION_8_P1),
                          html.P(SECTION_8_P2)], className='pg2-text-content-lgeo'),
                html.H5(TABLE_8_1_TITLE, className='table-desc'),
                html.Div(
                "No chart for 2021 Indigenous Core Housing Need.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')
        
        unacceptable_pct = max(0.0, 100.0 - acceptable_pct)

        raw_details = [_pct(ind) for ind in CHART_DETAIL_INDICATORS]
        total_raw = sum(raw_details)
        scaled_details = (
            [v * unacceptable_pct / total_raw for v in raw_details]
            if total_raw > 0 else [unacceptable_pct / 4] * 4
        )

        labels  = ["Housing", "Unacceptable", "Acceptable"] + CHART_DETAIL_LABELS
        parents = ["", "Housing", "Housing"] + ["Unacceptable"] * len(CHART_DETAIL_LABELS)
        values  = [acceptable_pct + unacceptable_pct, unacceptable_pct, acceptable_pct] + scaled_details
        colors  = ["#FFFFFF", "#5e2a1c", _PIE_ACCEPTABLE_COLOR] + _PIE_OUTER_COLORS

        text = [
            lbl if lbl == "Housing"
            else f"{lbl}<br>{val:.0f}%"
            if (i < 3 or raw_details[i - 3] > 0) else ""
            for i, (lbl, val) in enumerate(zip(labels, values))
        ]

        threshold = 7 # threshold below which labels change to "..."
        total_value = sum(values)

        interactive_text = []
        for i, (val, original_text) in enumerate(zip(values, text)):
            if i >= 3:  # Detail indicators only (Unaffordability, Inadequacy, etc.)
                raw_pct = raw_details[i - 3]
                if raw_pct < threshold:
                    interactive_text.append("•••") 
                else:
                    interactive_text.append(original_text)
            else:
                interactive_text.append(original_text)


        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors, line=dict(color="white", width=2)),
            text=interactive_text,
            texttemplate="%{text}",
            textfont=dict(size=10, color="white"),
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>%{value:.0f}% of total HHs<extra></extra>",
            sort=False,
            rotation=-90
        ))

        fig.update_layout(
            title=dict(
                text=f"2021 Indigenous Households in Unacceptable Housing<br><sup>{geo_name}</sup>",
                x=0.5, xanchor="center",
                # font=dict(size=15, family=TABLE_FONT),
            ),
            paper_bgcolor="white",
            font=dict(family=TABLE_FONT),
            margin=dict(t=90, b=40, l=20, r=20),
            height=550,
            # Prevents text from sizing down into tiny unreadable fonts if slices shrink
            uniformtext=dict(minsize=9, mode="hide") 
        )
        fig.update_traces(leaf=dict(opacity=0.9))

        return html.Div([
            html.H4(SECTION_8_TITLE, className='table-title'),
            html.Div([html.P(SECTION_8_P1),
                      html.P(SECTION_8_P2)], className='pg2-text-content-lgeo'),
            html.H5(TABLE_8_1_TITLE, className='table-desc'),
            html.Div([html.P(CHART_8_1_DESC)], className='pg2-text-content-lgeo'),
            dcc.Graph(id='chart-8-1', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_8_3_layout(self, geocode: int, show_both: bool = False) -> pd.DataFrame:
        """Create Dash DataTable for Table 8.3 with Households in CHN or Extreme CHN, by Tenure (Indigenous & non-Indigenous) (2006, 2016, 2021)."""
        df = self.data_loader.get_table('table_8_3_hhs_in_chn', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.H5(TABLE_8_3_TITLE, className='table-title'),
                html.Div(
                "No data for Households in CHN or Extreme CHN (2006, 2016, 2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo'), True

        filtered = df.copy()
        _LABEL_COL = 'Census Year'

        pct_mask = filtered[_LABEL_COL].str.contains('%', na=False)
        for year in YEARS_MINUS_2011:
            filtered.loc[pct_mask, year] = filtered.loc[pct_mask, year].apply(
                lambda v: format_percent(v, multiply=False)
            )
            filtered.loc[~pct_mask, year] = filtered.loc[~pct_mask, year].apply(
                lambda v: format_number(v, decimals=0)
            )

        # Split by household type and prefix year columns
        indg = (
            filtered[filtered['Household Type'] == 'Indigenous HHs'][[_LABEL_COL] + YEARS_MINUS_2011]
            .rename(columns={y: f'indg_{y}' for y in YEARS_MINUS_2011})
        )
        non_indg = (
            filtered[filtered['Household Type'] == 'Non-Indigenous HHs'][[_LABEL_COL] + YEARS_MINUS_2011]
            .rename(columns={y: f'non_indg_{y}' for y in YEARS_MINUS_2011})
        )

        result = indg.merge(non_indg, on=_LABEL_COL, how='left')

        non_indg_cols = [f'non_indg_{y}' for y in YEARS_MINUS_2011]
        result[non_indg_cols] = result[non_indg_cols].fillna('N/A')

        indg_cols = [f'indg_{y}' for y in YEARS_MINUS_2011]
        all_val_cols = indg_cols + non_indg_cols

        # rows = [blank_row(_LABEL_COL, all_val_cols, _LABEL_COL)]
        rows = []
        for _, row in result.iterrows():
            rows.append(row.to_dict())
            tenure = row[_LABEL_COL]
            if tenure == '% of HHs in CHN who rent' in str(tenure):
                rows.append(blank_row(_LABEL_COL))
        
        
        table_df = pd.DataFrame(rows, dtype=object)
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        table_df = table_df.fillna("N/A")

        columns = [
            {"name": [geo_name, "", _LABEL_COL], "id": _LABEL_COL}
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
        df_display = table_df[data_cols]

        base_style = get_base_table_style()
        data_cols.remove(_LABEL_COL)

        table = dash_table.DataTable(
            id='table-8-3',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL, section_headers={_LABEL_COL},
                                          geo_headers={"Indigenous HHs", "Non-Indigenous HHs"})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=3,
                left_align_cells={'column_id':_LABEL_COL, 'header_index': 2}
                ),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-8-3'),
        ], className='pg2-table-lgeo'), False


    def create_table_8_4_layout(self, geocode: int):
        """Create Dash DataTable for Table 8.4 with Households in CHN by Indigenous communities."""
        df = self.data_loader.get_table('table_8_4_hhs_in_chn_breakdown', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Households in CHN by Indigenous communities.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        _LABEL_COL = 'Census Year'
        # communities = [comm + "-led HH"  for comm in COMMUNITIES]

        community_df = []
        for community in COMMUNITIES:
            indig_df = (
                df[df['Household Type'] == community]
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

        pct_mask = table_df[_LABEL_COL].str.contains('%', na=False)
        for col in val_cols:
            table_df.loc[pct_mask, col] = table_df.loc[pct_mask, col].apply(
                lambda v: format_percent(v, multiply=False)
            )
            table_df.loc[~pct_mask, col] = table_df.loc[~pct_mask, col].apply(format_number)

        # Prepend section header row

        # rows = [blank_row(_LABEL_COL, val_cols, _LABEL_COL)]
        rows = []
        for _, row in table_df.iterrows():
            rows.append(row.to_dict())
            tenure = row[_LABEL_COL]
            if tenure == '% of HHs in CHN who rent' in str(tenure):
                rows.append(blank_row(_LABEL_COL))

        formatted_df = pd.DataFrame(rows, dtype=object)

        # 3-level columns: [geo_name, year, community]
        columns = [{"name": [geo_name, "", _LABEL_COL], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-8-4',
            columns=columns,
            data=formatted_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(formatted_df)
                + make_special_row_styles(formatted_df, _LABEL_COL, geo_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL,
                left_align_cells={'column_id':_LABEL_COL, 'header_index': 2}
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='25%', 
                                                   label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.Div([html.P(TABLE_8_4_DESC)], className='pg2-text-content-lgeo'),
            with_export_btn(table, 'table-8-4'),
        ], className='pg2-table-lgeo')
    

    def create_table_8_5_layout(self, geocode: int, show_both: bool = False):
        
        """Create Dash DataTable for Table 8.5 with Households in CHN by Priority Population"""

        df = self.data_loader.get_table('table_8_5_hhs_in_chn_prior_pop', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Households in CHN by Priority Population.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo'), True

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

        filtered = df.copy()
        _LABEL_COL = 'Metric'
        
        for col in YEARS_MINUS_2011:
            filtered[col] = filtered[col].map(format_percent)

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

        # indg_cols = [f'indg_{y}' for y in YEARS_MINUS_2011]
        # all_val_cols = indg_cols + non_indg_cols
    
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
        df_display = result[data_cols]

        base_style = get_base_table_style()
        data_cols.remove(_LABEL_COL)

        table = dash_table.DataTable(
            id='table-8-5',
            columns=columns,
            data=df_display.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(df_display)
                + make_special_row_styles(df_display, _LABEL_COL, 
                                          geo_headers={_LABEL_COL}, total_labels={'Total'})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL,
                left_align_cells={'column_id':_LABEL_COL, 'header_index': 2}
                ),
            style_cell_conditional=make_style_cell(_LABEL_COL, data_cols, label_min_width='160px'),
            **base_style
        )

        return html.Div([
            with_export_btn(table, 'table-8-5'),
        ], className='pg2-table-lgeo'), False
    
    
    def create_chart_8_5(self, geocode: int):
        """Create stacked bar chart for Table 8.5 households in CHN by Priority Population - 2021."""

        filtered = self.data_loader.get_table('table_8_5_hhs_in_chn_prior_pop', geocode, 
                                              check_columns=['2021'])

        if filtered.empty:
            return html.Div([
                html.H5(TABLE_8_5_TITLE, className='table-title'),
                html.Div(
                "No chart for households in CHN by Priority Population - 2021.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        indg = filtered[filtered['Household Type'] == 'Indigenous HHs'][['Metric', '2021']].copy()
        _LABEL_COL = 'Metric'

        
        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        max_val = indg['2021'].max()

        prior_pop_list = indg[_LABEL_COL].tolist()
        colors = {t: CHART_COLORS[i % len(CHART_COLORS)] for i, t in enumerate(prior_pop_list)}

        # hover_config = dict(namelength=-1)
        # if '#80875C' in colors.values():
        #     hover_config['font'] = dict(color='white')


        fig = go.Figure()
  
        # fig.add_trace(go.Bar(
        #     y=indg[_LABEL_COL],
        #     x=indg['2021'],
        #     orientation='h',
        #     marker_color=[colors[t] for t in indg[_LABEL_COL]],
        #     customdata=indg[_LABEL_COL],
        #     # textposition='inside',
        #     hovertemplate=('<b>%{customdata}</b><br>Percentage: %{x:.1f}%<extra></extra>'),
        #     # hoverlabel=hover_config
        # ))
        mask = indg[_LABEL_COL].map(colors) == '#80875C'

        fig.add_trace(go.Bar(
            y=indg.loc[mask, _LABEL_COL],
            x=indg.loc[mask, '2021'],
            orientation='h',
            customdata=indg[_LABEL_COL],
            marker_color='#80875C',
            hoverlabel=dict(font=dict(color='white')),
            hovertemplate=('<b>%{customdata}</b><br>Percentage: %{x:.1f}%<extra></extra>'),
        ))

        fig.add_trace(go.Bar(
            y=indg.loc[~mask, _LABEL_COL],
            x=indg.loc[~mask, '2021'],
            orientation='h',
            customdata=indg[_LABEL_COL],
            marker_color=[colors[t] for t in indg.loc[~mask, _LABEL_COL]],
            hovertemplate=('<b>%{customdata}</b><br>Percentage: %{x:.1f}%<extra></extra>'),
        ))

        fig.update_layout(
            title=dict(text=f'Indigenous Housing in Core Housing Need by Priority Population in 2021 - {geo_name}', x=0.5, xanchor='center'),
            yaxis=dict(
                title='',
                categoryorder='array',
                categoryarray=prior_pop_list[::-1]
            ),
            xaxis=dict(
                title='Percentage of Households',
                ticksuffix='%',
                range=[0, max_val * 1.1],
                dtick=10,
                gridcolor='#E5E5E5',
            ),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=TABLE_FONT),
            showlegend=False
        )

        return html.Div([
            html.H5(TABLE_8_5_TITLE, className='table-title'),
            html.Div([html.P(CHART_8_5_DESC)], className='pg2-text-content-lgeo'),
            dcc.Graph(id='chart-8-5', figure=fig, config=PLOT_CONFIG)
        ], className='pg2-table-lgeo')
    

    def create_table_8_6_layout(self, geocode: int):
        """Create Dash DataTable for Table 8.6 with Households in CHN by Priority Populations by Indigenous communities."""

        df = self.data_loader.get_table('table_8_6_hhs_in_chn_prior_pop_breakdown', geocode, check_columns=YEARS_MINUS_2011)

        if df.empty:
            return html.Div([
                html.Div(
                "No data for Households in CHN by Priority Populations by Indigenous communities.",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")
        _LABEL_COL = 'Metric'

        community_df = []
        for community in COMMUNITIES:
            indig_df = (
                df[df['Household Type'] == community]
                .set_index(_LABEL_COL)[YEARS_MINUS_2011]
                .rename(columns={y: f'{y}_{community[0]}' for y in YEARS_MINUS_2011})
            )
            community_df.append(indig_df)

        table_df = pd.concat(community_df, axis=1).reset_index()

        # Column order: year, community (2006_f, 2006_m, 2006_i, 2016_f, ...)
        val_cols = [f'{y}_{c[0]}' for y in YEARS_MINUS_2011 for c in COMMUNITIES]
        # print(table_df)

        for col in val_cols:
            table_df[col] = table_df[col].map(format_percent)


        # 3-level columns: [geo_name, year, community]
        columns = [{"name": [geo_name, "", "Census Year"], "id": _LABEL_COL}] + [
            {"name": [geo_name, y, community], "id": f'{y}_{community[0]}'}
            for y in YEARS_MINUS_2011
            for community in COMMUNITIES
        ]

        base_style = get_base_table_style()

        table = dash_table.DataTable(
            id='table-8-6',
            columns=columns,
            data=table_df.to_dict('records'),
            merge_duplicate_headers=True,
            style_data_conditional=(
                generate_style_data_conditional(table_df)
                + make_special_row_styles(table_df, _LABEL_COL, geo_headers={_LABEL_COL})
            ),
            style_header_conditional=generate_style_header_conditional(
                columns, is_multiindex=True, first_col_id=_LABEL_COL, n_header_rows=3, 
                left_align_cells={'column_id':_LABEL_COL, 'header_index': 2}
            ),
            style_cell_conditional=make_style_cell(_LABEL_COL, val_cols, label_width='25%', 
                                                   label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.Div([html.P(TABLE_8_6_DESC)], className='pg2-text-content-lgeo'),
            with_export_btn(table, 'table-8-6'),
        ], className='pg2-table-lgeo')
    

    
    def create_table_8_7_layout(self, geocode: int):
        """Create pie chart for Table 8.7 Housing Deficit by Income and HH size (2021)."""
        hh_cols = ['1 pp', '2 pp', '3 pp', '4 pp', '5+ pp', 'Total']
        
        df = self.data_loader.get_table('table_8_7_housing_deficit', geocode, check_columns=hh_cols)

        if df.empty:
            return html.Div([
                html.H5(TABLE_8_7_TITLE, className='table-title'),
                html.Div(
                "No data for Housing Deficit by Income and HH size (2021).",
                style={'fontFamily': TABLE_FONT, 'color': '#666'}
                )
            ], className='pg2-table-lgeo')

        geo_name = self.data_loader.get_geography_name(geocode) or str(geocode)
        df = df.fillna("N/A")

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
                columns, is_multiindex=True, first_col_id='Income Type', n_header_rows=2,
                left_align_cells={'column_id':'Income Type', 'header_index': 1}
            ),
            style_cell_conditional=make_style_cell('Income Type', hh_cols, label_width='25%', label_min_width='120px'),
            **base_style
        )

        return html.Div([
            html.H5(TABLE_8_7_TITLE, className='table-title'),
            html.Div([html.P(TABLE_8_7_DESC)], className='pg2-text-content-lgeo'),
            with_export_btn(table, 'table-8-7'),
        ], className='pg2-table-lgeo')
