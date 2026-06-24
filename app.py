# Import necessary libraries
from dash import html, dcc, callback_context, no_update, Input, Output, State, ALL

from app_file import app

# Connect to app pages
from pages import map_picker, indig_territory, tab1, tab2, tab3, tab4
from dashboard_helpers.content_helpers.export_helpers import table_to_excel


# Define the index page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[]),
    # Add external scripts for jsPDF and html2canvas
    html.Script(src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.4.0/jspdf.umd.min.js"),
    html.Script(src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"),
    html.Script(src="https://raw.githack.com/eKoopmans/html2pdf/master/dist/html2pdf.bundle.js"),
    dcc.Download(id="download-dataframe-xlsx"),
    # Fires a few times after page load so all charts get relayout'd at correct container size
    dcc.Interval(id='autosize-interval', interval=1000, max_intervals=8, n_intervals=0),
    html.Div(id='autosize-dummy', style={'display': 'none'}),
])

server = app.server


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

app.clientside_callback(
      """
    function(n_clicks, geo){
        if (n_clicks > 0 && geo){
            var opt = {
                margin: 1,
                filename: geo + '.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 3},
                jsPDF: { unit: 'cm', format: 'a2', orientation: 'p' },
                pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
            };
            html2pdf().from(document.getElementById("page-content-to-print")).set(opt).save();
        }
    }
    """,
    Output('dummy-output', 'children'),
    Input('export-btn', 'n_clicks'),
    State('main-area', 'data')
)

app.clientside_callback(
    """
    function(n) {
        if (window.Plotly) {
            document.querySelectorAll('.js-plotly-plot').forEach(function(el) {
                try { window.Plotly.relayout(el, {autosize: true}); } catch(e) {}
            });
        }
        return null;
    }
    """,
    Output('autosize-dummy', 'children'),
    Input('autosize-interval', 'n_intervals'),
    prevent_initial_call=True,
)

@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input({"type": "export-btn", "index": ALL}, "n_clicks"),
    State({"type": "export-data", "index": ALL}, "data"),
    State({"type": "export-cols", "index": ALL}, "data"),
    prevent_initial_call=True,
)
def download_xlsx(n_clicks_list, all_data, all_cols):
    if not callback_context.triggered or all((n or 0) == 0 for n in n_clicks_list):
        return no_update

    triggered_id = callback_context.triggered_id
    if not isinstance(triggered_id, dict) or triggered_id.get("type") != "export-btn":
        return no_update

    table_id = triggered_id["index"]

    # states_list[0] is the list of matched export-data stores
    store_ids = [item["id"]["index"] for item in callback_context.states_list[0]]
    if table_id not in store_ids:
        return no_update

    idx = store_ids.index(table_id)
    return table_to_excel(all_cols[idx], all_data[idx], f"{table_id}.xlsx")

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
