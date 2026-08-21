"""
Export to excel functionality for page 2 DataTables.
"""
from io import BytesIO
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard_helpers.config import TABLE_FONT

def with_export_btn(table_component, table_id: str, max_width: str = '1200px',
                    export_data: list = None, export_columns: list = None,
                    title: str = None):
    """
    Wrap a DataTable with an Export button.

    export_data / export_columns override what the button writes to the xlsx.
    Use them when a table is split into several visual DataTables (e.g. to repeat
    a merged geography header) but should still export as a single sheet.

    title renders a centred heading directly above the table, mirroring the
    in-figure titles used by the charts. It sits below the Export button so the
    button keeps its position beside any toggle above the table.
    """

    # Base layout styles. margin: '0 auto' centers the block within its parent
    # once maxWidth caps it narrower - the same effect table 3.3/3.6 got by
    # wrapping this call in an extra "d-flex align-items-center" div, applied
    # once here instead of at every call site.
    wrapper_style = {"width": "100%", "margin": "0 auto"}

    # Dynamically adjust maximum width restriction if provided
    if max_width:
        wrapper_style["maxWidth"] = max_width

    title_block = [
        html.H6(title, className='table-title',
                style={"textAlign": "center", "fontFamily": TABLE_FONT})
    ] if title else []

    table_data = table_component.data if export_data is None else export_data
    table_cols = table_component.columns if export_columns is None else export_columns

    # if title:
    #     # Add a title row using the first column
    #     # and blanks for the remaining columns.
    #     n_cols = len(table_cols)

    #     title_row = {
    #         col["id"]: title if i == 0 else ""
    #         for i, col in enumerate(table_cols)
    #     }

    #     table_data = [title_row] + table_data

    return html.Div([
        dcc.Store(
            id={"type": "export-data", "index": table_id},
            data=table_data,
        ),
        dcc.Store(
            id={"type": "export-cols", "index": table_id},
            data=table_cols,
        ),
        dcc.Store(
            id={"type": "export-title", "index": table_id},
            data=title,
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
        *title_block,
        table_component,

    ], style=wrapper_style)



def table_to_excel(columns: list, records: list, filename: str, title: str = None):
    """Convert DataTable columns + records to a dcc.send_bytes response."""
    if not records or not columns:
        return None

    # col_names = []
    # for c in columns:
    #     name = c["name"]
    #     if isinstance(name, list):
    #         name = " > ".join(part for part in name if part)
    #     col_names.append(name)

    col_ids = [c["id"] for c in columns]

    header_names = []
    for c in columns:
        name = c["name"]

        if isinstance(name, list):
            levels = ["" if part is None else str(part)
                      for part in name]
        else:
            levels = [str(name)]

        header_names.append(levels)

    n_header_rows = max(len(levels) for levels in header_names)

    header_matrix = []
    for level in range(n_header_rows):
        row = []
        for levels in header_names:
            if level < len(levels):
                row.append(levels[level])
            else:
                row.append("")

        header_matrix.append(row)


    df = pd.DataFrame(records).reindex(columns=col_ids)
    # df.columns = col_names

    output = BytesIO()
    # with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    #     df.to_excel(writer, index=False)
    # output.seek(0)
    # return dcc.send_bytes(output.read(), filename)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        workbook = writer.book
        worksheet = workbook.add_worksheet("Sheet1")

        # Don't let pandas create another worksheet
        writer.sheets["Sheet1"] = worksheet

        # -----------------------------------------------------
        # Formats
        # -----------------------------------------------------
        title_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "font_size": 14,
        })

        header_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        })

        data_format = workbook.add_format({
            "border": 1,
            "valign": "vcenter",
        })

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------
        current_row = 0

        if title:
            worksheet.merge_range(current_row, 0,
                current_row, len(col_ids) - 1,
                title, title_format)

            current_row += 1

        # -----------------------------------------------------
        # Multi-level headers
        # -----------------------------------------------------
        header_start_row = current_row

        for level, row_values in enumerate(header_matrix):
            excel_row = header_start_row + level

            for col_idx, value in enumerate(row_values):
                worksheet.write(excel_row, col_idx,
                    value, header_format)

        current_row += n_header_rows

        # -----------------------------------------------------
        # Merge duplicate header cells horizontally
        # -----------------------------------------------------
        for level in range(n_header_rows):

            row_values = header_matrix[level]

            start_col = 0

            while start_col < len(row_values):

                value = row_values[start_col]

                # Don't merge blanks
                if value == "":
                    start_col += 1
                    continue

                end_col = start_col

                while (
                    end_col + 1 < len(row_values)
                    and row_values[end_col + 1] == value
                ):
                    end_col += 1

                if end_col > start_col:
                    worksheet.merge_range(header_start_row + level,
                        start_col, header_start_row + level,
                        end_col, value, header_format)

                start_col = end_col + 1

        # -----------------------------------------------------
        # Write data
        # -----------------------------------------------------
        for row_idx, (_, row) in enumerate(df.iterrows()):

            excel_row = current_row + row_idx

            for col_idx, col_id in enumerate(col_ids):

                value = row[col_id]

                if pd.isna(value):
                    value = ""

                worksheet.write(excel_row, col_idx,
                    value, data_format)

        # -----------------------------------------------------
        # Basic column widths
        # -----------------------------------------------------
        for col_idx, c in enumerate(columns):

            name = c["name"]

            if isinstance(name, list):
                width = max([len(str(x)) for x in name if x] + [10])
            else:
                width = len(str(name))

            worksheet.set_column(col_idx, col_idx,
                min(max(width + 2, 12), 30))

    output.seek(0)

    return dcc.send_bytes(output.read(), filename)
