"""
Dashboard page 2: Housing needs tables and analysis.
"""
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc

from dashboard_helpers.page2_helpers.section_2 import Section2Prep
from dashboard_helpers.page2_helpers.section_3 import Section3Prep
from dashboard_helpers.page2_helpers.section_4 import Section4Prep
from dashboard_helpers.page2_helpers.section_5 import Section5Prep
from dashboard_helpers.page2_helpers.section_7 import Section7Prep
from dashboard_helpers.page2_helpers.section_8 import Section8Prep
from dashboard_helpers.page2_helpers.section_9 import Section9Prep

from dashboard_helpers.page2_helpers.text_content import (
    INTRO_TITLE, INTRO_TEXT
)
from dashboard_helpers.config import DEFAULT_GEOCODE, PLOT_CONFIG, TABLE_FONT

# Initialize helpers
section_2_layout = Section2Prep()
section_3_layout = Section3Prep()
section_4_layout = Section4Prep()
section_5_layout = Section5Prep()
section_7_layout = Section7Prep()
section_8_layout = Section8Prep()
section_9_layout = Section9Prep()

# Table IDs - add new table IDs with toggle features as page 2 grows
TABLE_IDS = ["table-4-1", "table-4-3", "table-5-5", "table-7-1", "table-8-1"]


def derive_global_state(store: dict) -> str:
    """Return 'all_on', 'all_off', or 'mixed' based on per-table toggle states."""
    values = list(store.values())
    if all(values):
        return "all_on"
    if not any(values):
        return "all_off"
    return "mixed"


def global_toggle_ui():
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
                        id="global-toggle-btn",
                        children="● Show Comparison",
                        color="success",
                        outline=True,
                        size="sm",
                        className="d-flex align-items-center gap-2",
                        style={"minWidth": "170px", "justifyContent": "center"},
                    ),
                ], className="d-flex align-items-center"),
            ], className="d-flex justify-content-between align-items-center"),
        ]),
        className="mb-4 shadow-sm border-0",
        style={"backgroundColor": "#f8f9fa"},
    )


