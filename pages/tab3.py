"""
Dashboard Tab 3: Where does the system fail? Covers: Housing Need Indicators (Section 8) and Systematic Pathways (Section 9)
"""
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc

from dashboard_helpers.tab3_helpers.section_8 import Section8Prep
from dashboard_helpers.tab3_helpers.section_9 import Section9Prep

from dashboard_helpers.content_helpers.text_content import (
    TABLE_8_1_DESC, TABLE_8_3_DESC, TABLE_8_3_TITLE, TABLE_8_5_DESC
)
from dashboard_helpers.config import TABLE_FONT
from dashboard_helpers.content_helpers.table_styles import COLOR_SCHEME
from dashboard_helpers.content_helpers.data_loader import resolve_geocode

# Initialize helpers
section_8_layout = Section8Prep()
section_9_layout = Section9Prep()

# Table IDs with toggle features for Tab 3
TABLE_IDS = ["table-8-1", "table-8-3", "table-8-5"]

TOGGLE_WRAPPER_STYLE = {}


def derive_tab3_state(store: dict) -> str:
    """Return 'all_on', 'all_off', or 'mixed' based on per-table toggle states."""
    values = list(store.values())
    if all(values):
        return "all_on"
    if not any(values):
        return "all_off"
    return "mixed"


def tab3_toggle_ui():
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
                        id="tab3-toggle-btn",
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
    dcc.Store(id="tab3-intent-store", data="all_off"),
    dcc.Store(id="tab3-visibility-store", data={tid: False for tid in TABLE_IDS}),

    # Export button
    # dbc.Button("Export to PDF", id="export-btn", className="export-pdf"),
    # html.Div(id='dummy-output', style={'display': 'none'}),
    

    # Page content
    html.Div([
        # Global toggle card (top of page)
        html.Br(),
        tab3_toggle_ui(),
        
        # Section 8 - Housing Need Indicators
        html.Div([
            html.Div(id='chart-8-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div([html.P(TABLE_8_1_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab3-toggle", "index": "table-8-1"},
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
            ], id='toggle-wrapper-8-1'),

            html.Div(id='table-8-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.H5(TABLE_8_3_TITLE, className='table-title'),
            html.Div([html.P(TABLE_8_3_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab3-toggle", "index": "table-8-3"},
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
            ], id='toggle-wrapper-8-3'),

            html.Div(id='table-8-3-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div(id='table-8-4-container'),
            html.Div(id='chart-8-5-container'),
        ], className='pg2-table-plot-box-lgeo'),


        html.Div([
            html.Div([html.P(TABLE_8_5_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab3-toggle", "index": "table-8-5"},
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
            ], id='toggle-wrapper-8-5'),

            html.Div(id='table-8-5-container'),
        ], className='pg2-table-plot-box-lgeo'),


        html.Div([
            html.Div(id='table-8-6-container'),
            html.Div(id='table-8-7-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 9 - Systematic Pathways and Indigenous Homelessness
        html.Div([
            html.Div(id='chart-9-1-container'),
            html.Div(id='table-9-1-container'),
            html.Div(id='table-9-2-container'),
            html.Div(id='table-9-3-container'),
        ], className='pg2-table-plot-box-lgeo'),

    ], id='page-content-to-print', className='dashboard-pg2-lgeo')

], className='content-container-fullpage')


# Any local switch → rebuild visibility store + derive global state (incl. mixed)
@callback(
    Output("tab3-visibility-store", "data"),
    Output("tab3-toggle-btn", "children"),
    # Output("tab3-toggle-btn", "color"),
    Output("tab3-toggle-btn", "style"),
    Output("tab3-intent-store", "data"),
    Input({"type": "tab3-toggle", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def tab3_toggle_state(toggle_values):
    new_store = {tid: val for tid, val in zip(TABLE_IDS, toggle_values)}
    global_state = derive_tab3_state(new_store)

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
    Output("tab3-visibility-store", "data", allow_duplicate=True),
    Output("tab3-toggle-btn", "children", allow_duplicate=True),
    # Output("tab3-toggle-btn", "color", allow_duplicate=True),
    Output("tab3-toggle-btn", "style", allow_duplicate=True),
    Output("tab3-intent-store", "data", allow_duplicate=True),
    Output({"type": "tab3-toggle", "index": ALL}, "value"),
    Input("tab3-toggle-btn", "n_clicks"),
    State("tab3-intent-store", "data"),
    prevent_initial_call=True,
)
def tab3_toggle_click(_, current_intent):
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
    Output('chart-8-1-container', 'children'),
    Output('table-8-1-container', 'children'),
    Output('toggle-wrapper-8-1', 'style'),
    Output('table-8-3-container', 'children'),
    Output('toggle-wrapper-8-3', 'style'),
    Output('table-8-4-container', 'children'),
    Output('chart-8-5-container', 'children'),
    Output('table-8-5-container', 'children'),
    Output('toggle-wrapper-8-5', 'style'),
    Output('table-8-6-container', 'children'),
    Output('table-8-7-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('tab3-visibility-store', 'data'),
)
def update_section_8(geo_name, scale, visibility):
    show_both_8_1 = (visibility or {}).get("table-8-1", False)
    show_both_8_3 = (visibility or {}).get("table-8-3", False)
    show_both_8_5 = (visibility or {}).get("table-8-5", False)
    geocode = resolve_geocode(geo_name, scale, section_8_layout.data_loader)

    table_8_1, empty_8_1 = section_8_layout.create_table_8_1_layout(geocode, show_both_8_1)
    table_8_3, empty_8_3 = section_8_layout.create_table_8_3_layout(geocode, show_both_8_3)
    table_8_5, empty_8_5 = section_8_layout.create_table_8_5_layout(geocode, show_both_8_5)

    return (
        section_8_layout.create_chart_8_1(geocode),
        table_8_1,
        {'display': 'none'} if empty_8_1 else TOGGLE_WRAPPER_STYLE,
        table_8_3,
        {'display': 'none'} if empty_8_3 else TOGGLE_WRAPPER_STYLE,
        section_8_layout.create_table_8_4_layout(geocode),
        section_8_layout.create_chart_8_5(geocode),
        table_8_5,
        {'display': 'none'} if empty_8_5 else TOGGLE_WRAPPER_STYLE,
        section_8_layout.create_table_8_6_layout(geocode),
        section_8_layout.create_table_8_7_layout(geocode)
    )


@callback(
    Output('chart-9-1-container', 'children'),
    Output('table-9-1-container', 'children'),
    Output('table-9-2-container', 'children'),
    Output('table-9-3-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data')
)
def update_section_9(geo_name, scale):
    geocode = resolve_geocode(geo_name, scale, section_9_layout.data_loader)

    return (
        section_9_layout.create_chart_9_1(geocode),
        section_9_layout.create_table_9_1_layout(geocode),
        section_9_layout.create_table_9_2_layout(geocode),
        section_9_layout.create_table_9_3_layout(geocode)
    )
