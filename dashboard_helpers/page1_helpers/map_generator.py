"""
Map generation utilities for dashboard.
"""
import json
import numpy as np
import plotly.graph_objects as go
from dashboard_helpers.page1_helpers.data_loader import DataLoader
from dashboard_helpers.config import (
    MAP_COLORS_WO_BLACK, MAP_COLORS_HIGHLIGHT,
    OPACITY_VALUE, MODEBAR_COLOR,
    MODEBAR_ACTIVECOLOR, PROVINCE_CODE
)


class MapGenerator:
    """Generates interactive Plotly maps."""

    def __init__(self):
        self.data_loader = DataLoader()

    def create_province_map(self, selected_geography: str = None, highlight: bool = False) -> go.Figure:
        """Create province-level map."""
        gdf = self.data_loader.province_gdf.copy()

        if highlight and selected_geography:
            info = self.data_loader.get_geography_info(selected_geography)
            gdf['rand'] = gdf.index.map(
                lambda x: 0 if x == int(info['province_code']) else 100
            )
            colors = MAP_COLORS_HIGHLIGHT
        else:
            gdf['rand'] = 0
            colors = MAP_COLORS_WO_BLACK

        fig = go.Figure()
        fig.add_trace(go.Choroplethmapbox(
            geojson=json.loads(gdf.geometry.to_json()),
            locations=gdf.index,
            z=gdf['rand'],
            showscale=False,
            colorscale=colors,
            text=gdf['NAME'],
            hovertemplate='%{text} - %{location}<extra></extra>',
            marker=dict(opacity=OPACITY_VALUE),
            marker_line_width=0.5
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={
                "lat": gdf['lat'].mean(),
                "lon": gdf['lon'].mean()
            },
            mapbox_zoom=3.8,
            margin=dict(b=0, t=10, l=0, r=10),
            modebar_color=MODEBAR_COLOR,
            modebar_activecolor=MODEBAR_ACTIVECOLOR,
            autosize=True
        )

        return fig

    def create_region_map(self, selected_geography: str = None,
                          highlight: bool = False,
                          region_code: str = None) -> go.Figure:
        """Create region (CD) level map."""
        if region_code:
            gdf = self.data_loader.load_region_gdf(int(region_code[:2]))
        elif selected_geography:
            info = self.data_loader.get_geography_info(selected_geography)
            gdf = self.data_loader.load_region_gdf(int(info['province_code']))
        else:
            gdf = self.data_loader.load_region_gdf(PROVINCE_CODE)

        if highlight and selected_geography:
            info = self.data_loader.get_geography_info(selected_geography)
            gdf['rand'] = gdf.index.map(
                lambda x: 0 if str(x) == info['region_code'] else 100
            )
            colors = MAP_COLORS_HIGHLIGHT
        else:
            gdf['rand'] = np.arange(len(gdf))
            colors = MAP_COLORS_WO_BLACK

        fig = go.Figure()
        fig.add_trace(go.Choroplethmapbox(
            geojson=json.loads(gdf.geometry.to_json()),
            locations=gdf.index,
            z=gdf['rand'],
            showscale=False,
            colorscale=colors,
            text=gdf['CDNAME'],
            hovertemplate='%{text} - %{location}<extra></extra>',
            marker=dict(opacity=OPACITY_VALUE),
            marker_line_width=0.5
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={
                "lat": gdf['lat'].mean() + 3,
                "lon": gdf['lon'].mean()
            },
            mapbox_zoom=4.0,
            margin=dict(b=0, t=10, l=0, r=10),
            modebar_color=MODEBAR_COLOR,
            modebar_activecolor=MODEBAR_ACTIVECOLOR,
            autosize=True
        )

        return fig

    def create_subregion_map(self, selected_geography: str = None,
                             highlight: bool = False,
                             subregion_code: str = None) -> go.Figure:
        """Create subregion (CSD) level map."""
        if subregion_code:
            region_code = int(subregion_code[:4])
        elif selected_geography:
            info = self.data_loader.get_geography_info(selected_geography)
            region_code = int(info['region_code'])
        else:
            return self.create_region_map()

        gdf = self.data_loader.load_subregion_gdf(region_code)

        if gdf is None:
            # Fallback to region map
            return self.create_region_map(selected_geography, highlight)

        if highlight and selected_geography:
            info = self.data_loader.get_geography_info(selected_geography)
            gdf['rand'] = gdf.index.map(
                lambda x: 50 if str(x) == info['geo_code'] else 100
            )
            colors = MAP_COLORS_HIGHLIGHT
        else:
            gdf['rand'] = np.random.randint(30, 100, len(gdf))
            colors = MAP_COLORS_WO_BLACK

        fig = go.Figure()
        fig.add_trace(go.Choroplethmapbox(
            geojson=json.loads(gdf.geometry.to_json()),
            locations=gdf.index,
            z=gdf['rand'],
            showscale=False,
            colorscale=colors,
            text=gdf['CSDNAME'],
            hovertemplate='%{text} - %{location}<extra></extra>',
            marker=dict(opacity=OPACITY_VALUE),
            marker_line_width=0.5
        ))

        # Calculate zoom level
        max_bound = max(
            abs(gdf['lat'].max() - gdf['lat'].min()),
            abs(gdf['lon'].max() - gdf['lon'].min())
        ) * 111
        zoom = 11.5 - np.log(max_bound) if max_bound > 0 else 9

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={
                "lat": gdf['lat'].mean(),
                "lon": gdf['lon'].mean()
            },
            mapbox_zoom=zoom,
            margin=dict(b=0, t=10, l=0, r=10),
            modebar_color=MODEBAR_COLOR,
            modebar_activecolor=MODEBAR_ACTIVECOLOR,
            autosize=True
        )

        return fig