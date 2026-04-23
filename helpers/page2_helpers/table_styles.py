"""
Styling utilities for Dash DataTables.
"""
import pandas as pd
from helpers.config import TABLE_COLORS, TABLE_FONT, YEARS, YEARS_MINUS_2011


#-------------------- Shared blank-separator style --------------------
_BLANK_ROW_STYLE = {
    'backgroundColor': '#FFFFFF',
    'padding': '0px',
    'lineHeight': '6px',
    'minHeight': '6px',
    'height': '6px',
}

def blank_row(col_name='', years='', label=''):
    return {col_name: label, **{y: '' for y in years}}

#-------------------- Generic stylers  (reusable across all tables) --------------------

def make_style_cell(
    label_col_id: str,
    value_col_ids: list,
    label_width: str = '40%',
    label_min_width: str = '160px',
) -> list:
    """
    Build style_cell_conditional for a table with one label column
    and one or more right-aligned value columns.

    The label column gets ``label_width``; each value column shares the
    remaining 60% equally.

    Args:
        label_col_id:   Column ID of the left-hand label column.
        value_col_ids:  Ordered list of value column IDs.
        label_width:    CSS width for the label column.
        label_min_width: CSS min-width for the label column.

    Returns:
        List of style_cell_conditional dicts.
    """
    n = len(value_col_ids)
    value_width = f'{round(60 / n, 1)}%' if n else '0%'

    styles = [{
        'if': {'column_id': label_col_id},
        'textAlign': 'left',
        'width': label_width,
        'minWidth': label_min_width,
    }]
    for col_id in value_col_ids:
        styles.append({'if': {'column_id': col_id}, 'textAlign': 'right', 'width': value_width})
    return styles


def make_special_row_styles(
    data: pd.DataFrame,
    label_col: str,
    *,
    geo_headers: set = frozenset(),
    section_headers: set = frozenset(),
    warning_headers: set = frozenset(),
    total_labels: set = frozenset({'TOTAL'}),
    italic_labels: set = frozenset(),
    warning_color: str = '#b55438',
    blank_label: str = '',
) -> list:
    """
    Build style_data_conditional for special rows in a DataTable.

    Row classification (first match wins):
      geo_headers     → geography colour + white text + bold
      warning_headers → warning_color text + bold
      section_headers → headings colour + body text + bold
      total_labels    → bold only
      italic_labels   → warning_color text + italic
      blank_label     → thin white separator

    Args:
        data:            DataFrame passed to the DataTable.
        label_col:       Name of the column holding row-type labels.
        geo_headers:     Label values that render as geography-colour header rows.
        section_headers: Label values that render as headings-colour section rows.
        warning_headers: Label values that render in warning_color bold.
        total_labels:    Label values that render bold only (default: {'TOTAL'}).
        italic_labels:   Label values that render italic in warning_color.
        warning_color:   CSS colour for warning/below-multiple rows.
        blank_label:     Label value used for blank separator rows (default: '').

    Returns:
        List of style_data_conditional dicts.
    """
    _GEO = {
        'backgroundColor': TABLE_COLORS['geography'],
        'color': '#FFFFFF',
        'fontWeight': 'bold',
    }
    _SECTION = {
        'backgroundColor': TABLE_COLORS['headings'],
        'color': TABLE_COLORS['text'],
        'fontWeight': 'bold',
    }

    styles = []
    for i, (_, row) in enumerate(data.iterrows()):
        val = row.get(label_col, '')
        rule = {'if': {'row_index': i}}

        if val in geo_headers:
            styles.append({**rule, **_GEO})
        elif val in warning_headers:
            styles.append({**rule, 'color': warning_color, 'fontWeight': 'bold'})
        elif val in section_headers:
            styles.append({**rule, **_SECTION})
        elif val in total_labels:
            styles.append({**rule, 'fontWeight': 'bold'})
        elif val in italic_labels:
            styles.append({**rule, 'color': warning_color, 'fontStyle': 'italic'})
        elif val == blank_label:
            styles.append({**rule, **_BLANK_ROW_STYLE})

    return styles


#-------------------- Shared header and base styles --------------------

