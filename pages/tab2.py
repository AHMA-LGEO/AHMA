"""
Dashboard Tab 2: How are people housed? Covers: Dwellings (Section 6), Shelter Cost and Rental Market (Section 7) and Access to Services (Section 10)
"""
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc

from dashboard_helpers.tab2_helpers.section_6 import Section6Prep
from dashboard_helpers.tab2_helpers.section_7 import Section7Prep
from dashboard_helpers.tab2_helpers.section_10 import Section10Prep

from dashboard_helpers.content_helpers.text_content import (
    SECTION_7_P1, SECTION_7_P2, SECTION_7_TITLE, 
    TABLE_6_1_DESC, TABLE_6_3_DESC, TABLE_6_5_DESC, TABLE_6_5_TITLE, TABLE_7_1_DESC, TABLE_7_1_TITLE,
)
from dashboard_helpers.config import TABLE_FONT
from dashboard_helpers.content_helpers.table_styles import COLOR_SCHEME
from dashboard_helpers.content_helpers.data_loader import resolve_geocode

# Initialize helpers
section_6_layout = Section6Prep()
section_7_layout = Section7Prep()
section_10_layout = Section10Prep()


# Table IDs with toggle features for Tab 2
TABLE_IDS = ["table-6-1", "table-6-3", "table-6-5", "table-7-1"]

TOGGLE_WRAPPER_STYLE = {'maxWidth': '1200px', 'margin': '0 auto'}

def derive_tab2_state(store: dict) -> str:
    """Return 'all_on', 'all_off', or 'mixed' based on per-table toggle states."""
    values = list(store.values())
    if all(values):
        return "all_on"
    if not any(values):
        return "all_off"
    return "mixed"


def tab2_toggle_ui():
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.H5("Indigenous Household Comparison", className="mb-0 fw-bold"),
                    html.Small("Toggle Indigenous & Non-Indigenous comparison view",
                               className="text-muted"),
                ]),
                html.Div([
                    dbc.Button(
                        id="tab2-toggle-btn",
                        children="● Show Comparison",
                        color="success",
                        outline=True,
                        size="sm",
                        className="d-flex align-items-center gap-2",
                        style={"minWidth": "170px", 
                               "justifyContent": "center",
                               "backgroundColor": "#80875C",
                               "borderColor": "#80875C",
                               "color": "#ffffff",
                               "fontFamily": "Open Sans",
                               "cursor": "pointer"},
                    ),
                ], className="d-flex align-items-center"),
            ], className="d-flex justify-content-between align-items-center"),
        ]),
        className="mb-4 shadow-sm border-0",
        style={"backgroundColor": "#f8f9fa"},
    )


