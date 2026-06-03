"""
Dashboard page 1: Geography selection with interactive map.
"""
from dash import dcc, html, Input, Output, ctx, callback
from dashboard_helpers.page1_helpers.data_loader import DataLoader
from dashboard_helpers.page1_helpers.map_generator import MapGenerator
from dashboard_helpers.config import DEFAULT_GEOGRAPHY, PLOT_CONFIG, PROVINCE_CODE

# Initialize data loader and map generator
data_loader = DataLoader()
map_generator = MapGenerator()

# Get dropdown options
dropdown_options = data_loader.dropdown_options['Geography'].unique()

# Create default map
default_map = map_generator.create_subregion_map(selected_geography=DEFAULT_GEOGRAPHY, highlight=True)

# Layout
layout = html.Div(
    children=[
        # Storage components
        dcc.Store(id='area-scale-store', storage_type='local'),
        dcc.Store(id='main-area', storage_type='local'),
        dcc.Store(id='comparison-area', storage_type='local'),

        # Main content
        html.Div(
            children=[
                # Dropdown section
                html.Div(
                    children=[
                        # Main area dropdown
                        html.Div(
                            id='all-geo-dropdown-parent',
                            children=[
                                html.Strong('Select or Search Census Geography'),
                                dcc.Dropdown(
                                    dropdown_options,
                                    DEFAULT_GEOGRAPHY,
                                    id='all-geo-dropdown',
                                    placeholder='Select or search geography'
                                ),
                            ],
                            className='dropdown-lgeo'
                        ),

                    ],
                    className='dropdown-box-lgeo'
                ),

                # Scale buttons
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Button(
                                    'View Municipalities',
                                    title='A provincially-legislated area at the municipal scale',
                                    id='to-geography-1',
                                    n_clicks=0,
                                    className='button-lgeo'
                                ),
                            ],
                            className='region-button-box-lgeo'
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    'View Regions',
                                    title='A provincially legislated area like counties or regional districts',
                                    id='to-region-1',
                                    n_clicks=0,
                                    className='button-lgeo'
                                ),
                            ],
                            className='region-button-box-lgeo'
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    'View Province',
                                    title='Province of British Columbia',
                                    id='to-province-1',
                                    n_clicks=0,
                                    className='button-lgeo'
                                ),
                            ],
                            className='region-button-box-lgeo'
                        ),
                    ],
                    className='scale-button-box-lgeo'
                ),

                # Map section
                html.Div(
                    children=[
                        html.Div(
                            dcc.Graph(
                                id='canada_map',
                                figure=default_map,
                                config=PLOT_CONFIG,
                            ),
                            className='map-lgeo'
                        ),

                        # Reset button
                        html.Div(
                            children=[
                                html.Button('Reset Map', 
                                            id='reset-map', 
                                            n_clicks=0,
                                            className='button-lgeo'
                                            ),
                                
                            ],
                            className='reset-button-lgeo'
                        ),
                    ],
                    className='map-area-box-lgeo'
                ),
            ],
            className='dashboard-pg1-lgeo'
        ),
    ],
    className='background-lgeo'
)


# Callbacks
@callback(
    Output('main-area', 'data'),
    Output('comparison-area', 'data'),
    Output('area-scale-store', 'data'),
    Input('all-geo-dropdown', 'value'),
    Input('all-geo-dropdown-parent', 'n_clicks'),
    Input('to-geography-1', 'n_clicks'),
    Input('to-region-1', 'n_clicks'),
    Input('to-province-1', 'n_clicks')
)
def store_geography(geo, geo_c, *args):
    """Store selected geographies and scale level."""
    triggered_id = str(ctx.triggered_id)
    return geo, geo_c, triggered_id


@callback(
    Output('canada_map', 'figure'),
    Output('all-geo-dropdown', 'value'),
    Input('canada_map', 'clickData'),
    Input('reset-map', 'n_clicks'),
    Input('all-geo-dropdown', 'value'),
    Input('all-geo-dropdown-parent', 'n_clicks'),
    Input('to-geography-1', 'n_clicks'),
    Input('to-region-1', 'n_clicks'),
    Input('to-province-1', 'n_clicks')
)
def update_map(click_data, reset_clicks, selected_geo, *args):
    """Update map based on user interactions."""
    triggered_id = ctx.triggered_id

    # Default value
    if selected_geo is None:
        selected_geo = DEFAULT_GEOGRAPHY

    # Get geography info
    geo_info = data_loader.get_geography_info(selected_geo)
    if geo_info is None:
        return default_map, DEFAULT_GEOGRAPHY

    level = geo_info['level']

    # Handle reset
    if triggered_id == 'reset-map':
        fig = map_generator.create_region_map(region_code=str(PROVINCE_CODE))
        return fig, DEFAULT_GEOGRAPHY

    # Handle scale button clicks
    if triggered_id == 'to-province-1':
        fig = map_generator.create_province_map(selected_geo, highlight=True)
        return fig, selected_geo

    if triggered_id == 'to-region-1':
        if level == 'province':
            fig = map_generator.create_region_map(selected_geo, highlight=False)
        else:
            fig = map_generator.create_region_map(selected_geo, highlight=True)
        return fig, selected_geo

    if triggered_id == 'to-geography-1':
        if level in ['province', 'cd']:
            fig = map_generator.create_region_map(selected_geo, highlight=True)
        else:
            fig = map_generator.create_subregion_map(selected_geo, highlight=True)
        return fig, selected_geo

    # Handle dropdown selection
    if triggered_id == 'all-geo-dropdown-parent':
        if level == 'province':
            fig = map_generator.create_province_map(selected_geo, highlight=True)
        elif level == 'cd':
            fig = map_generator.create_region_map(selected_geo, highlight=True)
        else:  # csd
            fig = map_generator.create_subregion_map(selected_geo, highlight=True)
        return fig, selected_geo

    # Handle map clicks
    if click_data:
        clicked_code = str(click_data['points'][0]['location'])
        clicked_level = data_loader._determine_level(clicked_code)

        if clicked_level == 'province':
            fig = map_generator.create_region_map(region_code=clicked_code)
            geo_name = data_loader.province_list.query(
                f"Geo_Code == '{clicked_code}'"
            )['Geography'].iloc[0]
            return fig, geo_name

        elif clicked_level == 'cd':
            fig = map_generator.create_subregion_map(subregion_code=clicked_code)
            geo_name = data_loader.region_list.query(
                f"Geo_Code == '{clicked_code}'"
            )['Geography'].iloc[0]
            return fig, geo_name

        else:  # csd            
            match = data_loader.geocode_master[
                data_loader.geocode_master['Geo_Code'] == clicked_code
                ]
            if not match.empty:
                geo_name = match['Geography'].iloc[0]

                fig = map_generator.create_subregion_map(subregion_code=clicked_code, 
                                                     highlight=True, selected_geography=geo_name)
                return fig, geo_name

    # Default: show region map
    # fig = map_generator.create_subregion_map(selected_geography=DEFAULT_GEOGRAPHY, highlight=True)
    fig = map_generator.create_region_map(selected_geography=DEFAULT_GEOGRAPHY, highlight=False)
    return fig, DEFAULT_GEOGRAPHY