def generate_style_data_conditional(data: pd.DataFrame) -> list:
    """
    Generate alternating row colours for table data.

    Args:
        data: DataFrame with table data.

    Returns:
        List of style dicts for DataTable style_data_conditional.
    """
    return [
        {
            'if': {'row_index': i},
            'backgroundColor': TABLE_COLORS['row_alt_1'] if i % 2 == 0 else TABLE_COLORS['row_alt_2'],
            'color': TABLE_COLORS['text'],
            'border': f"1px solid {TABLE_COLORS['border']}",
        }
        for i in range(len(data))
    ]


def generate_style_header_conditional(
    columns: list,
    is_multiindex: bool = False,
    first_col_id: str = 'Households by Tenure',
) -> list:
    """
    Generate header styling for table columns.

    For 3-level multi-index headers:
        header_index 0 – geography name row  → geography colour
        header_index 1 – group row           → headings colour; first col → geography colour
        header_index 2 – year / label row    → headings colour; first col → geography colour

    Args:
        columns:       List of column definitions.
        is_multiindex: Whether columns use multi-level (list) names.
        first_col_id:  Column ID of the first (label) column to visually merge.

    Returns:
        List of style dicts for DataTable style_header_conditional.
    """
    if not is_multiindex:
        return [
            {
                'if': {'header_index': 0, 'column_id': col['id']},
                'backgroundColor': TABLE_COLORS['geography'] if i == 0 else TABLE_COLORS['headings'],
                'color': TABLE_COLORS['text'],
                'fontWeight': 'bold',
                'border': f"1px solid {TABLE_COLORS['border']}",
            }
            for i, col in enumerate(columns)
        ]

    base = {'fontWeight': 'bold', 'border': f"1px solid {TABLE_COLORS['border']}"}
    return [
        # Row 0 – geography name: geography colour across all columns
        {**base, 'if': {'header_index': 0},
         'backgroundColor': TABLE_COLORS['geography'], 'color': '#FFFFFF'},

        # Row 1 – group labels: headings colour
        {**base, 'if': {'header_index': 1},
         'backgroundColor': TABLE_COLORS['headings'], 'color': TABLE_COLORS['text']},

        # Row 2 – year labels: headings colour
        {**base, 'if': {'header_index': 2},
         'backgroundColor': TABLE_COLORS['headings'], 'color': TABLE_COLORS['text']},

        # Override first column at rows 1 & 2 → geography colour (visually merged)
        {**base, 'if': {'header_index': 1, 'column_id': first_col_id},
         'backgroundColor': TABLE_COLORS['geography'], 'color': '#FFFFFF'},
        {**base, 'if': {'header_index': 2, 'column_id': first_col_id},
         'backgroundColor': TABLE_COLORS['geography'], 'color': '#FFFFFF'},

        # Remove internal borders between the 3 header rows of the first column
        {'if': {'header_index': 0, 'column_id': first_col_id}, 'borderBottom': 'none'},
        {'if': {'header_index': 1, 'column_id': first_col_id}, 'borderTop': 'none', 'borderBottom': 'none'},
        {'if': {'header_index': 2, 'column_id': first_col_id}, 'borderTop': 'none'},
    ]


