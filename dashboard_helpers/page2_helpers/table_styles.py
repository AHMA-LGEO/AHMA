"""
Styling utilities for Dash DataTables.
"""
import pandas as pd
from dashboard_helpers.config import TABLE_COLORS, TABLE_FONT


#-------------------- Global Comparison Button Style --------------------

COLOR_SCHEME = {
    "all_on": {
        "bg": "#6b7280",      
        "border": "#6b7280",  
        "text": "#ffffff",    
        "label": "○ Hide Comparison",
    },
    "all_off": {
        "bg": "#9CA37A",     
        "border": "#9CA37A", 
        "text": "#ffffff",   
        "label": "● Show Comparison",
    },
    "mixed": {
        "bg": "#f59e0b",     
        "border": "#f59e0b", 
        "text": "#ffffff",   
        "label": "◐ Mixed",
    },
}

#-------------------- Shared blank-separator style --------------------
_BLANK_ROW_STYLE = {
    'backgroundColor': '#FFFFFF',
    'color': '#FFFFFF',
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
        'paddingLeft': '12px',
    }]
    for col_id in value_col_ids:
        styles.append({
            'if': {'column_id': col_id}, 
            'textAlign': 'right', 
            'width': value_width,
            'paddingRight': '12px',
            })
    return styles


def make_special_row_styles(
    data: pd.DataFrame,
    label_col: str,
    *,
    geo_headers: set = frozenset(),
    col_headers: set = frozenset(),
    section_headers: set = frozenset(),
    warning_headers: set = frozenset(),
    total_labels: set = frozenset({'Total'}),
    italic_labels: set = frozenset(),
    total_col: bool = False,
    warning_color: str = '#b55438',
    blank_label: str = '',
) -> list:
    """
    Build style_data_conditional for special rows in a DataTable.

    Row classification (first match wins):
      geo_headers       → geography colour + white text + bold
      col_headers       → columns colour + white text + bold
      warning_headers   → warning_color text + bold
      section_headers   → headings colour + body text + bold
      total_labels      → bold only (exact match on label column)
      italic_labels     → warning_color text + italic
      blank_label       → thin white separator
      total_col         → bold all cells in any column whose ID contains 'total'

    Args:
        data:               DataFrame passed to the DataTable.
        label_col:          Name of the column holding row-type labels.
        geo_headers:        Label values that render as geography-colour header rows.
        col_headers:        Label values that render as columns-colour header rows.
        section_headers:    Label values that render as headings-colour section rows.
        warning_headers:    Label values that render in warning_color bold.
        total_labels:       Label values that render bold only (default: {'Total'}).
        italic_labels:      Label values that render italic in warning_color.
        total_col:          If True, bold all cells in columns whose ID contains 'total'.
        warning_color:      CSS colour for warning/below-multiple rows.
        blank_label:        Label value used for blank separator rows (default: '').

    Returns:
        List of style_data_conditional dicts.
    """
    _GEO = {
        'backgroundColor': TABLE_COLORS['geography'],
        'color': '#FFFFFF',
        'fontWeight': 'bold',
    }
    _COLUMNS = {
        'backgroundColor': TABLE_COLORS['columns'],
        'color': '#FFFFFF',
        'fontWeight': 'bold',
        'borderRight': 'none',
    }
    _SECTION = {
        'backgroundColor': TABLE_COLORS['headings'],
        'color': TABLE_COLORS['text'],
        'fontWeight': 'bold',
    }

    styles = []
    for i, (_, row) in enumerate(data.iterrows()):
        val = row.get(label_col, '')
        rule = {'if': {'row_index': i}, 'paddingRight': '12px'}

        if val in geo_headers:
            styles.append({**rule, **_GEO})
        elif val in col_headers:
            styles.append({**rule, **_COLUMNS})
        elif val in warning_headers:
            styles.append({**rule, 'color': warning_color, 'fontWeight': 'bold'})
        elif val in section_headers:
            styles.append({**rule, **_SECTION})
        elif val in total_labels:
            styles.append({**rule, 'fontWeight': 'bold', 'backgroundColor': TABLE_COLORS['headings']})  # assigning headings color to "Total" rows
        elif val in italic_labels:
            styles.append({**rule, 'color': warning_color, 'fontStyle': 'italic'})
        elif val == blank_label:
            styles.append({**rule, **_BLANK_ROW_STYLE})

    if total_col:
        for col in data.columns:
            if 'total' in str(col).lower():
                styles.append({'if': {'column_id': col}, 'fontWeight': 'bold', 'paddingRight': '12px'})

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
            'paddingRight': '12px',
        }
        for i in range(len(data))
    ]


