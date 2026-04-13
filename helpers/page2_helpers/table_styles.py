"""
Styling utilities for Dash DataTables.
"""
import pandas as pd
from helpers.config import TABLE_COLORS, TABLE_FONT


def generate_style_data_conditional(data: pd.DataFrame) -> list:
    """
    Generate alternating row colors for table data.

    Args:
        data: DataFrame with table data

    Returns:
        List of style dictionaries for DataTable
    """
    data_style = []
    for i in range(len(data)):
        bg_color = TABLE_COLORS['row_alt_1'] if i % 2 == 0 else TABLE_COLORS['row_alt_2']
        data_style.append({
            'if': {'row_index': i},
            'backgroundColor': bg_color,
            'color': TABLE_COLORS['text'],
            'border': f"1px solid {TABLE_COLORS['border']}"
        })
    return data_style


def generate_style_header_conditional(columns: list, is_multiindex: bool = False,
                                      first_col_id: str = 'Households by Tenure') -> list:
    """
    Generate header styling for table columns.

    For 3-level multi-index headers:
        header_index 0 – geography name row      → geography colour
        header_index 1 – group row               → headings colour; first col → geography colour
        header_index 2 – year / label row        → headings colour; first col → geography colour

    Args:
        columns:       List of column definitions
        is_multiindex: Whether columns use multi-level (list) names
        first_col_id:  Column ID of the first (label) column to merge across header rows

    Returns:
        List of style dictionaries for DataTable style_header_conditional
    """
    if not is_multiindex:
        return [
            {
                'if': {'header_index': 0, 'column_id': col['id']},
                'backgroundColor': TABLE_COLORS['geography'] if i == 0 else TABLE_COLORS['headings'],
                'color': TABLE_COLORS['text'],
                'fontWeight': 'bold',
                'border': f"1px solid {TABLE_COLORS['border']}"
            }
            for i, col in enumerate(columns)
        ]

    base = {'fontWeight': 'bold', 'border': f"1px solid {TABLE_COLORS['border']}"}

    return [
        # Row 0 – geography name: geography colour across all columns
        {**base, 'if': {'header_index': 0},
         'backgroundColor': TABLE_COLORS['geography'],
         'color': '#FFFFFF'},

        # Row 1 – group labels: headings colour
        {**base, 'if': {'header_index': 1},
         'backgroundColor': TABLE_COLORS['headings'],
         'color': TABLE_COLORS['text']},

        # Row 2 – year labels: headings colour
        {**base, 'if': {'header_index': 2},
         'backgroundColor': TABLE_COLORS['headings'],
         'color': TABLE_COLORS['text']},

        # Override first column at rows 1 & 2 → geography colour (visually merged)
        {**base, 'if': {'header_index': 1, 'column_id': first_col_id},
         'backgroundColor': TABLE_COLORS['geography'],
         'color': '#FFFFFF'},
        {**base, 'if': {'header_index': 2, 'column_id': first_col_id},
         'backgroundColor': TABLE_COLORS['geography'],
         'color': '#FFFFFF'},

        # Remove internal borders between the 3 header rows of the first column
        {'if': {'header_index': 0, 'column_id': first_col_id}, 'borderBottom': 'none'},
        {'if': {'header_index': 1, 'column_id': first_col_id}, 'borderTop': 'none', 'borderBottom': 'none'},
        {'if': {'header_index': 2, 'column_id': first_col_id}, 'borderTop': 'none'},
    ]


def get_special_row_styles(data: pd.DataFrame) -> list:
    """
    Generate style_data_conditional entries for the three special row types
    inserted by prepare_table_4_1_data:

      'Households by Tenure'  → section header (geography colour, white, bold)
      'TOTAL'                 → bold
      ''                      → thin blank separator (white background)
    """
    styles = []
    for i, (_, row) in enumerate(data.iterrows()):
        tenure = row.get('Households by Tenure', '')
        if tenure == 'Households by Tenure':
            styles.append({
                'if': {'row_index': i},
                'backgroundColor': TABLE_COLORS['geography'],
                'color': '#FFFFFF',
                'fontWeight': 'bold',
            })
        elif tenure == 'TOTAL':
            styles.append({
                'if': {'row_index': i},
                'fontWeight': 'bold',
            })
        elif tenure == '':
            styles.append({
                'if': {'row_index': i},
                'backgroundColor': '#FFFFFF',
                'padding': '0px',
                'lineHeight': '6px',
                'minHeight': '6px',
                'height': '6px',
            })
    return styles


