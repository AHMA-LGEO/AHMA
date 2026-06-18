"""
Dashboard page Indigenous Territory: List of Traditional Territories and Metis Communities - below map picker
"""

from dashboard_helpers.indigeneous_helper.section_2 import Section2Prep
from dash import dcc, html, Input, Output, callback

from dashboard_helpers.content_helpers.data_loader import resolve_geocode

# Initialize helpers
section_2_layout = Section2Prep()

layout = html.Div([
    # Stores
    dcc.Store(id='main-area', storage_type='local'),
    dcc.Store(id='comparison-area', storage_type='local'),
    dcc.Store(id='area-scale-store', storage_type='local'),

    html.Div([
        html.Div([
            html.Div(id='table-2-1-container'),
            html.Div(id='table-2-2-container'),
        ], className='pg2-table-plot-box-lgeo'),

    ], id='page-content-to-print', className='dashboard-pg2-lgeo')

], className='content-container-fullpage')


# Section 2 - Nations / Territories + Métis Communities
@callback(
    Output('table-2-1-container', 'children'),
    Output('table-2-2-container', 'children'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
)
def update_section_2(geo_name, scale):
    geocode = resolve_geocode(geo_name, scale, section_2_layout.data_loader)
    return (
        section_2_layout.prepare_table_2_1_layout(geocode),
        section_2_layout.prepare_table_2_2_layout(geocode),
    )

