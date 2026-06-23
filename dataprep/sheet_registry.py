import pdb, sys, os
import pandas as pd
from functools import lru_cache
from collections import defaultdict
from pathlib import Path



source_dir = Path(__file__).parent.parent / "source" / "data"
DATA_PATH = os.path.join(source_dir, r"2026-06-19 IHNAT Data v12.xlsx") # CHECK IN DROPBOX'S SOURCE FOLDER, IF THIS IS THE RECENT DATA FILE

# ADDED THE ACCESS PATH HERE FROM SECTION 10 PREP, FOR CONSISTENCY PURPOSES
ACCESS_DATA_PATH = os.path.join(source_dir, r"2026-05-10 IHNAT Access Data v1.csv") # CHECK IN DROPBOX'S PROCESSED->DATA->EXCEL->CSV->Access Data (for source-data) FOR MOST

ANCHOR_COLS = ["Geocode", "Geography", "Name", "Region"] # For some sheet it is Name or Region instead of Geography

# How many header rows each sheet has before actual data starts.
# output_row: the row index where "output number:" lives, ie row tells which table each column belongs to eg: 2.1, 2.2
# col_row: the row index of actual column names, ie Geocode, Nation1, etc <- this becomes df header
# data_start: the row index where real data begins, everything above this is either meta data or columns
# output_col_start:
_STANDARD_CONFIG = {"output_row": 0, "col_row": 1,  "data_start": 2}
_STANDARD_SHEETS = [
    "2006_Indig_Profile",
    "2011_Indig_Profile",
    "2016_Indig_Profile",
    "2021_Indig_Profile",
    "2006_IHNAT_T5",
    "2006_IHNAT_T6",
    "2016_IHNAT_T3",
    "2016_IHNAT_T4",
    "2021_IHNAT_T1",
    "2021_IHNAT_T2",
    "2006_HART",
    "2016_HART",
    "2021_HART",
    "CMHC",
    "BC Corrections",
    "MCFD",
    "BC Stats Projections",
    "Housing Targets",
    "Native Land",
    "Metis Communities"
]

SHEET_HEADER_CONFIG = {
    **{sheet: _STANDARD_CONFIG for sheet in _STANDARD_SHEETS},
    "PiT Count": {"output_row": 0, "col_row": 5, "data_start": 6},
    "Native Land_URLs": {"output_row": 0, "col_row": 0, "data_start": 1},
    "Friendship Centres": {"output_row": 0, "col_row": 0, "data_start": 1},
}


@lru_cache(maxsize=1) # builds once, reused for all the tables created
def build_registry() -> dict:
    """
    Returns a nested dict:
      registry[table_id][sheet_name] = [col_name, col_name, ...]

    e.g.
      registry["2.1"]["Native Lands"] = ["Nation1", "Nation2", ...]
      registry["9.3"]["PiT"] = ["2021_All Respondents_% Brain injury_(blank)", ...]
    """
    registry = defaultdict(lambda: defaultdict(list))

    print(f"Reading {DATA_PATH}, check if this the most recent data file...")
    ahma_data = pd.ExcelFile(DATA_PATH)

    for sheet_name in ahma_data.sheet_names:
        if sheet_name not in SHEET_HEADER_CONFIG:
            continue

        cfg = SHEET_HEADER_CONFIG[sheet_name]
        
        output_row_idx = cfg["output_row"]
        col_row_idx    = cfg["col_row"]

        # Read just the header rows — no data yet
        raw = pd.read_excel(
            DATA_PATH,
            sheet_name=sheet_name,
            header=None,
            nrows=col_row_idx + 1,   # read up to and including the col name row
        )
        if pd.isna(raw.iloc[0, 0]):
            raw.iloc[0, 0] = 'Dummy_Column' # To handle blank column name in excel sheets

        # output_col_start = cfg.get("output_col_start", 1)  # default to 1 if not set
        output_numbers = raw.iloc[output_row_idx]   # e.g. ["Output Number", 2.1, 2.1, ...]
        col_names = raw.iloc[col_row_idx]       # e.g. ["Geocode", "Nation1", ...]

        for col_idx, (output_val, col_name) in enumerate(zip(output_numbers, col_names)):
            # Skip the label column itself and any columns with no output number
            # if col_idx < output_col_start:   # skip label columns
            #     continue
            if pd.isna(output_val) or str(output_val).strip() in ("", "Output Number:"):
                continue

            table_id = str(output_val).strip()      # "2.1", "9.3" etc.
            col_name = str(col_name).strip()

            registry[table_id][sheet_name].append(col_name)

    return registry