# Layout
layout = html.Div([
    # Stores
    dcc.Store(id='main-area', storage_type='local'),
    dcc.Store(id='comparison-area', storage_type='local'),
    dcc.Store(id='area-scale-store', storage_type='local'),
    dcc.Store(id="global-intent-store", data="all_off"),
    dcc.Store(id="table-visibility-store", data={tid: False for tid in TABLE_IDS}),

    # Export button
    dbc.Button("Export to PDF", id="export-button", className="export-pdf"),
    html.Div(id='dummy-output', style={'display': 'none'}),

    # Page content
    html.Div([
        # Global toggle card (top of page)
        global_toggle_ui(),

        # Introduction
        html.H3(html.Strong(INTRO_TITLE), id='intro-title'),
        html.Div([
            html.H6([
                INTRO_TEXT,
                html.Br(), html.Br(),
                # INTRO_PARAGRAPH,
                html.Br(), html.Br(),
                # html.Ul([
                #     html.Li([html.I([note])]) for note in NOTES
                # ])
            ], style={'fontFamily': TABLE_FONT})
        ], className='muni-reg-text-lgeo'),

        # Section 2 - Nations / Territories and Métis Communities
        html.Div([
            html.Div(id='table-2-1-container'),
            html.Div(id='table-2-2-container'),
        ], className='pg2-table-plot-box-lgeo'),


        # Section 3 - Demographics
        html.Div([
            # html.Div(id='table-3-1-container'),
            # html.Div(id='chart-3-2-container'),
            # html.Div(id='chart-3-3-container'),
            # html.Div(id='table-3-3-container'),
            # html.Div(id='chart-3-4-container'),
            # html.Div(id='table-3-4-container'),
            # html.Div(id='table-3-5-container'),
            # html.Div(id='table-3-5-1-container'),
            # html.Div(id='chart-3-6-container'),
            # html.Div(id='table-3-6-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 4 - Housing Tenure
        html.Div([
            html.Div([
                html.Div([
                    html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                    html.Span('Indigenous & Non-Indigenous',
                              style={'fontFamily': TABLE_FONT}),
                ]),
                dbc.Switch(
                    id={"type": "table-toggle", "index": "table-4-1"},
                    value=False,
                    label="",
                    className="mb-0",
                    style={"transform": "scale(1.2)"},
                ),
            ], className="d-flex justify-content-between align-items-center mb-2 pb-2",
               style={"borderBottom": "2px solid #002145"}),

            # html.Div(id='chart-4-1-container'),
            # html.Div(id='table-4-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            # html.Div(id='table-4-2-container'),
        ], className='pg2-table-plot-box-lgeo'),


        html.Div([
            html.Div([
                html.Div([
                    html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                    html.Span('Indigenous & Non-Indigenous',
                              style={'fontFamily': TABLE_FONT}),
                ]),
                dbc.Switch(
                    id={"type": "table-toggle", "index": "table-4-3"},
                    value=False,
                    label="",
                    className="mb-0",
                    style={"transform": "scale(1.2)"},
                ),
            ], className="d-flex justify-content-between align-items-center mb-2 pb-2",
               style={"borderBottom": "2px solid #002145"}),

            # html.Div(id='chart-4-3-container'),
            # html.Div(id='table-4-3-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            # html.Div(id='table-4-4-container'),
        ], className='pg2-table-plot-box-lgeo'),


        # Section 5 - Income
        html.Div([
            # html.Div(id='table-5-1-container'),
            # html.Div(id='table-5-4-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            html.Div([
                html.Div([
                    html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                    html.Span('Indigenous & Non-Indigenous',
                              style={'fontFamily': TABLE_FONT}),
                ]),
                dbc.Switch(
                    id={"type": "table-toggle", "index": "table-5-5"},
                    value=False,
                    label="",
                    className="mb-0",
                    style={"transform": "scale(1.2)"},
                ),
            ], className="d-flex justify-content-between align-items-center mb-2 pb-2",
               style={"borderBottom": "2px solid #002145"}),

            # html.Div(id='table-5-5-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 7 - Shelter Costs
        html.Div([
            html.Div([
                html.Div([
                    html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                    html.Span('Indigenous & Non-Indigenous',
                              style={'fontFamily': TABLE_FONT}),
                ]),
                dbc.Switch(
                    id={"type": "table-toggle", "index": "table-7-1"},
                    value=False,
                    label="",
                    className="mb-0",
                    style={"transform": "scale(1.2)"},
                ),
            ], className="d-flex justify-content-between align-items-center mb-2 pb-2",
               style={"borderBottom": "2px solid #002145"}),

            # html.Div(id='table-7-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            # html.Div(id='chart-7-3-1-container'),
            # html.Div(id='table-7-3-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 8 - Housing Need Indicators
        html.Div([
            html.Div([
                html.Div([
                    html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                    html.Span('Indigenous & Non-Indigenous',
                              style={'fontFamily': TABLE_FONT}),
                ]),
                dbc.Switch(
                    id={"type": "table-toggle", "index": "table-8-1"},
                    value=False,
                    label="",
                    className="mb-0",
                    style={"transform": "scale(1.2)"},
                ),
            ], className="d-flex justify-content-between align-items-center mb-2 pb-2",
               style={"borderBottom": "2px solid #002145"}),

            # html.Div(id='chart-8-1-container'),
            # html.Div(id='table-8-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        html.Div([
            # html.Div(id='table-8-7-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 9 - Systematic Pathways and Indigenous Homelessness
        html.Div([
            html.Div(id='chart-9-1-container'),
            html.Div(id='table-9-1-container'),
            html.Div(id='table-9-2-container'),
            html.Div(id='table-9-3-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Footer
        html.Footer([
            html.Img(src='./assets/Footer for HNR Calc.png', className='footer-image')
        ], className='footer')

    ], id='page-content-to-print', className='dashboard-pg2-lgeo')

], className='content-container-fullpage')


# Any local switch → rebuild visibility store + derive global state (incl. mixed)
@callback(
    Output("table-visibility-store", "data"),
    Output("global-toggle-btn", "children"),
    Output("global-toggle-btn", "color"),
    Output("global-intent-store", "data"),
    Input({"type": "table-toggle", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def local_toggle_state(toggle_values):
    new_store = {tid: val for tid, val in zip(TABLE_IDS, toggle_values)}
    global_state = derive_global_state(new_store)

    if global_state == "all_on":
        btn_label, btn_color, new_intent = "○ Hide Comparison", "secondary", "all_on"
    elif global_state == "all_off":
        btn_label, btn_color, new_intent = "● Show Comparison", "success", "all_off"
    else:  # mixed — next global click will turn all on
        btn_label, btn_color, new_intent = "◐ Mixed", "warning", "all_on"

    return new_store, btn_label, btn_color, new_intent


# Global button click → set all switches + update store + button state
@callback(
    Output("table-visibility-store", "data", allow_duplicate=True),
    Output("global-toggle-btn", "children", allow_duplicate=True),
    Output("global-toggle-btn", "color", allow_duplicate=True),
    Output("global-intent-store", "data", allow_duplicate=True),
    Output({"type": "table-toggle", "index": ALL}, "value"),
    Input("global-toggle-btn", "n_clicks"),
    State("global-intent-store", "data"),
    prevent_initial_call=True,
)
def global_toggle_click(_, current_intent):
    turn_on = (current_intent == "all_off")
    new_store = {tid: turn_on for tid in TABLE_IDS}

    if turn_on:
        btn_label, btn_color, new_intent = "● Show Comparison", "success", "all_on"
    else:
        btn_label, btn_color, new_intent = "○ Hide Comparison", "secondary", "all_off"

    return new_store, btn_label, btn_color, new_intent, [turn_on] * len(TABLE_IDS)


# Section 2 - Nations / Territories + Métis Communities
@callback(
    Output('table-2-1-container', 'children'),
    Output('table-2-2-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
)
def update_section_2(geo_name, scale):
    geocode = _resolve_geocode(geo_name, scale, section_2_layout.data_loader)
    return (
        section_2_layout.prepare_table_2_1_layout(geocode),
        section_2_layout.prepare_table_2_2_layout(geocode),
    )


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
    geocode = _resolve_geocode(geo_name, scale, section_3_layout.data_loader)

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
    Output('table-4-2-container', 'children'),
    Output('chart-4-3-container', 'children'),
    Output('table-4-3-container', 'children'),
    Output('table-4-4-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('table-visibility-store', 'data'),
)
def update_section_4(geo_name, scale, visibility):
    show_both = (visibility or {}).get("table-4-1", False)
    geocode = _resolve_geocode(geo_name, scale, section_4_layout.data_loader)

    return (
        section_4_layout.create_chart_4_1(geocode),
        section_4_layout.create_table_4_1_layout(geocode, show_both),
        section_4_layout.create_table_4_2_layout(geocode),
        section_4_layout.create_chart_4_3(geocode),
        section_4_layout.create_table_4_3_layout(geocode, show_both),
        section_4_layout.create_table_4_4_layout(geocode),
    )


@callback(
    Output('table-5-1-container', 'children'),
    Output('table-5-4-container', 'children'),
    Output('table-5-5-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('table-visibility-store', 'data'),
)
def update_section_5(geo_name, scale, visibility):
    show_both = (visibility or {}).get("table-5-5", False)
    geocode = _resolve_geocode(geo_name, scale, section_5_layout.data_loader)

    return (
        section_5_layout.create_table_5_1_layout(geocode),
        section_5_layout.create_table_5_4_layout(geocode),
        section_5_layout.create_table_5_5_layout(geocode, show_both),
        )


@callback(
    Output('table-7-1-container', 'children'),
    Output('chart-7-3-1-container', 'children'),
    Output('table-7-3-1-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('table-visibility-store', 'data'),
)
def update_section_7(geo_name, scale, visibility):
    show_both = (visibility or {}).get("table-7-1", False)
    geocode = _resolve_geocode(geo_name, scale, section_7_layout.data_loader)
    return (
        section_7_layout.create_table_7_1_layout(geocode, show_both),
        section_7_layout.create_chart_7_3_1(geocode),
        section_7_layout.create_table_7_3_1_layout(geocode)
        )


@callback(
    Output('chart-8-1-container', 'children'),
    Output('table-8-1-container', 'children'),
    Output('table-8-7-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('table-visibility-store', 'data'),
)
def update_section_8(geo_name, scale, visibility):
    show_both = (visibility or {}).get("table-8-1", False)
    geocode = _resolve_geocode(geo_name, scale, section_8_layout.data_loader)

    return (
        section_8_layout.create_chart_8_1(geocode),
        section_8_layout.create_table_8_1_layout(geocode, show_both),
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
    geocode = _resolve_geocode(geo_name, scale, section_9_layout.data_loader)

    return (
        section_9_layout.create_chart_9_1(geocode),
        section_9_layout.create_table_9_1_layout(geocode),
        section_9_layout.create_table_9_2_layout(geocode),
        section_9_layout.create_table_9_3_layout(geocode)
    )


# Helper function to share geocode resolution logic
def _resolve_geocode(geo_name, scale, data_loader):
    if geo_name is None:
        from dashboard_helpers.config import DEFAULT_GEOGRAPHY
        geo_name = DEFAULT_GEOGRAPHY

    geocode = data_loader.get_geocode(geo_name)

    if geocode is None:
        geocode = DEFAULT_GEOCODE
    else:
        try:
            geocode = int(geocode)
        except (ValueError, TypeError):
            geocode = DEFAULT_GEOCODE

    if scale == 'to-region-1':
        region = data_loader.get_region_geocode(geocode)
        geocode = int(region) if region is not None else geocode
    elif scale == 'to-province-1':
        province = data_loader.get_province_geocode(geocode)
        geocode = int(province) if province is not None else geocode

    return geocode