def generate_style_header_conditional(
    columns: list,
    is_multiindex: bool = False,
    first_col_id: str = 'Households by Tenure',
    n_header_rows: int = 3,
) -> list:
    """
    Generate header styling for table columns.

    For multi-index headers (n_header_rows levels):
        header_index 0          - geography name row → geography colour (all columns)
        header_index 1..n-1     - label/group/year rows → headings colour; first col → geography colour

    Args:
        columns:        List of column definitions.
        is_multiindex:  Whether columns use multi-level (list) names.
        first_col_id:   Column ID of the first (label) column to visually merge across all rows.
        n_header_rows:  Number of header levels (default 3; use 4 for HHs + % of Total (tables like 5.5)).

    Returns:
        List of style dicts for DataTable style_header_conditional.
    """
    if not is_multiindex:
        return [
            {
                'if': {'header_index': 0, 'column_id': col['id']},
                'backgroundColor': TABLE_COLORS['geography'] if i == 0 else TABLE_COLORS['columns'],
                'color': '#FFFFFF',
                'fontWeight': 'bold',
                'border': f"1px solid {TABLE_COLORS['border']}",
                'padding': '6px',
            }
            for i, col in enumerate(columns)
        ]
 
    base = {
        'fontWeight': 'bold',
        'border': f"1px solid {TABLE_COLORS['border']}",
        'padding': '6px',
        'color': '#FFFFFF',
    }
    
    styles = []
    
    # Header row 0: Geography level - spans entire row (no internal borders)
    styles.append({
        **base,
        'if': {'header_index': 0},
        'backgroundColor': TABLE_COLORS['geography'],
        
    })

    # Header rows 1+: Columns level (household type and year)
    for i in range(1, n_header_rows):
        styles.append({
            **base,
            'if': {'header_index': i},
            'backgroundColor': TABLE_COLORS['columns'],
        })

    # Add borders between geography and label column rows
    styles.append({
        'if': {'header_index': 0, 'column_id': first_col_id},
        'borderBottom': f"1px solid {TABLE_COLORS['border']}",
    })
    for i in range(1, n_header_rows - 1):
        styles.append({
            'if': {'header_index': i, 'column_id': first_col_id},
            'borderTop': 'none',
            'borderBottom': 'none',
        })
    styles.append({
        'if': {'header_index': n_header_rows - 1, 'column_id': first_col_id},
        'borderBottom': 'none',
    })
    
    return styles