def get_columns(table_id: str) -> dict:
    """
    Returns {sheet_name: [col_names]} for the given table_id.
    e.g. get_columns("9.3") -> {"PiT": ["2021_All...", "2023_All...", ...]}
    """
    reg = build_registry()
    # pdb.set_trace()
    if table_id not in reg:
        raise KeyError(f"Table '{table_id}' not found in any sheet. "
                       f"Available: {sorted(reg.keys())}")
    return dict(reg[table_id])


def get_sheet(sheet_name: str) -> pd.DataFrame:
    """
    Loads a sheet with correct header row
    """
    data_start = SHEET_HEADER_CONFIG[sheet_name]["data_start"]
    col_row = SHEET_HEADER_CONFIG[sheet_name]["col_row"]

    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name, header=col_row)
    df.columns = df.columns.str.strip()
    # data_start is absolute row index in the file,
    # after read_excel the rows above data_start become the header,
    # so we drop the metadata rows that land above the data
    rows_to_skip = data_start - col_row - 1
    if rows_to_skip > 0:
        df = df.iloc[rows_to_skip:]

    return df.reset_index(drop=True)


def fetch_data(table_id: str, geo: str = None, sheets: list = None) -> pd.DataFrame:
    """
    Pulls all columns tagged with table_id across all sheets.
    Merges on geocode if data spans multiple sheets.
    """
    col_map = get_columns(table_id)

    # filter to specific sheets if requested
    if sheets:
        col_map = {k: v for k, v in col_map.items() if k in sheets}

    if not col_map:
        return pd.DataFrame()

    # Step 1: Loading dataframes
    frames = {}
    for sheet_name, cols in col_map.items():
        sheet = get_sheet(sheet_name)

        keep_cols = (
                [c for c in ANCHOR_COLS if c in sheet.columns] +
                [c for c in cols if c not in ANCHOR_COLS and c in sheet.columns]
        )

        frames[sheet_name] = sheet[keep_cols]

    # Step 2: resolve column name conflicts if across different sheets
    col_seen = {} # col_name -> sheet_name that first claimed it
    for sheet_name, frame in frames.items():
        new_columns = list(frame.columns)
        col_count_in_sheet = {}

        for i, col in enumerate(frame.columns):
            if col in ANCHOR_COLS:
                continue

            if col in col_count_in_sheet:
                # Intra-sheet duplicate: disambiguate with occurrence count
                col_count_in_sheet[col] += 1
                new_name = f"{col}_{col_count_in_sheet[col]}"
                new_columns[i] = new_name
                col_seen[new_name] = sheet_name
                print(f"[WARN] '{col}' duplicate within '{sheet_name}' (occurrence {col_count_in_sheet[col]}) → renamed to '{new_name}'")
            elif col in col_seen:
                # Cross-sheet conflict: append sheet name
                new_name = f"{col}_{sheet_name}"
                new_columns[i] = new_name
                col_seen[new_name] = sheet_name
                print(f"[WARN] '{col}' conflict between '{col_seen[col]}' and '{sheet_name}' → renamed to '{new_name}'")
            else:
                col_count_in_sheet[col] = 1
                col_seen[col] = sheet_name

        frame.columns = new_columns
        frames[sheet_name] = frame

    # Step 3: merging all data on geocode column
    result = list(frames.values())[0]
    for frame in list(frames.values())[1:]:
        new_cols = ["Geocode", "Geography"] + [
            c for c in frame.columns
            if c not in result.columns
               and c not in ANCHOR_COLS
        ]
        new_cols = [c for c in new_cols if c in frame.columns]

        result = result.merge(frame[new_cols], on='Geocode', how='outer', suffixes=("_old", ""))

        # keep latest Geography, drop the old one
        if "Geography_old" in result.columns:
            result["Geography"] = result["Geography"].fillna(result["Geography_old"])
            result = result.drop(columns=["Geography_old"])

    if geo is not None:
        result = result[result['Geocode'] == geo]

    return result.reset_index(drop=True)
