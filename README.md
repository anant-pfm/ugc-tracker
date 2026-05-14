# UGC Production Tracker

Internal dashboard for tracking UGC show production across Scripting, ER Review, and Production stages.

## Live on Vercel

Once deployed, the dashboard is a single static site — no server, no database.

---

## Repository structure

```
ugc-tracker/
├── index.html          ← Dashboard UI (all CSS + JS inline)
├── data.js             ← All tracker data (regenerate this when Excel updates)
├── scripts/
│   └── update_data.py  ← Python script to regenerate data.js from Excel
└── README.md
```

---

## Deploying to Vercel

### First time

1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → Add New Project → Import the GitHub repo
3. Vercel auto-detects it as a static site — click **Deploy**
4. Your dashboard is live at `https://your-project.vercel.app`

### Every subsequent deploy

Just push a commit with the updated `data.js` — Vercel auto-redeploys in ~30 seconds.

---

## Updating data (weekly workflow)

Each time you have a new version of the Excel file:

### Option A — Python script (recommended)

```bash
# Install dependency once
pip install pandas openpyxl

# Run the update script
python scripts/update_data.py path/to/UGC_Production_Tracker.xlsx
```

This overwrites `data.js` with fresh data. Then commit and push:

```bash
git add data.js
git commit -m "Data update: <date>"
git push
```

Vercel picks up the push and redeploys automatically.

### Option B — Manual

Open `data.js` and replace the `window.WDATA` and `window.YDATA` arrays with your new data.

---

## Dashboard features

### Weekly Tracker
- **Week filter** — toggle between available weeks (defaults to latest)
- **Last week targets** toggle — shows previous week's targets side-by-side for comparison
- **Search + filters** — filter by show name, status, writer, POD lead
- **Editable targets** — J (Script Target), N (ER Target), Q (Release Target) can be typed in and saved; they persist in browser localStorage across page refreshes
- **Export CSV** — exports the current filtered view, including prev-week columns if toggle is on

### Yearly Tracker
- **Month filter** — click one month to filter; click a second month to enter compare mode
- **Compare mode** — side-by-side columns for two months with a Diff column (green = increase, red = decrease)
- **Search** — searches by show name or show ID
- **Export CSV** — exports current view, diff-aware in compare mode

### Global
- **Zoom control** (25–100%) in the top bar — persists across sessions

---

## Column mapping (for reference)

### Weekly (Monthwise sheet)
| Dashboard column | Excel column |
|---|---|
| Week / Month | A |
| Show name | D |
| Production status | E |
| Writer | F |
| POD lead | G |
| Producer | H |
| Till date scripts | I |
| Script target (J) | K |
| Scripts submitted | L |
| Scripts WC | M |
| ER target (N) | O |
| ER approved | P |
| Approval pending | Q |
| Release target (Q) | R |
| Live episodes | S |
| Week start date | V |

### Yearly (Dump sheet, aggregated)
| Dashboard column | Excel column |
|---|---|
| Show ID | B |
| Show title | C |
| Scripts submitted | D (Under Review scripts) |
| Editorial reviewed scripts | E (Approved scripts) |
| Eps made live | P (Released eps) |
| Scripts WC | R (Under Review word count) |
| Ep made live duration (hr) | AE (Released hr) |
