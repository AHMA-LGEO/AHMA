import os
import pandas as pd
from pathlib import Path
from section2_prep import Section2DataPrep
from section3_prep import Section3DataPrep
from section4_prep import Section4DataPrep
from section5_prep import Section5DataPrep
from section7_prep import Section7DataPrep
from section8_prep import Section8DataPrep
from section9_prep import Section9DataPrep

OUTPUT_DIR = Path(__file__).parent.parent / "throughputs"

SECTION_PREPS = [
    # Section2DataPrep(),
    # Section3DataPrep(),
    Section4DataPrep(),
    # Section5DataPrep(),
    # Section7DataPrep(),
    Section8DataPrep(),
    # Section9DataPrep()
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