def get_base_table_style() -> dict:
    """Get base styling shared by all tables."""
    return {
        'style_table': {
            'overflowY': 'auto',
            'overflowX': 'auto',
        },
        'style_data': {
            'whiteSpace': 'normal',
            'height': 'auto',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
        'style_cell': {
            'font-family': TABLE_FONT,
            'height': 'auto',
            'whiteSpace': 'normal',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'border': f"1px solid {TABLE_COLORS['border']}",
        },
        'style_header': {
            'textAlign': 'center',
            'fontWeight': 'bold',
            'font-family': TABLE_FONT,
        },
    }


#-------------------- Cell formatters --------------------

def format_number(value, decimals: int = 0):
    """Format number with commas and specified decimals."""
    if pd.isna(value) or value == 'n/a':
        return value
    try:
        if decimals == 0:
            return f'{int(value):,}'
        return f'{float(value):,.{decimals}f}'
    except (ValueError, TypeError):
        return value


def format_percent(value, multiply: bool = False):
    """Format value as percentage."""
    if pd.isna(value) or value == 'n/a':
        return value
    try:
        v = float(value) * 100 if multiply else float(value)
        return f'{v:.0f}%'
    except (ValueError, TypeError):
        return value



# -------------------- Section 3 – Demographics --------------------

############### Table 3.1 stylers ###############
_T3_1_SECTION_HEADERS = frozenset({
    'Indigenous Population (by CSD)',
    'Regional Indigenous Households (by CD)',
    'Number of Indigenous-led HHs who have moved in last 5 years (by CD)...',
})


def get_special_row_styles_3_1(data: pd.DataFrame) -> list:
    return make_special_row_styles(
        data, 'Indicator',
        geo_headers={'__geo_header__', '__cd_header__'},
        section_headers=_T3_1_SECTION_HEADERS,
    )


def style_cell_3_1() -> list:
    return make_style_cell(
        'Indicator',
        YEARS,
        label_min_width='200px',
    )

############### Table 3.3 stylers ###############

_T3_3_VALUE_COLS = ['Indigenous', 'First Nations', 'Métis', 'Inuit', 'Multiple/Other Responses']

def get_special_row_styles_3_3(data: pd.DataFrame) -> list:
    return make_special_row_styles(data, 'Age Group', total_labels={'Total'})


def style_cell_3_3() -> list:
    return make_style_cell('Age Group', _T3_3_VALUE_COLS, label_width='25%', label_min_width='120px')


############### Table 3.4 stylers ###############

_T3_4_VALUE_COLS = ['Indigenous', 'Men+', 'Women+']

def get_special_row_styles_3_4(data: pd.DataFrame) -> list:
    return make_special_row_styles(data, 'Age Group', total_labels={'Total'})


def style_cell_3_4() -> list:
    return make_style_cell('Age Group', _T3_4_VALUE_COLS, label_width='25%', label_min_width='120px')


############### Table 3.5 stylers ###############

def get_special_row_styles_3_5(data: pd.DataFrame) -> list:
    return make_special_row_styles(
        data, 'Number of Indigenous HHs',
        geo_headers={'Number of Indigenous HHs'},
        total_labels={'Total'},
    )


def style_cell_3_5() -> list:
    return make_style_cell('Number of Indigenous HHs', YEARS_MINUS_2011, label_width='25%', label_min_width='120px')


#-------------------- Section 4 – Housing Tenure --------------------

############### Table 4.1 stylers ###############

def get_special_row_styles_4_1(data: pd.DataFrame) -> list:
    return make_special_row_styles(
        data, 'Households by Tenure',
        geo_headers={'Households by Tenure'},
    )


def style_cell_4_1(show_both: bool) -> list:
    value_cols = [f'indg_{y}' for y in YEARS]
    if show_both:
        value_cols += [f'non_indg_{y}' for y in YEARS]
    return make_style_cell('Households by Tenure', value_cols, label_min_width='160px')


#-------------------- Section 8 – Core Housing Need --------------------

############### Table 8.1 stylers ###############

_T8_INDICATORS = frozenset({
    "Affordability (Households paying >30% of income on shelter)",
    "Adequacy (Households living in dwellings needing Major Repairs)",
    "Suitability (Households living in overcrowded dwellings)",
    "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)",
    "Acceptable Housing (Affordable, Adequate, and Suitable)",
    "Total households (for reference)",
})
_T8_BELOW_MULTIPLE = "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)"
_T8_TOTAL = "Total households (for reference)"

# Indicators that use geography-colour header styling (excludes warning + total rows)
_T8_GEO_HEADERS = _T8_INDICATORS - {_T8_BELOW_MULTIPLE, _T8_TOTAL}


def get_special_row_styles_8_1(data: pd.DataFrame) -> list:
    return make_special_row_styles(
        data, 'Indicator',
        geo_headers=_T8_GEO_HEADERS,
        warning_headers={_T8_BELOW_MULTIPLE},
        section_headers={_T8_TOTAL},
        total_labels=frozenset(),           # no plain TOTAL rows in 8.1
        italic_labels={'__below_count__', '__below_pct__'},
    )


def style_cell_8_1(show_both: bool) -> list:
    value_cols = [f'indg_{y}' for y in YEARS_MINUS_2011]
    if show_both:
        value_cols += [f'non_indg_{y}' for y in YEARS_MINUS_2011]
    return make_style_cell('Indicator', value_cols, label_min_width='200px')


