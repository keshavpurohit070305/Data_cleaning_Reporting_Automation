# Data Cleaning & Reporting Automation

**Thiranex Internship — Task 4**

An automated pipeline that takes a raw, inconsistent business dataset and
turns it into a clean, analysis-ready dataset with a full audit trail, an
automated Excel report, and an interactive Power BI-style dashboard.

## Key Features

- **Automated cleaning pipeline in Python** — a rule-based pipeline handles
  every fix end to end: standardizing inconsistent text casing and
  whitespace, parsing five+ mixed date formats into one consistent format,
  validating emails and phone numbers, correcting invalid numeric values,
  and capping statistical outliers.
- **Missing values, duplicates, and inconsistent data handled systematically**
  — numeric gaps are imputed with the column median, categorical gaps with
  the most frequent value, and both exact and near-duplicate records
  (re-typed order IDs) are detected and removed. Every action is logged
  with the exact number of rows it affected, so the process is auditable
  rather than a black box.
- **Automated reports and visual summaries** — a multi-sheet Excel report
  (summary, before/after data quality, cleaning log, category breakdown,
  and the full cleaned dataset) with native charts is generated on every
  run, alongside an interactive Power BI-style dashboard with slicers that
  cross-filter every chart.

## Expected Outcome

Demonstrates practical data preprocessing, automation, and reporting
efficiency — transforming a messy raw export into clean, trustworthy data
with measurable before/after quality scores and shareable visual reporting,
without manual spreadsheet editing.

## Project Structure

```
thiranex_task4_data_cleaning/
├── app.py                          # Power BI-style Streamlit dashboard
├── main.py                         # Runs the full pipeline end-to-end (script mode)
├── requirements.txt
├── data/
│   ├── generate_messy_data.py      # Generates the synthetic raw (messy) dataset
│   ├── raw_customer_orders.csv     # Raw data (850+ rows, intentionally messy)
│   └── cleaned_customer_orders.csv # Output: cleaned dataset
├── src/
│   ├── cleaning.py                 # Automated cleaning pipeline + audit log
│   ├── quality_metrics.py          # Completeness / uniqueness / validity scoring
│   └── report_generator.py         # Builds the automated Excel report
└── outputs/
    ├── Data_Quality_Report.xlsx    # Automated multi-sheet report with charts
    ├── cleaning_log.csv
    └── quality_comparison.csv
```

## Setup (VS Code)

1. Open this folder in VS Code.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

**Option A — Full pipeline in the terminal** (cleans the data, scores
quality, generates the Excel report):
```bash
python main.py
```

**Option B — Interactive dashboard**:
```bash
streamlit run app.py
```
Opens a Power BI-style dashboard with sidebar slicers (category, state,
status, date range) that cross-filter every chart, KPI cards, a data
quality before/after comparison, the full cleaning log, and a searchable
data explorer.

To regenerate the raw messy dataset from scratch:
```bash
python data/generate_messy_data.py
```

## What the Pipeline Cleans

| Issue | How it's handled |
|---|---|
| Missing values (email, phone, city, quantity, price, etc.) | Numeric → median imputation. Categorical → most frequent value. Contact fields → left blank and flagged rather than guessed. |
| Exact & near-duplicate rows | Detected on full-row content (ignoring order ID) and dropped, keeping the first occurrence. |
| Inconsistent text casing/whitespace | Trimmed and standardized to Title Case. |
| Mixed date formats | Parsed into a single consistent datetime format. |
| Invalid emails / phone numbers | Validated with regex / digit-count rules; invalid entries nulled and flagged. |
| Negative quantities, ₹0 prices | Negatives converted to absolute value; zero prices treated as missing and imputed. |
| Statistical outliers | Capped using the IQR method. |

Every one of these steps is logged with the exact row count it affected —
visible in the **Cleaning Log** tab of the dashboard and the `Cleaning Log`
sheet of the Excel report.

## Tech Stack

Python, pandas, NumPy, openpyxl (Excel report + native charts), Streamlit,
Plotly.