def get_base_table_style() -> dict:
    """Get base styling for all tables."""
    return {
        'style_table': {
            'overflowY': 'auto',
            'overflowX': 'auto'
        },
        'style_data': {
            'whiteSpace': 'normal',
            'height': 'auto',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        },
        'style_cell': {
            'font-family': TABLE_FONT,
            'height': 'auto',
            'whiteSpace': 'normal',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'border': f"1px solid {TABLE_COLORS['border']}"
        },
        'style_header': {
            'textAlign': 'center',
            'fontWeight': 'bold',
            'font-family': TABLE_FONT
        }
    }

def style_cell_4_1(show_both: bool) -> list:
    year_cols = ['2006', '2011', '2016', '2021']
    n_groups = 2 if show_both else 1
    # 40% for the label column; remaining 60% split across all year cells
    year_width = f'{round(60 / (n_groups * len(year_cols)), 1)}%'

    styles = [
        {
            'if': {'column_id': 'Households by Tenure'},
            'textAlign': 'left',
            'width': '40%',
            'minWidth': '160px',
        }
    ]
    for y in year_cols:
        styles.append({'if': {'column_id': f'indg_{y}'}, 'textAlign': 'right', 'width': year_width})
        if show_both:
            styles.append({'if': {'column_id': f'non_indg_{y}'}, 'textAlign': 'right', 'width': year_width})

    return styles


_T8_INDICATORS = {
    "Affordability (Households paying >30% of income on shelter)",
    "Adequacy (Households living in dwellings needing Major Repairs)",
    "Suitability (Households living in overcrowded dwellings)",
    "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)",
    "Acceptable Housing (Affordable, Adequate, and Suitable)",
    "Total households (for reference)",
}
_T8_BELOW_MULTIPLE = "Below multiple indicators (Affordability and/or Adequacy and/or Suitability)"
_T8_TOTAL = "Total households (for reference)"


def get_special_row_styles_8_1(data: pd.DataFrame) -> list:
    """
    Generate style_data_conditional entries for the special row types in Table 8.1:
      Indicator section header rows  → geography colour, white, bold
      'Below multiple' section header → warning colour (#b55438), white, bold
      'Below multiple' metric rows    → red italic text
      'Total households' section hdr  → headings colour, bold
      ''  (blank separator)           → thin white row
    """
    styles = []
    for i, (_, row) in enumerate(data.iterrows()):
        val = row.get('Indicator', '')

        if val in _T8_INDICATORS:
            if val == _T8_BELOW_MULTIPLE:
                styles.append({
                    'if': {'row_index': i},
                    'color': '#b55438',
                    'fontWeight': 'bold',
                })
            elif val == _T8_TOTAL:
                styles.append({
                    'if': {'row_index': i},
                    'backgroundColor': TABLE_COLORS['headings'],
                    'color': TABLE_COLORS['text'],
                    'fontWeight': 'bold',
                })
            else:
                styles.append({
                    'if': {'row_index': i},
                    'backgroundColor': TABLE_COLORS['geography'],
                    'color': '#FFFFFF',
                    'fontWeight': 'bold',
                })
        elif val in ('__below_count__', '__below_pct__'):
            styles.append({
                'if': {'row_index': i},
                'color': '#b55438',
                'fontStyle': 'italic',
            })
        elif val == '':
            styles.append({
                'if': {'row_index': i},
                'backgroundColor': '#FFFFFF',
                'padding': '0px',
                'lineHeight': '6px',
                'minHeight': '6px',
                'height': '6px',
            })

    return styles


def style_cell_8_1(show_both: bool) -> list:
    year_cols = ['2006', '2016', '2021']
    n_groups = 2 if show_both else 1
    year_width = f'{round(60 / (n_groups * len(year_cols)), 1)}%'

    styles = [
        {
            'if': {'column_id': 'Indicator'},
            'textAlign': 'left',
            'width': '40%',
            'minWidth': '200px',
        }
    ]
    for y in year_cols:
        styles.append({'if': {'column_id': f'indg_{y}'}, 'textAlign': 'right', 'width': year_width})
        if show_both:
            styles.append({'if': {'column_id': f'non_indg_{y}'}, 'textAlign': 'right', 'width': year_width})

    return styles


def format_number(value, decimals: int = 0):
    """Format number with commas and specified decimals."""
    if pd.isna(value) or value == 'n/a':
        return value
    try:
        if decimals == 0:
            return f'{int(value):,}'
        else:
            return f'{float(value):,.{decimals}f}'
    except (ValueError, TypeError):
        return value


def format_percent(value, multiply: bool = False):
    """Format value as percentage."""
    if pd.isna(value) or value == 'n/a':
        return value
    try:
        if multiply:
            return f'{float(value) * 100:.0f}%'
        else:
            return f'{float(value):.0f}%'
    except (ValueError, TypeError):
        return value