"""
Export to excel functionality for page 2 DataTables.
"""
from io import BytesIO
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard_helpers.config import TABLE_FONT

def with_export_btn(table_component, table_id: str, max_width: str = None):

    # Base layout styles
    wrapper_style = {"width": "100%"}
    
    # Dynamically adjust maximum width restriction if provided
    if max_width:
        wrapper_style["maxWidth"] = max_width

    return html.Div([
        dcc.Store(
            id={"type": "export-data", "index": table_id},
            data=table_component.data,
        ),
        dcc.Store(
            id={"type": "export-cols", "index": table_id},
            data=table_component.columns,
        ),
        html.Div(
            dbc.Button(
                "Export",
                id={"type": "export-btn", "index": table_id},
                outline=True,
                className="export-xlsx-btn",
            ),
            style={
                "display": "flex",
                "justifyContent": "flex-end",
                "paddingBottom": "10px",
                "fontFamily": TABLE_FONT
            }
        ),
        # html.Br(),
        table_component,
        
    ], style=wrapper_style)



def table_to_excel(columns: list, records: list, filename: str):
    """Convert DataTable columns + records to a dcc.send_bytes response."""
    if not records or not columns:
        return None

    col_names = []
    for c in columns:
        name = c["name"]
        if isinstance(name, list):
            name = " > ".join(part for part in name if part)
        col_names.append(name)

    col_ids = [c["id"] for c in columns]

    df = pd.DataFrame(records).reindex(columns=col_ids)
    df.columns = col_names

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return dcc.send_bytes(output.read(), filename)