layout = html.Div([
    # Stores
    dcc.Store(id='main-area', storage_type='local'),
    dcc.Store(id='comparison-area', storage_type='local'),
    dcc.Store(id='area-scale-store', storage_type='local'),
    dcc.Store(id="tab2-intent-store", data="all_off"),
    dcc.Store(id="tab2-visibility-store", data={tid: False for tid in TABLE_IDS}),

    # Export button
    # Wrapped in the content column so the button lines up with the
    # left edge of the section text instead of the viewport edge.
    html.Div(
        dbc.Button("Export to PDF", id="export-btn", className="export-pdf"),
        className="dashboard-pg2-lgeo",
    ),
    html.Div(id='dummy-output', style={'display': 'none'}),
    

    # Page content
    html.Div([
        # Global toggle card (top of page)
        html.Br(),
        tab2_toggle_ui(),

        # Section 6- Dwellings
        html.Div([
            html.Div(id='chart-6-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div([html.P(TABLE_6_1_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab2-toggle", "index": "table-6-1"},
                        value=False,
                        label="",
                        className="mb-0 green-toggle ms-5",
                        style={"transform": "scale(1.2)", "pointerEvents": "auto"},
                    ),
                ], className="d-flex align-items-center",
                   style={
                    #    "borderBottom": "2px solid #002145"
                        "borderLeft": "4px solid #9CA37A",
                        "marginBottom": "-70px",
                        "position": "relative",
                        "paddingLeft": "12px",
                        "paddingRight": "12px",
                        "paddingTop": "8px",
                        "paddingBottom": "8px",
                        "pointerEvents": "none",
                    }),
            ], id='toggle-wrapper-6-1'),

            html.Div(id='table-6-1-container'),
        ], className='pg2-table-plot-box-lgeo'),


        html.Div([
            html.Div(id='table-6-2-container'),
            html.Div(id='chart-6-3-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div([html.P(TABLE_6_3_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab2-toggle", "index": "table-6-3"},
                        value=False,
                        label="",
                        className="mb-0 green-toggle ms-5",
                        style={"transform": "scale(1.2)", "pointerEvents": "auto"},
                    ),
                ], className="d-flex align-items-center",
                   style={
                    #    "borderBottom": "2px solid #002145"
                        "borderLeft": "4px solid #9CA37A",
                        "marginBottom": "-70px",
                        "position": "relative",
                        "paddingLeft": "12px",
                        "paddingRight": "12px",
                        "paddingTop": "8px",
                        "paddingBottom": "8px",
                        "pointerEvents": "none",
                    }),
            ], id='toggle-wrapper-6-3'),

            html.Div(id='table-6-3-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div(id='table-6-4-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Br(),
        html.Br(),
        html.Div([
            html.Div([html.H5(TABLE_6_5_TITLE, className='table-title')]),
            html.Div([html.P(TABLE_6_5_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab2-toggle", "index": "table-6-5"},
                        value=False,
                        label="",
                        className="mb-0 green-toggle ms-5",
                        style={"transform": "scale(1.2)", "pointerEvents": "auto"},
                    ),
                ], className="d-flex align-items-center",
                   style={
                    #    "borderBottom": "2px solid #002145"
                        "borderLeft": "4px solid #9CA37A",
                        "marginBottom": "-70px",
                        "position": "relative",
                        "paddingLeft": "12px",
                        "paddingRight": "12px",
                        "paddingTop": "8px",
                        "paddingBottom": "8px",
                        "pointerEvents": "none",
                    }),
            ], id='toggle-wrapper-6-5'),

            html.Div(id='table-6-5-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div(id='table-6-6-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Br(),
        html.Br(),
        html.Br(),

        # Section 7 - Shelter Costs
        html.Div([
            html.H4(SECTION_7_TITLE, className='table-title'),
            html.Div([dcc.Markdown(SECTION_7_P1),
                      html.P(SECTION_7_P2)], className='pg2-text-content-lgeo'),
            html.H5(TABLE_7_1_TITLE, className='table-title'),
            html.Div([html.P(TABLE_7_1_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab2-toggle", "index": "table-7-1"},
                        value=False,
                        label="",
                        className="mb-0 green-toggle ms-5",
                        style={"transform": "scale(1.2)", "pointerEvents": "auto"},
                    ),
                ], className="d-flex align-items-center",
                   style={
                    #    "borderBottom": "2px solid #002145"
                        "borderLeft": "4px solid #9CA37A",
                        "marginBottom": "-70px",
                        "position": "relative",
                        "paddingLeft": "12px",
                        "paddingRight": "12px",
                        "paddingTop": "8px",
                        "paddingBottom": "8px",
                        "pointerEvents": "none",
                    }),
            ], id='toggle-wrapper-7-1'),

            html.Div(id='table-7-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div(id='chart-7-3-1-container'),
            html.Div(id='table-7-3-1-container'),
            html.Div(id='chart-7-3-2-container'),
            html.Div(id='table-7-3-2-container'),
            html.Div(id='chart-7-3-3-container'),
            html.Div(id='table-7-3-3-container'),
        ], className='pg2-table-plot-box-lgeo'),


        # Section 10 - Access to Services
        html.Div([
            html.Div(id='table-10-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

    ], id='page-content-to-print', className='dashboard-pg2-lgeo')

], className='content-container-fullpage')


