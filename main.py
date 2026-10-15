"""
main.py
-------
Runs the complete data cleaning & reporting automation pipeline:
  1. Load raw (messy) data
  2. Run the automated cleaning pipeline (with full audit log)
  3. Score data quality before and after
  4. Generate the automated Excel report (summary, charts, cleaning log)
  5. Save the cleaned dataset

Usage:
    python main.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.cleaning import run_cleaning_pipeline
from src.quality_metrics import quality_comparison
from src.report_generator import build_report

RAW_DATA_PATH = "data/raw_customer_orders.csv"


def main():
    print("=" * 60)
    print("DATA CLEANING & REPORTING AUTOMATION")
    print("=" * 60)

    print("\n[1/4] Loading raw data and running cleaning pipeline...")
    raw_df, cleaned_df, log_df = run_cleaning_pipeline(RAW_DATA_PATH)
    print(f"    -> Raw: {len(raw_df)} rows -> Cleaned: {len(cleaned_df)} rows")
    print(f"    -> {len(log_df)} cleaning actions logged, "
          f"{int(log_df['rows_affected'].sum())} total values fixed")

    print("\n[2/4] Scoring data quality (before vs. after)...")
    quality_df = quality_comparison(raw_df, cleaned_df)
    print(quality_df.to_string(index=False))

    print("\n[3/4] Generating automated Excel report...")
    Path("outputs").mkdir(exist_ok=True)
    build_report(raw_df, cleaned_df, log_df, quality_df, "outputs/Data_Quality_Report.xlsx")

    print("\n[4/4] Saving cleaned dataset and logs...")
    cleaned_df.to_csv("data/cleaned_customer_orders.csv", index=False)
    log_df.to_csv("outputs/cleaning_log.csv", index=False)
    quality_df.to_csv("outputs/quality_comparison.csv", index=False)

    print("\nPipeline complete.")
    print("    -> data/cleaned_customer_orders.csv")
    print("    -> outputs/Data_Quality_Report.xlsx")
    print("    -> outputs/cleaning_log.csv")
    print("    -> outputs/quality_comparison.csv")
    print("\nTo explore results interactively, run:  streamlit run app.py")


if __name__ == "__main__":
    main()
