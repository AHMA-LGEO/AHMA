import os
import pandas as pd
from pathlib import Path
from table2_prep import Table2DataPrep
from table3_prep import Table3DataPrep
from table4_prep import Table4DataPrep
from table8_prep import Table8DataPrep

OUTPUT_DIR = Path(__file__).parent.parent / "throughputs"

TABLE_PREPS = [
    # Table2DataPrep(),
    Table3DataPrep(),
    # Table4DataPrep(),

    # Table8DataPrep()
    #...
]

def run_all():
    all_outputs: dict[str, pd.DataFrame] = {}

    for prep in TABLE_PREPS:
        results = prep.run_all()
        all_outputs.update(results)

    for table_id, df in all_outputs.items():
        safe_name = table_id.replace(".", "_")
        path = os.path.join(OUTPUT_DIR, f"table_{safe_name}.csv")
        df.to_csv(path, index=False)
        print(f"Saved {table_id}")

    print(f"\n Done.... {len(all_outputs)} tables saved to {OUTPUT_DIR}")
    return all_outputs

if __name__ == "__main__":
    run_all()