@callback(
    Output("tab2-visibility-store", "data"),
    Output("tab2-toggle-btn", "children"),
    # Output("global-toggle-btn", "color"),
    Output("tab2-toggle-btn", "style"),
    Output("tab2-intent-store", "data"),
    Input({"type": "tab2-toggle", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def tab2_toggle_state(toggle_values):
    new_store = {tid: val for tid, val in zip(TABLE_IDS, toggle_values)}
    global_state = derive_tab2_state(new_store)

    if global_state == "all_on":
        # btn_label, btn_color, new_intent = "○ Hide Comparison", "secondary", "all_on"
        state_key, new_intent = "all_on", "all_on"
    elif global_state == "all_off":
        # btn_label, btn_color, new_intent = "● Show Comparison", "success", "all_off"
        state_key, new_intent = "all_off", "all_off"
    else:  # mixed — next global click will turn all on
        # btn_label, btn_color, new_intent = "◐ Mixed", "warning", "all_on"
        state_key, new_intent = "mixed", "all_on"

    colors =  COLOR_SCHEME[state_key]
    btn_style = {
        "minWidth": "170px",
        "justifyContent": "center",
        "backgroundColor": colors["bg"],
        "borderColor": colors["border"],
        "color": colors["text"],
        "cursor": "pointer",
        "border": f"2px solid {colors['border']}",
    }

    # return new_store, btn_label, btn_color, new_intent
    return new_store, colors['label'], btn_style, new_intent


# Global button click → set all switches + update store + button state
@callback(
    Output("tab2-visibility-store", "data", allow_duplicate=True),
    Output("tab2-toggle-btn", "children", allow_duplicate=True),
    # Output("global-toggle-btn", "color", allow_duplicate=True),
    Output("tab2-toggle-btn", "style", allow_duplicate=True),
    Output("tab2-intent-store", "data", allow_duplicate=True),
    Output({"type": "tab2-toggle", "index": ALL}, "value"),
    Input("tab2-toggle-btn", "n_clicks"),
    State("tab2-intent-store", "data"),
    prevent_initial_call=True,
)
def tab2_toggle_click(_, current_intent):
    turn_on = (current_intent == "all_off")
    new_store = {tid: turn_on for tid in TABLE_IDS}

    if turn_on:
        # btn_label, btn_color, new_intent = "● Show Comparison", "success", "all_on"
        state_key, new_intent = "all_on", "all_off"
    else:
        # btn_label, btn_color, new_intent = "○ Hide Comparison", "secondary", "all_off"
        state_key, new_intent = "all_off", "all_on"

    colors = COLOR_SCHEME[state_key]
    
    btn_style = {
        "minWidth": "170px",
        "justifyContent": "center",
        "backgroundColor": colors["bg"],
        "borderColor": colors["border"],
        "color": colors["text"],
        "cursor": "pointer",
        "border": f"2px solid {colors['border']}",
    }

    # return new_store, btn_label, btn_color, new_intent, [turn_on] * len(TABLE_IDS)
    return new_store, colors['label'], btn_style, new_intent, [turn_on] * len(TABLE_IDS)


@callback(
    Output('chart-6-1-container', 'children'),
    Output('table-6-1-container', 'children'),
    Output('toggle-wrapper-6-1', 'style'),
    Output('table-6-2-container', 'children'),

    Output('chart-6-3-container', 'children'),
    Output('table-6-3-container', 'children'),
    Output('toggle-wrapper-6-3', 'style'),
    Output('table-6-4-container', 'children'),

    Output('table-6-5-container', 'children'),
    Output('toggle-wrapper-6-5', 'style'),
    Output('table-6-6-container', 'children'),

    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('tab2-visibility-store', 'data'),
)
def update_section_6(geo_name, scale, visibility):
    show_both_6_1 = (visibility or {}).get("table-6-1", False)
    show_both_6_3 = (visibility or {}).get("table-6-3", False)
    show_both_6_5 = (visibility or {}).get("table-6-5", False)
    geocode = resolve_geocode(geo_name, scale, section_6_layout.data_loader)

    table_6_1_name = 'table_6_1_hhs_bedroom'
    table_6_2_name = 'table_6_2_hhs_bedroom_breakdown'
    table_6_1_2_label = 'Households by Number of Bedrooms of Dwelling'

    table_6_3_name = 'table_6_3_hhs_construction_period'
    table_6_4_name = 'table_6_4_hhs_construction_period_breakdown'
    table_6_3_4_label = 'Households by Period of Construction of Dwelling'

    table_6_5_name = 'table_6_5_hhs_structure_type'
    table_6_6_name = 'table_6_6_hhs_structure_type_breakdown'
    table_6_5_6_label = 'Households by Structural Type of Dwelling'

    table_6_1, empty_6_1 = section_6_layout.create_table_6_primary_layout(geocode, table_6_1_name, table_6_1_2_label, show_both_6_1)
    table_6_3, empty_6_3 = section_6_layout.create_table_6_primary_layout(geocode, table_6_3_name, table_6_3_4_label, show_both_6_3)
    table_6_5, empty_6_5 = section_6_layout.create_table_6_primary_layout(geocode, table_6_5_name, table_6_5_6_label, show_both_6_5)

    return (
        section_6_layout.create_chart_6(geocode, table_6_1_name, table_6_1_2_label),
        table_6_1,
        {'display': 'none'} if empty_6_1 else TOGGLE_WRAPPER_STYLE,
        section_6_layout.create_table_6_secondary_layout(geocode, table_6_2_name, table_6_1_2_label),

        section_6_layout.create_chart_6(geocode, table_6_3_name, table_6_3_4_label),
        table_6_3,
        {'display': 'none'} if empty_6_3 else TOGGLE_WRAPPER_STYLE,
        section_6_layout.create_table_6_secondary_layout(geocode, table_6_4_name, table_6_3_4_label),

        table_6_5,
        {'display': 'none'} if empty_6_5 else TOGGLE_WRAPPER_STYLE,
        section_6_layout.create_table_6_secondary_layout(geocode, table_6_6_name, table_6_5_6_label),
        )


@callback(
    Output('table-7-1-container', 'children'),
    Output('toggle-wrapper-7-1', 'style'),
    Output('chart-7-3-1-container', 'children'),
    Output('table-7-3-1-container', 'children'),
    Output('chart-7-3-2-container', 'children'),
    Output('table-7-3-2-container', 'children'),
    Output('chart-7-3-3-container', 'children'),
    Output('table-7-3-3-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('tab2-visibility-store', 'data'),
)
def update_section_7(geo_name, scale, visibility):
    show_both = (visibility or {}).get("table-7-1", False)
    geocode = resolve_geocode(geo_name, scale, section_7_layout.data_loader)
    table_7_1, empty_7_1 = section_7_layout.create_table_7_1_layout(geocode, show_both)
    return (
        table_7_1,
        {'display': 'none'} if empty_7_1 else TOGGLE_WRAPPER_STYLE,
        section_7_layout.create_chart_7_3_1(geocode),
        section_7_layout.create_table_7_3_1_layout(geocode),
        section_7_layout.create_chart_7_3_2(geocode),
        section_7_layout.create_table_7_3_2_layout(geocode),
        section_7_layout.create_chart_7_3_3(geocode),
        section_7_layout.create_table_7_3_3_layout(geocode),
        )

@callback(
    Output('table-10-1-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data')
)
def update_section_10(geo_name, scale):
    geocode = resolve_geocode(geo_name, scale, section_10_layout.data_loader)

    return section_10_layout.create_table_10_1_layout(geocode)