def merge_columns(
    df: pd.DataFrame,
    rows: list[int],
    value_cols: list[str],
    group_size: int = 3,
) -> pd.DataFrame:
    """
    Keep values only in the middle column for selected rows.

    Example:
        For 3 communities per year:
    [col1, col2, col3] -> ['', col2, '']
    [col4, col5, col6] -> ['', col5, '']

    Args:
        df: DataFrame to process
        rows: Row indices to merge
        value_cols: All value column IDs
        group_size: Number of columns per group (1 for original, 3 for communities)
    """
    out = df.copy()
    
    # If group_size is 1, use original logic
    if group_size == 1:
        middle_col = value_cols[len(value_cols) // 2]
        side_cols = [c for c in value_cols if c != middle_col]
        
        for row_idx in rows:
            out.loc[row_idx, side_cols] = ''
    else:
        # Process groups of columns
        middle_idx = group_size // 2
        
        for row_idx in rows:
            for group_num in range(len(value_cols) // group_size):
                group_start = group_num * group_size
                group_end = group_start + group_size
                
                group_cols = value_cols[group_start:group_end]
                middle_col = group_cols[middle_idx]
                side_cols = [c for c in group_cols if c != middle_col]
                
                out.loc[row_idx, side_cols] = ''
    
    return out


def make_centered_merged_row_styles(
    rows: list[int],
    value_cols: list[str],
    group_size: int = 1,
) -> list:
    """
    Style rows so the middle value column appears visually merged.

    - hides vertical borders between value columns
    - centers the middle value
    - removes text from side columns visually
    """

    styles = []

    # If group_size is 1, use original logic
    if group_size == 1:
        for row_idx in rows:
            # left cell
            styles.append({
                'if': {
                    'row_index': row_idx,
                    'column_id': value_cols[0]
                },
                'borderRight': 'none',
                'textAlign': 'center',
                'color': 'transparent',
            })
 
            # right cell
            styles.append({
                'if': {
                    'row_index': row_idx,
                    'column_id': value_cols[2]
                },
                'borderLeft': 'none',
                'textAlign': 'center',
                'color': 'transparent',
            })
 
            # middle cell
            styles.append({
                'if': {
                    'row_index': row_idx,
                    'column_id': value_cols[1]
                },
                'textAlign': 'center',
                'borderLeft': 'none',
                'borderRight': 'none',
            })
    else:
        # Process groups of columns
        middle_idx = group_size // 2
        
        for row_idx in rows:
            for group_num in range(len(value_cols) // group_size):
                group_start = group_num * group_size
                group_end = group_start + group_size
                
                group_cols = value_cols[group_start:group_end]
                
                # Left cell
                styles.append({
                    'if': {
                        'row_index': row_idx,
                        'column_id': group_cols[0]
                    },
                    'borderRight': 'none',
                    'textAlign': 'center',
                    'color': 'transparent',
                })
                
                # Middle cell
                styles.append({
                    'if': {
                        'row_index': row_idx,
                        'column_id': group_cols[middle_idx]
                    },
                    'textAlign': 'center',
                    'borderLeft': 'none',
                    'borderRight': 'none',
                })
                
                # Right cell
                styles.append({
                    'if': {
                        'row_index': row_idx,
                        'column_id': group_cols[2]
                    },
                    'borderLeft': 'none',
                    'textAlign': 'center',
                    'color': 'transparent',
                })

    return styles


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
    
    # handle strings
    if isinstance(value, str):
        value = value.strip().replace(',', '')

        if value == '':
            return value
        
    try:
        num = float(value)
        if decimals == 0:
            return f'{int(num):,}'
        
        return f'{float(num):,.{decimals}f}'
    
    except (ValueError, TypeError):
        return value


def format_percent(value, multiply: bool = False, precision: int = 0):
    """Format value as percentage."""
    if pd.isna(value) or value == 'n/a':
        return value
    try:
        v = float(value) * 100 if multiply else float(value)
        return f'{v:.{precision}f}%'
    except (ValueError, TypeError):
        return value


def format_dollar(value):
    """Format value as a dollar amount"""
    if pd.isna(value) or value == 'n/a':
        return value
    try:
        return f'${int(float(value)):,}'
    except (ValueError, TypeError):
        return value




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
    base_styles = make_special_row_styles(
        data, 'Indicator',
        col_headers=_T8_GEO_HEADERS,
        warning_headers={_T8_BELOW_MULTIPLE},
        section_headers={_T8_TOTAL},
        total_labels=frozenset(), 
        italic_labels={'__below_count__', '__below_pct__'},
    )
    
    # Override col_headers styling to semi-bold
    # styles = []
    # for style in base_styles:
    #     if style.get('if', {}).get('column_id') in _T8_GEO_HEADERS:
    #         # Semi-bold for col_headers (600 instead of 700)
    #         style['fontWeight'] = '300'
    #     styles.append(style)
    for style in base_styles:
        rule = style.get('if', {})
        if 'row_index' in rule:
            # Check if this row contains col_headers
            row_idx = rule['row_index']
            if data.iloc[row_idx]['Indicator'] in _T8_GEO_HEADERS:
                style['fontWeight'] = '600'  # Semi-bold
    
    return base_styles


#-------------------- Section 9 – Systemic Pathways and Indigenous Homelessness --------------------

############### Table 9.1 stylers ###############
_T9_1_LABEL_COL_2 = 'Percentage of people released who identify as indigenous'
def get_special_row_styles_9_1(data: pd.DataFrame) -> list:
    styles = make_special_row_styles(data, 'Age',
                                    total_labels={'Total'},
                                    col_headers={_T9_1_LABEL_COL_2})

    # Find rows with col_headers and add textAlign
    for i, val in enumerate(data['Age']):
        if val == _T9_1_LABEL_COL_2:
            styles.append({
                'if': {'row_index': i},
                'textAlign': 'center',
            })
    return styles


############### Table 9.3 stylers ###############

_T9_3_GEO_HEADERS = {
    "Number of Indigenous people who experienced homelessness (PEH)",
    "All respondents",
}
_T9_3_SECTION_HEADERS = {
    "Where PEH stayed the night of the PIT count",
    "Length of time experiencing homelessness",
    "Reason for housing loss",
    "% who experienced homelessness for the first time as a youth",
    "% of youth who were in foster care, youth group home, or an independent Living Agreement as a youth",
}
_T9_3_RED_ATTRS = {"Indigenous respondents", "Non-Indigenous respondents", 
                   "Sheltered", "Unsheltered", "% who identified eviction as cause of most recent housing loss",
                   "First Nations", "Métis", "Inuit", "Other/Multiple Indigenous Communities"}

def get_special_row_styles_9_3(data: pd.DataFrame) -> list:
    return make_special_row_styles(
        data, 'Attribute',
        geo_headers=_T9_3_GEO_HEADERS,
        section_headers=_T9_3_SECTION_HEADERS,
        italic_labels=_T9_3_RED_ATTRS,
        total_labels={"Total"},
    )
