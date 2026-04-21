import os
import pandas as pd
from pathlib import Path
from dataprep.section2_prep import Section2DataPrep
from dataprep.section3_prep import Section3DataPrep
from dataprep.section4_prep import Section4DataPrep
from dataprep.section8_prep import Section8DataPrep

OUTPUT_DIR = Path(__file__).parent.parent / "throughputs"

SECTION_PREPS = [
    # Section2DataPrep(),
    Section3DataPrep(),
    # Section4DataPrep(),

    # Section8DataPrep()
    #...
]

def run_all():
    all_outputs: dict[str, pd.DataFrame] = {}

    for prep in SECTION_PREPS:
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
