# Import necessary libraries
from dash import html, dcc, callback_context, no_update, Input, Output, State, ALL
from flask_compress import Compress

from app_file import app

# Connect to app pages
from pages import map_picker, indig_territory, tab1, tab2, tab3, tab4
from dashboard_helpers.content_helpers.export_helpers import table_to_excel
from dashboard_helpers.content_helpers.data_loader import get_data_loader, resolve_geocode

# Preload every DB table before gunicorn starts accepting requests. Running
# this in a background thread let the app become reachable sooner, but meant
# whichever visitor arrived first could still land mid-warm-up and hit
# un-cached tables - blocking here guarantees no request is ever served
# against a partially-warmed cache, at the cost of a few extra seconds on
# every cold boot.
get_data_loader().warm_cache()


# Define the index page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[]),
    # jsPDF/html2canvas/html2pdf are already served locally from assets/ (Dash
    # auto-injects every .js file found there) - loading them again here from
    # external CDNs was duplicating ~2.5MB of downloads on every first page
    # load for no benefit.
    dcc.Download(id="download-dataframe-xlsx"),
    dcc.Store(id='display-geo-name', storage_type='memory'),
])

server = app.server

# Compresses every text response (JS/CSS assets, HTML, callback JSON) on the
# way out - plotly.js and html2pdf.bundle.js in particular go from several MB
# down to a fraction of that over the wire. No compression was configured
# anywhere before this.
Compress(server)


# Create the callback to handle multipage inputs
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/map_picker':
        return map_picker.layout
    elif pathname == '/indig_territory':
        return indig_territory.layout
    elif pathname == '/tab1':
        return tab1.layout
    elif pathname == '/tab2':
        return tab2.layout
    elif pathname == '/tab3':
        return tab3.layout
    elif pathname == '/tab4':
        return tab4.layout
    else:
        return "404 Page Error! Please choose a link"


@app.callback(
    Output('display-geo-name', 'data'),
    Input('main-area', 'data'),
    Input('area-scale-store', 'data'),
)
def update_display_geo_name(geo_name, scale):
    """Track the geography actually shown (post 'Show Region'/'Show Province'
    scale-up), since main-area keeps the raw dropdown pick unchanged - used so
    PDF export filenames match what's on screen instead of the stale dropdown value."""
    loader = get_data_loader()
    geocode = resolve_geocode(geo_name, scale, loader)
    return loader.get_geography_name(geocode) or geo_name


app.clientside_callback(
      """
    async function(n_clicks, geo, displayGeo, pathname){
        if (n_clicks > 0 && geo){
            // Name the PDF after the tab it was exported from.
            var tabNames = {
                '/tab1': 'Who lives here',
                '/tab2': 'How are people housed',
                '/tab3': 'Where does the system fail',
                '/tab4': 'What is needed'
            };
            var tab = tabNames[pathname];
            var geoLabel = displayGeo || geo;
            var filename = (tab ? tab + ' - ' + geoLabel : geoLabel) + '.pdf';
            var opt = {
                margin: 1,
                filename: filename,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 3},
                jsPDF: { unit: 'cm', format: 'a2', orientation: 'p' },
                pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
            };

            var container = document.getElementById("page-content-to-print");
            var originalWidth = container.style.width;
            var originalMaxWidth = container.style.maxWidth;
            var plots = container.querySelectorAll('.js-plotly-plot');
            var scrollables = [];

            // Everything that mutates the live DOM - including the setup below -
            // must be inside this try so a mid-setup error can't leave the page
            // permanently moved off-screen (which showed as "dashboard flashes
            // white and stays blank").
            try {
                // Tables use overflowX:'auto' (get_base_table_style), so any
                // table wider than its box scrolls on screen - html2canvas
                // can't capture content scrolled out of view inside a nested
                // scrollable/clipped element. DataTable's internal markup also
                // uses overflow:hidden on some wrapper divs (frozen-column
                // support), which clips overflowing content outright with no
                // visible scrollbar. Force all of these to overflow:visible so
                // the full table renders.
                container.querySelectorAll('*').forEach(function(el){
                    var cs = window.getComputedStyle(el);
                    if (cs.overflowX === 'auto' || cs.overflowX === 'scroll' || cs.overflowX === 'hidden') {
                        scrollables.push({el: el, overflowX: el.style.overflowX});
                        el.style.overflowX = 'visible';
                    }
                });

                // .dashboard-pg2-lgeo is width:90%, so its rendered pixel width
                // - and every chart's - depends on whichever window/monitor
                // triggered the export. Pin it to a fixed width and force each
                // chart to actually re-layout at that width before capture, so
                // exports are identical regardless of the triggering device.
                container.style.width = '1200px';
                container.style.maxWidth = '1200px';
                if (window.Plotly) {
                    plots.forEach(function(p){ Plotly.Plots.resize(p); });
                }

                // Give the resize/re-render a moment to finish before capturing.
                await new Promise(function(resolve){ setTimeout(resolve, 300); });

                await html2pdf().from(container).set(opt).save();
            } finally {
                container.style.width = originalWidth;
                container.style.maxWidth = originalMaxWidth;
                scrollables.forEach(function(s){ s.el.style.overflowX = s.overflowX; });
                if (window.Plotly) {
                    plots.forEach(function(p){ Plotly.Plots.resize(p); });
                }
            }
        }
    }
    """,
    Output('dummy-output', 'children'),
    Input('export-btn', 'n_clicks'),
    State('main-area', 'data'),
    State('display-geo-name', 'data'),
    State('url', 'pathname')
)

@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input({"type": "export-btn", "index": ALL}, "n_clicks"),
    State({"type": "export-data", "index": ALL}, "data"),
    State({"type": "export-cols", "index": ALL}, "data"),
    State({"type": "export-title", "index": ALL}, "data"),
    prevent_initial_call=True,
)
def download_xlsx(n_clicks_list, all_data, all_cols, title):
    if not callback_context.triggered:
        return no_update

    triggered_id = callback_context.triggered_id
    if not isinstance(triggered_id, dict) or triggered_id.get("type") != "export-btn":
        return no_update

    # When a section rebuilds, Dash re-fires this callback for newly added export
    # buttons whose n_clicks is None. Only proceed on an actual user click (n_clicks > 0).
    if not callback_context.triggered[0]["value"]:
        return no_update

    table_id = triggered_id["index"]

    # states_list[0] is the list of matched export-data stores
    store_ids = [item["id"]["index"] for item in callback_context.states_list[0]]
    if table_id not in store_ids:
        return no_update

    idx = store_ids.index(table_id)
    return table_to_excel(all_cols[idx], all_data[idx], f"{table_id}.xlsx", title[idx])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
