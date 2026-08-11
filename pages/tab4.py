"""
Dashboard Tab 4: What is needed? Covers: Population and Household Growth (Section 11) and Housing Targets (Section 12)
"""
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from dashboard_helpers.tab4_helpers.section_11 import Section11Prep
from dashboard_helpers.tab4_helpers.section_12 import Section12Prep

from dashboard_helpers.content_helpers.data_loader import resolve_geocode

# Initialize helpers
section_11_layout = Section11Prep()
section_12_layout = Section12Prep()

layout = html.Div([
    # Stores
    dcc.Store(id='main-area', storage_type='local'),
    dcc.Store(id='comparison-area', storage_type='local'),
    dcc.Store(id='area-scale-store', storage_type='local'),

    # Export button
    dbc.Button("Export to PDF", id="export-btn", className="export-pdf"),
    html.Div(id='dummy-output', style={'display': 'none'}),
        

    html.Div([
    # Section 11 - Population & Household Growth
        html.Div([
            html.Div(id='table-11-1-1-container'),
            html.Div(id='table-11-1-2-container'),
        ], className='pg2-table-plot-box-lgeo'),

        # Section 12 - Housing Targets
        html.Div([
            html.Div(id='table-12-1-container'),
            html.Div(id='table-12-2-container'),
        ], className='pg2-table-plot-box-lgeo'),


    ], id='page-content-to-print', className='dashboard-pg2-lgeo')
], className='content-container-fullpage')



@callback(
    Output('table-11-1-1-container', 'children'),
    Output('table-11-1-2-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data')
)
def update_section_11(geo_name, scale):
    geocode = resolve_geocode(geo_name, scale, section_11_layout.data_loader)

    return (
        section_11_layout.create_table_11_1_1_layout(geocode),
        section_11_layout.create_table_11_1_2_layout(geocode),
        )



@callback(
    Output('table-12-1-container', 'children'),
    Output('table-12-2-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data')
)
def update_section_12(geo_name, scale):
    geocode = resolve_geocode(geo_name, scale, section_12_layout.data_loader)

    return (
        section_12_layout.create_table_12_1_layout(),
        section_12_layout.create_table_12_2_layout(geocode),
    )