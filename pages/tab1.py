"""
Dashboard Tab 1: Who lives here? Covers: Demographics (Section 3), Households (Section 4) and Income (Section 5)
"""
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc

from dashboard_helpers.tab1_helpers.section_3 import Section3Prep
from dashboard_helpers.tab1_helpers.section_4 import Section4Prep
from dashboard_helpers.tab1_helpers.section_5 import Section5Prep


from dashboard_helpers.content_helpers.text_content import (
    TABLE_4_1_DESC, TABLE_4_3_DESC, 
    TABLE_5_2_DESC, TABLE_5_5_DESC, TABLE_5_5_NOTE, TABLE_5_5_TITLE, 
)
from dashboard_helpers.config import TABLE_FONT
from dashboard_helpers.content_helpers.table_styles import COLOR_SCHEME
from dashboard_helpers.content_helpers.data_loader import resolve_geocode


# Initialize helpers
section_3_layout = Section3Prep()
section_4_layout = Section4Prep()
section_5_layout = Section5Prep()

# Table IDs with toggle features for Tab 1
TABLE_IDS = ["table-4-1", "table-4-3", "table-5-2", "table-5-5"]

TOGGLE_WRAPPER_STYLE = {}

def derive_tab1_state(store: dict) -> str:
    """Return 'all_on', 'all_off', or 'mixed' based on per-table toggle states."""
    values = list(store.values())
    if all(values):
        return "all_on"
    if not any(values):
        return "all_off"
    return "mixed"


