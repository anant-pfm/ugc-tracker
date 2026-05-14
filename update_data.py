#!/usr/bin/env python3
"""
UGC Tracker — Data Update Script
Usage: python scripts/update_data.py path/to/UGC_Production_Tracker.xlsx

Reads Monthwise and Dump sheets, generates data.js in the root directory.
Run this every time you upload a new version of the Excel file.
"""

import sys, os, json, math
import pandas as pd
from datetime import datetime

def clean(v):
    if v is None: return ''
    if isinstance(v, float) and math.isnan(v): return ''
    s = str(v)
    if s.endswith('.0') and s[:-2].lstrip('-').isdigit(): s = s[:-2]
    if s in ['nan', 'None']: return ''
    return s.strip()

def clean_num(v):
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v): return 0
        return round(v, 2)
    return v

def process_monthwise(xl_path):
    df = pd.read_excel(xl_path, sheet_name='Monthwise', header=None)
    data = df.iloc[4:].copy()
    data = data[data[3].notna()].reset_index(drop=True)
    rows = []
    for _, r in data.iterrows():
        wk_start = ''
        # week start is in col 21 (new file) or 20 (old file)
        for idx in [21, 20]:
            if idx < len(r) and pd.notna(r[idx]):
                try:
                    wk_start = str(r[idx])[:10]
                    break
                except: pass
        rows.append([
            clean(r[0]),   # week_month
            clean(r[3]),   # show_name
            clean(r[4]),   # prod_status
            clean(r[5]),   # writer
            clean(r[6]),   # pod_lead
            clean(r[7]),   # producer
            clean(r[8]),   # till_date_scripts
            clean(r[10]),  # j_target (Week's Target - scripting)
            clean(r[11]),  # scripts_submitted
            clean(r[12]),  # scripts_wc
            clean(r[14]),  # n_target (Week's Target - ER)
            clean(r[15]),  # er_approved
            clean(r[16]),  # approval_pending
            clean(r[17]),  # q_target (Week's Target - prod)
            clean(r[18]),  # live_episodes
            wk_start,
        ])
    return rows

def process_dump(xl_path):
    df = pd.read_excel(xl_path, sheet_name='Dump', header=0)
    df = df[df['Period'] != 'Period'].copy()
    df['Period'] = pd.to_datetime(df['Period'], errors='coerce')
    df = df.dropna(subset=['Period'])
    df['month_key'] = df['Period'].dt.strftime('%b %Y')
    df['month_sort'] = df['Period'].dt.strftime('%Y-%m')
    for col in ['Under Review (scripts)', 'Approved (scripts)', 'Released (eps)',
                'Under Review (word count)', 'Released (hr)']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    grp = df.groupby(['Show ID', 'Show Title', 'month_key', 'month_sort'], as_index=False).agg(
        scripts_sub=('Under Review (scripts)', 'sum'),
        er_scripts=('Approved (scripts)', 'sum'),
        ep_live=('Released (eps)', 'sum'),
        scripts_wc=('Under Review (word count)', 'sum'),
        ep_live_hr=('Released (hr)', 'sum'),
    )
    grp = grp.sort_values(['month_sort', 'Show Title']).reset_index(drop=True)
    rows = []
    for _, r in grp.iterrows():
        rows.append([
            str(r['Show ID']), str(r['Show Title']),
            str(r['month_key']), str(r['month_sort']),
            clean_num(r['scripts_sub']), clean_num(r['er_scripts']),
            clean_num(r['ep_live']), clean_num(r['scripts_wc']),
            clean_num(r['ep_live_hr']),
        ])
    return rows

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_data.py path/to/file.xlsx")
        sys.exit(1)

    xl_path = sys.argv[1]
    if not os.path.exists(xl_path):
        print(f"File not found: {xl_path}")
        sys.exit(1)

    print(f"Reading {xl_path} ...")
    weekly = process_monthwise(xl_path)
    yearly = process_dump(xl_path)
    print(f"  Weekly rows: {len(weekly)}")
    print(f"  Yearly rows: {len(yearly)}")

    today = datetime.today().strftime('%d %b %Y')
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.js')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"""// ─────────────────────────────────────────────────────────────────
//  UGC PRODUCTION TRACKER — DATA FILE
//  Auto-generated on {today}
//  Source: {os.path.basename(xl_path)}
//
//  To regenerate: python scripts/update_data.py path/to/file.xlsx
// ─────────────────────────────────────────────────────────────────

// WEEKLY DATA (Monthwise sheet)
// Columns: [week_month, show_name, prod_status, writer, pod_lead, producer,
//           till_date, j_target, scripts_submitted, scripts_wc,
//           n_target, er_approved, approval_pending,
//           q_target, live_episodes, week_start_date]
window.WDATA = {json.dumps(weekly, ensure_ascii=False)};

// YEARLY DATA (Dump sheet, aggregated by Show + Month)
// Columns: [show_id, show_title, month_label, month_sort,
//           scripts_submitted, er_scripts, ep_live, scripts_wc, ep_live_hr]
window.YDATA = {json.dumps(yearly, ensure_ascii=False)};
""")

    print(f"Written to {out_path}")
    print("Done! Commit data.js and push to redeploy on Vercel.")

if __name__ == '__main__':
    main()
