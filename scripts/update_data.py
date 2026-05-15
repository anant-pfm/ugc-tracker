#!/usr/bin/env python3
"""
UGC Tracker — Data Update Script
Usage: python scripts/update_data.py path/to/UGC_Production_Tracker.xlsx
Reads Monthwise and Dump sheets, generates data.js in the root directory.
"""

import sys, os, json, math
import pandas as pd
from datetime import datetime

def clean(v):
    if v is None: return ''
    if isinstance(v, float) and math.isnan(v): return ''
    s = str(v)
    if s.endswith('.0') and s[:-2].lstrip('-').isdigit(): s = s[:-2]
    return '' if s in ['nan', 'None'] else s.strip()

def cn(v):
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v): return 0
        return round(v, 2)
    return v

def process_monthwise(xl_path):
    df = pd.read_excel(xl_path, sheet_name='Monthwise', header=None)
    data = df.iloc[4:][df.iloc[4:][3].notna()].reset_index(drop=True)
    rows = []
    for _, r in data.iterrows():
        wk = ''
        for idx in [24, 21, 20]:
            if idx < len(r) and pd.notna(r[idx]):
                try: wk = str(r[idx])[:10]; break
                except: pass
        rows.append([
            clean(r[2]),   # 0: Production Show_id (col C)
            clean(r[0]),   # 1: week_month
            clean(r[3]),   # 2: show_name
            clean(r[4]),   # 3: prod_status
            clean(r[5]),   # 4: writer
            clean(r[6]),   # 5: pod_lead
            clean(r[7]),   # 6: producer
            clean(r[8]),   # 7: Scripts to record (col I)
            cn(r[9]) if pd.notna(r[9]) else '',  # 8: Duration Live hrs (col J)
            clean(r[10]),  # 9:  TTD Scripts (col K)
            clean(r[11]),  # 10: TTD ER (col L)
            clean(r[12]),  # 11: TTD Release (col M)
            clean(r[13]),  # 12: Script target / Week's Target (col N)
            clean(r[14]),  # 13: Scripts submitted (col O)
            clean(r[15]),  # 14: Scripts WC (col P)
            clean(r[16]),  # 15: Missed by scripting (col Q)
            clean(r[17]),  # 16: ER target / Week's Target (col R)
            clean(r[18]),  # 17: ER approved (col S)
            clean(r[19]),  # 18: Approval pending (col T)
            clean(r[20]),  # 19: Release target / Week's Target (col U)
            clean(r[21]),  # 20: Live episodes (col V)
            clean(r[22]),  # 21: Missed by prod (col W)
            wk,            # 22: week_start_date
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
        a=('Under Review (scripts)', 'sum'), b=('Approved (scripts)', 'sum'),
        c=('Released (eps)', 'sum'), d=('Under Review (word count)', 'sum'),
        e=('Released (hr)', 'sum'),
    ).sort_values(['month_sort', 'Show Title']).reset_index(drop=True)
    return [[str(r['Show ID']), str(r['Show Title']), str(r['month_key']), str(r['month_sort']),
             cn(r.a), cn(r.b), cn(r.c), cn(r.d), cn(r.e)] for _, r in grp.iterrows()]

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_data.py path/to/file.xlsx")
        sys.exit(1)
    xl_path = sys.argv[1]
    if not os.path.exists(xl_path):
        print(f"File not found: {xl_path}"); sys.exit(1)

    print(f"Reading {xl_path} ...")
    weekly = process_monthwise(xl_path)
    yearly = process_dump(xl_path)
    print(f"  Weekly rows: {len(weekly)}, Yearly rows: {len(yearly)}")
    print(f"  Weeks: {list(set(r[1] for r in weekly))}")

    today = datetime.today().strftime('%d %b %Y')
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.js')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"""// Auto-generated {today} from {os.path.basename(xl_path)}
// To regenerate: python scripts/update_data.py path/to/file.xlsx
window.WDATA = {json.dumps(weekly, ensure_ascii=False)};
window.YDATA = {json.dumps(yearly, ensure_ascii=False)};
""")
    print(f"Written to {out_path}")
    print("Done! Commit and push to redeploy.")

if __name__ == '__main__':
    main()