def tab1_toggle_ui():
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
                        id="tab1-toggle-btn",
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
    dcc.Store(id="tab1-intent-store", data="all_off"),
    dcc.Store(id="tab1-visibility-store", data={tid: False for tid in TABLE_IDS}),

    # Export button
    dbc.Button("Export to PDF", id="export-btn", className="export-pdf"),
    html.Div(id='dummy-output', style={'display': 'none'}),
    

    # Page content
    html.Div([
        # Global toggle card (top of page)
        html.Br(),
        tab1_toggle_ui(),
        
        # Section 3 - Demographics
        html.Div([
            html.Div(id='table-3-1-container'),
            html.Div(id='chart-3-2-container'),
            html.Div(id='chart-3-3-container'),
            html.Div(id='table-3-3-container'),
            html.Div(id='chart-3-4-container'),
            html.Div(id='table-3-4-container'),
            html.Div(id='table-3-5-container'),
            html.Div(id='table-3-5-1-container'),
            html.Div(id='chart-3-6-container'),
            html.Div(id='table-3-6-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 4 - Housing Tenure
        html.Div([
            html.Div(id='chart-4-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div([html.P(TABLE_4_1_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab1-toggle", "index": "table-4-1"},
                        value=False,
                        label="",
                        className="mb-0 green-toggle ms-5",
                        style={"transform": "scale(1.2)", "pointerEvents": "auto"},
                    ),
                # ], className="d-flex justify-content-between align-items-center mb-2 pb-2",
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
            ], id='toggle-wrapper-4-1'),
            
            html.Div(id='table-4-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div(id='table-4-2-container'),
            html.Div(id='chart-4-3-container'),
        ], className='pg2-table-plot-box-lgeo'),


        html.Div([
            html.Div([html.P(TABLE_4_3_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab1-toggle", "index": "table-4-3"},
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
            ], id='toggle-wrapper-4-3'),

            html.Div(id='table-4-3-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div(id='table-4-4-container'),
            html.Div(id='table-4-5-container'),
            html.Div(id='table-4-6-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 5 - Income
        html.Div([
            html.Div(id='table-5-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div(id='chart-5-2-container'),
            html.Div([html.P(TABLE_5_2_DESC)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab1-toggle", "index": "table-5-2"},
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
            ], id='toggle-wrapper-5-2'),
            
            html.Div(id='table-5-2-container'),
        ], className='pg2-table-plot-box-lgeo'),


        html.Div([
            html.Div(id='table-5-3-container'),
            html.Div(id='table-5-4-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.H5(TABLE_5_5_TITLE, className='table-title'),
            html.Div([html.P(TABLE_5_5_DESC),
                      html.I(TABLE_5_5_NOTE)], className='pg2-text-content-lgeo'),
            html.Div([
                html.Div([
                    html.Div([
                        # html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                        html.Span('Show Comparison: Indigenous & Non-Indigenous',
                                  style={'fontFamily': TABLE_FONT}),
                    ]),
                    dbc.Switch(
                        id={"type": "tab1-toggle", "index": "table-5-5"},
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
            ], id='toggle-wrapper-5-5'),

            html.Div(id='table-5-5-container'),
        ], className='pg2-table-plot-box-lgeo'),

    ], id='page-content-to-print', className='dashboard-pg2-lgeo')

], className='content-container-fullpage')


# Any local switch → rebuild visibility store + derive global state (incl. mixed)
@callback(
    Output("tab1-visibility-store", "data"),
    Output("tab1-toggle-btn", "children"),
    # Output("tab1-toggle-btn", "color"),
    Output("tab1-toggle-btn", "style"),
    Output("tab1-intent-store", "data"),
    Input({"type": "tab1-toggle", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def tab1_toggle_state(toggle_values):
    new_store = {tid: val for tid, val in zip(TABLE_IDS, toggle_values)}
    global_state = derive_tab1_state(new_store)

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
    Output("tab1-visibility-store", "data", allow_duplicate=True),
    Output("tab1-toggle-btn", "children", allow_duplicate=True),
    # Output("tab1-toggle-btn", "color", allow_duplicate=True),
    Output("tab1-toggle-btn", "style", allow_duplicate=True),
    Output("tab1-intent-store", "data", allow_duplicate=True),
    Output({"type": "tab1-toggle", "index": ALL}, "value"),
    Input("tab1-toggle-btn", "n_clicks"),
    State("tab1-intent-store", "data"),
    prevent_initial_call=True,
)
def tab1_toggle_click(_, current_intent):
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


# Section 3 - Demographics
@callback(
    Output('table-3-1-container', 'children'),
    Output('chart-3-2-container', 'children'),
    Output('chart-3-3-container', 'children'),
    Output('table-3-3-container', 'children'),
    Output('chart-3-4-container', 'children'),
    Output('table-3-4-container', 'children'),
    Output('table-3-5-container', 'children'),
    Output('table-3-5-1-container', 'children'),
    Output('chart-3-6-container', 'children'),
    Output('table-3-6-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data')
)
def update_section_3(geo_name, scale):
    geocode = resolve_geocode(geo_name, scale, section_3_layout.data_loader)

    return (
        section_3_layout.create_table_3_1_layout(geocode),
        section_3_layout.create_chart_3_2(geocode),
        section_3_layout.create_chart_3_3(geocode),
        section_3_layout.create_table_3_3_layout(geocode),
        section_3_layout.create_chart_3_4(geocode),
        section_3_layout.create_table_3_4_layout(geocode),
        section_3_layout.create_table_3_5_layout(geocode),
        section_3_layout.create_table_3_5_1_layout(geocode),
        section_3_layout.create_chart_3_6(geocode),
        section_3_layout.create_table_3_6_layout(geocode),
    )



@callback(
    Output('chart-4-1-container', 'children'),
    Output('table-4-1-container', 'children'),
    Output('toggle-wrapper-4-1', 'style'),
    Output('table-4-2-container', 'children'),
    Output('chart-4-3-container', 'children'),
    Output('table-4-3-container', 'children'),
    Output('toggle-wrapper-4-3', 'style'),
    Output('table-4-4-container', 'children'),
    Output('table-4-5-container', 'children'),
    Output('table-4-6-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('tab1-visibility-store', 'data'),
)
def update_section_4(geo_name, scale, visibility):
    show_both_4_1 = (visibility or {}).get("table-4-1", False)
    show_both_4_3 = (visibility or {}).get("table-4-3", False)
    geocode = resolve_geocode(geo_name, scale, section_4_layout.data_loader)

    table_4_1, empty_4_1 = section_4_layout.create_table_4_1_layout(geocode, show_both_4_1)
    table_4_3, empty_4_3 = section_4_layout.create_table_4_3_layout(geocode, show_both_4_3)

    return (
        section_4_layout.create_chart_4_1(geocode),
        table_4_1,
        {'display': 'none'} if empty_4_1 else TOGGLE_WRAPPER_STYLE,
        section_4_layout.create_table_4_2_layout(geocode),
        section_4_layout.create_chart_4_3(geocode),
        table_4_3,
        {'display': 'none'} if empty_4_3 else TOGGLE_WRAPPER_STYLE,
        section_4_layout.create_table_4_4_layout(geocode),
        section_4_layout.create_table_4_5_layout(geocode, True),
        section_4_layout.create_table_4_6_layout(geocode),
    )


@callback(
    Output('table-5-1-container', 'children'),
    Output('chart-5-2-container', 'children'),
    Output('table-5-2-container', 'children'),
    Output('toggle-wrapper-5-2', 'style'),
    Output('table-5-3-container', 'children'),
    Output('table-5-4-container', 'children'),
    Output('table-5-5-container', 'children'),
    Output('toggle-wrapper-5-5', 'style'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('tab1-visibility-store', 'data'),
)
def update_section_5(geo_name, scale, visibility):
    show_both_5_2 = (visibility or {}).get("table-5-2", False)
    show_both_5_5 = (visibility or {}).get("table-5-5", False)
    geocode = resolve_geocode(geo_name, scale, section_5_layout.data_loader)

    table_5_2, empty_5_2 = section_5_layout.create_table_5_2_layout(geocode, show_both_5_2)
    table_5_5, empty_5_5 = section_5_layout.create_table_5_5_layout(geocode, show_both_5_5)

    return (
        section_5_layout.create_table_5_1_layout(geocode),
        section_5_layout.create_chart_5_2(geocode),
        table_5_2,
        {'display': 'none'} if empty_5_2 else TOGGLE_WRAPPER_STYLE,
        section_5_layout.create_table_5_3_layout(geocode),
        section_5_layout.create_table_5_4_layout(geocode),
        table_5_5,
        {'display': 'none'} if empty_5_5 else TOGGLE_WRAPPER_STYLE,
        )
