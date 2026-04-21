"""
Dashboard page 2: Housing needs tables and analysis.
"""
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc

from helpers.page2_helpers.section_2 import Section2Prep
from helpers.page2_helpers.section_4 import Section4Prep
from helpers.page2_helpers.section_8 import Section8Prep
# from helpers.page2_helpers.table_4_2_prep import Table42Prep
# from helpers.page2_helpers.chart_4_prep import Chart4Prep
from helpers.page2_helpers.text_content import (
    INTRO_TITLE, INTRO_TEXT
)
from helpers.config import DEFAULT_GEOCODE, PLOT_CONFIG

# Initialize helpers
section_2_layout = Section2Prep()
section_4_layout = Section4Prep()
section_8_layout = Section8Prep()

# Table IDs — add new table IDs with toggle features as page 2 grows
TABLE_IDS = ["table-4-1", "table-8-1"]


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
                        children="○ Hide Comparison",
                        color="secondary",
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
            ], style={'fontFamily': 'Bahnschrift'})
        ], className='muni-reg-text-lgeo'),

        # Section 2 – Nations / Territories and Métis Communities
        html.Div([
            html.Div(id='section-2-1-container'),
            html.Div(id='section-2-2-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Table 4.1 Section
        html.Div([
            html.Div([
                html.Div([
                    html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                    html.Span('Indigenous & Non-Indigenous',
                              style={'fontFamily': 'Bahnschrift'}),
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

            html.Div(id='chart-4-1-container'),
            html.Div(id='table-4-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Table 8.1 Section
        html.Div([
            html.Div([
                html.Div([
                    html.Strong('Show Comparison: ', style={'marginRight': '6px'}),
                    html.Span('Indigenous & Non-Indigenous',
                              style={'fontFamily': 'Bahnschrift'}),
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

            html.Div(id='chart-8-1-container'),
            html.Div(id='table-8-1-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Table 4.2 Section (Indigenous only)
        # html.Div(
        #     id='table-4-2-container',
        #     className='pg2-table-plot-box-lgeo'
        # ),

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
        btn_label, btn_color, new_intent = "● Show Comparison", "success", "all_on"
    elif global_state == "all_off":
        btn_label, btn_color, new_intent = "○ Hide Comparison", "secondary", "all_off"
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


# Section 2 – Nations / Territories + Métis Communities
@callback(
    Output('section-2-1-container', 'children'),
    Output('section-2-2-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
)
def update_section_2(geo_name, scale):
    geocode = _resolve_geocode(geo_name, scale, section_2_layout.data_loader)
    return (
        section_2_layout.create_section_2_1_layout(geocode),
        section_2_layout.create_section_2_2_layout(geocode),
    )


# Table update — reads show_both from visibility store
@callback(
    Output('chart-4-1-container', 'children'),
    Output('table-4-1-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('table-visibility-store', 'data'),
)
def update_table_4_1(geo_name, scale, visibility):
    """Update Table 4.1 and Chart based on selection."""
    show_both = (visibility or {}).get("table-4-1", False)
    geocode = _resolve_geocode(geo_name, scale, section_4_layout.data_loader)

    table_layout = section_4_layout.create_table_4_1_layout(geocode, show_both)
    chart_fig = section_4_layout.create_chart_4_1(geocode)

    chart_layout = dcc.Graph(
        id='chart-4-1',
        figure=chart_fig,
        config=PLOT_CONFIG
    )
    
    return chart_layout, table_layout


@callback(
    Output('chart-8-1-container', 'children'),
    Output('table-8-1-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('table-visibility-store', 'data'),
)
def update_table_8_1(geo_name, scale, visibility):
    """Update Table 8.1 and Chart 8.1 based on geography selection."""
    show_both = (visibility or {}).get("table-8-1", False)
    geocode = _resolve_geocode(geo_name, scale, section_8_layout.data_loader)

    table = section_8_layout.create_table_8_1_layout(geocode, show_both)
    chart_fig = section_8_layout.create_chart_8_1(geocode)

    chart = dcc.Graph(id='chart-8-1', figure=chart_fig, config=PLOT_CONFIG)

    return chart, table


# @callback(
#     Output('table-4-2-container', 'children'),
#     Input('main-area', 'data'),
#     Input('area-scale-store', 'data'),
#     Input('household-type-toggle', 'value')
# )
# def update_table_4_2(geo_name, scale, household_type):
#     """Update Table 4.2 - only show for Indigenous households."""
#     # Only show for Indigenous HHs
#     if household_type != 'Indigenous HHs':
#         return html.Div()

#     # Get geocode
#     if geo_name is None:
#         from helpers.config import DEFAULT_GEOGRAPHY
#         geo_name = DEFAULT_GEOGRAPHY

#     geocode = table_4_layout.data_loader.get_geocode(geo_name)

#     if geocode is None:
#         geocode = DEFAULT_GEOCODE

#     # Handle scale changes
#     if scale == 'to-region-1':
#         geocode = table_4_layout.data_loader.get_region_geocode(geocode)
#     elif scale == 'to-province-1':
#         geocode = table_4_layout.data_loader.get_province_geocode(geocode)

#     # Create table
#     return table_4_2_prep.create_table_layout(geocode)


# Helper function to share geocode resolution logic
def _resolve_geocode(geo_name, scale, data_loader):
    if geo_name is None:
        from helpers.config import DEFAULT_GEOGRAPHY
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

