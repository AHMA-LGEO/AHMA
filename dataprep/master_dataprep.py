import os
import pandas as pd
import utils
from pathlib import Path
from section2_prep import Section2DataPrep
from section3_prep import Section3DataPrep
from section4_prep import Section4DataPrep
from section5_prep import Section5DataPrep
from section6_prep import Section6DataPrep
from section7_prep import Section7DataPrep
from section8_prep import Section8DataPrep
from section9_prep import Section9DataPrep
from section10_prep import Section10DataPrep
from section11_prep import Section11DataPrep
from section12_prep import Section12DataPrep

OUTPUT_DIR = Path(__file__).parent.parent / "throughputs"

SECTION_PREPS = [

    # Section2DataPrep(),
    # Section3DataPrep(),
    # Section4DataPrep(),
    Section5DataPrep(),
    # Section6DataPrep(),
    # Section7DataPrep(),
    # Section8DataPrep(),
    # Section9DataPrep(),
    # Section10DataPrep(),
    # Section11DataPrep(),
    # Section12DataPrep()
    #...
]

def count_pcts_over_100(results, pct_counts: dict[str, dict[str, any]]) -> dict[str, dict[str, any]]:
    tables = ""
    for table_id in results.keys():
        tables += f"_{table_id}"
    pct_counts[tables] = {"total": utils.pct_count,
                          "over_100": utils.over_100_count}
    utils.pct_count = 0
    utils.over_100_count = 0
    return pct_counts

def save_pct_summary(pct_counts: dict[str, dict[str, any]]):
    rows = []
    for tables, counts in pct_counts.items():
        row = {'Tables': tables,
               'Percentages Calculated': counts["total"],
               'Percentages over 100': counts["over_100"]}
        rate = round(counts["over_100"]/counts["total"]*100, 2) if counts["total"] != 0 else None
        row['Over 100 Rate'] = f"{rate}%" if rate is not None else "N/A"
        rows.append(row)
    pct_df = pd.DataFrame(rows)
    pct_log_path = os.path.join(OUTPUT_DIR, f"pct_summary.csv")
    pct_df.to_csv(pct_log_path, index=False, encoding='utf-8-sig')

def run_all():
    all_outputs: dict[str, pd.DataFrame] = {}

    pct_counts: dict[str, dict[str, any]] = {}

    for prep in SECTION_PREPS:
        results = prep.run_all()
        all_outputs.update(results)

        pct_counts = count_pcts_over_100(results, pct_counts)

    for table_id, df in all_outputs.items():
        safe_name = table_id.replace(".", "_")
        path = os.path.join(OUTPUT_DIR, f"table_{safe_name}.csv")
        df.to_csv(path, index=False, encoding='utf-8-sig')
        print(f"Saved {table_id}")

    print(f"\n Done.... {len(all_outputs)} tables saved to {OUTPUT_DIR}")

    save_pct_summary(pct_counts)

    return all_outputs

if __name__ == "__main__":
    run_all()
