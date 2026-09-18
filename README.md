# Hidden Gem Internship Discovery Agent

An agent that automatically discovers technical internships at recognizable
**non-Big-Tech** companies — Target, Chipotle, Progressive, State Farm, John
Deere, Garmin, Hudl, and similar "hidden gem" employers that CS/CE students
don't usually think to check. It is a discovery and alerting tool, not an
application tracker: it does not track saved jobs, applied status, or
interview history.

## Architecture

```
data/company_registry.csv (which companies, which platform, enabled?)
        |
        v
internship_monitor_service.py  --dispatches by platform-->  company_monitors/
        |                                                    greenhouse_monitor.py
        |                                                    jibe_monitor.py
        |                                                    (lever/workday: planned)
        v
database_monitor.py (dedup-aware upsert)
        |
        v
database/internship_agent.db (SQLite - runtime source of truth)
        |
        +--> dashboard.py (Streamlit: search, recommendations, alerts)
        +--> database_alerts.py / user_matcher.py (alerts on new matches)
```

Company monitoring is registry-driven: `data/company_registry.csv` lists each
company's `platform` (`greenhouse`, `jibe`, or `custom`) and, for Greenhouse
and Jibe, `platform_identifier` (the board token, or the API host for Jibe).
`internship_monitor_service.py`
loads only `enabled=yes` rows, dispatches to the matching adapter, and
inserts normalized internship records directly into SQLite via a
dedup-aware `upsert_internship()` — re-running the monitor never creates
duplicate rows, and alerts are only generated the first time a job is seen.

`data/companies.csv` is a separate, older reference table (role-flag
columns) seeded into the database's `companies` table and shown in the
dashboard's Companies tab - it's static reference data, not part of the
live-monitoring pipeline (that's `data/company_registry.csv`, described
above).

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

The `playwright install chromium` step is required - it downloads a
headless browser used by `company_monitors/generic_browser_monitor.py`
to render JS-heavy career sites that a plain HTTP request can't see
through (most `platform=custom` companies fall into this category).

Copy `.env.example` to `.env` if you want SMS alerts (optional, see below).

## Database

The SQLite database at `database/internship_agent.db` is the runtime source
of truth for internships. CSV files remain useful for seed/reference data.

```powershell
# Create or safely migrate the schema (idempotent, preserves existing rows)
python src/database_setup.py

# Seed companies/users/internships from the CSV files
python src/database_loader.py
```

## Running the monitor

```powershell
python src/internship_monitor_service.py
```

Prints a run summary (companies checked/successful/failed/skipped, jobs
retrieved, new internships inserted, alerts created). Safe to re-run on a
schedule — only genuinely new postings create new rows and alerts.

To run the Greenhouse adapter directly against one company:

```powershell
python src/company_monitors/greenhouse_monitor.py
```

## Dashboard

```powershell
streamlit run src/dashboard.py
```

Tabs: Internships (search across company/title/location/role type, with
clickable Apply links), Recommendations (from an uploaded resume's detected
skills), Alerts, Companies, Users. Use the sidebar "Refresh Data" button
after running the monitor to pick up new rows without restarting Streamlit.

## Tests

```powershell
python -m pytest tests/ -v
```

Covers role classification, URL cleanup, mocked Greenhouse parsing,
internship dedup/upsert behavior, alert-only-on-new-job logic, and resume
skill-extraction regex edge cases (C++, Node.js variants, ROS vs. false
match inside "Microsoft").

## Environment variables

SMS alerts are optional but wired into the pipeline:
`internship_monitor_service.py` calls `send_sms_alert()` every time a new
internship alert is created (not just when the DB alert is saved). Sending
uses a free email-to-SMS carrier gateway (e.g. `number@tmomail.net` for
T-Mobile) via Gmail SMTP - not a paid SMS API - since this is a
single-user personal alert, not a product sending texts to other people.
Copy `.env.example` to `.env` and set:

- `EMAIL_SENDER_ADDRESS` - a Gmail address to send from
- `EMAIL_APP_PASSWORD` - a Gmail **App Password** (not your real
  password), generated at https://myaccount.google.com/apppasswords
  (requires 2-Step Verification enabled first)
- `NOTIFICATION_PHONE_NUMBER` - your phone number, digits only
- `SMS_CARRIER_GATEWAY` - your carrier's email-to-SMS domain (`vtext.com`
  for Verizon, `txt.att.net` for AT&T, `tmomail.net` for T-Mobile, etc.)

If unset, `send_sms_alert()` prints a message and skips sending rather than
failing - the rest of the pipeline (DB alerts, dashboard) works either way.
`.env` is gitignored — never commit real credentials.

## Supported platforms

Structured, high-accuracy adapters (real title/location/apply-link fields
from the platform's own API):

- **Greenhouse** — `get_greenhouse_internships(company_name, board_name)`.
  Verified live against Hudl.
- **Jibe / SAP SuccessFactors Recruiting Marketing** —
  `get_jibe_internships(company_name, api_host)`. Verified live against
  Garmin and State Farm. Exposes a genuine `tags3=Intern` server-side
  filter, so detection is exact rather than keyword-guessed.
- **Eightfold.ai** — `get_eightfold_internships(company_name, api_host,
  company_domain)`. Verified live against John Deere and Eaton. Search is
  keyword-only (no structured intern filter), so results are re-filtered
  client-side with a word-boundary regex to drop false positives like
  "Internal Auditor".
- **Oracle Recruiting Cloud (Fusion HCM)** —
  `get_oracle_orc_internships(company_name, career_site_host, tenant_host,
  site_number, site_name)`. Verified live against Honeywell (30 real
  internships). Same keyword-only caveat as Eightfold.

Best-effort fallback for everything else:

- **`platform=custom`** (59 of the 65 registry companies) —
  `company_monitors/generic_browser_monitor.py::get_browser_scraped_internships()`
  uses a real headless browser (Playwright/Chromium) to render the career
  page's JS, attempts a job-search-box submission if one exists, then
  extracts links whose text contains "intern"/"internship" as a whole
  word, isn't a generic nav label ("Internships", "Search Jobs", etc.),
  and points at what looks like an actual job-detail URL (contains a
  4+ digit id). This is what makes "any" custom career page possible to
  monitor at all without hand-building an adapter per company - a plain
  HTTP request can't see through most of these sites' JS rendering.

  **Real result from a full run across all 65 registry companies
  (2026-09-17): 24 of 59 `custom` companies produced real internship
  data - 154 postings total** (Caterpillar: 20, Leonardo DRS: 17,
  McKesson: 15, L3Harris: 15, RTX: 10, PepsiCo: 10, and 18 more with
  smaller counts). Notably this succeeded for RTX and Caterpillar, both
  "Phenom People"-platform sites where direct API reverse-engineering had
  stalled earlier - the browser fallback found real postings anyway.
  The other 35 `custom` companies returned 0 (either no search box was
  found/triggered, the site blocks headless browsers, or they may simply
  have no current internships posted).

  **Known limitations of this fallback**: location is always "Unknown"
  (link text alone doesn't reliably contain it); `application_url` quality
  depends on whether the site's link href points at the specific posting
  (usually does) vs. a search-results page; it can't handle career pages
  needing more than one search-box interaction to reach real listings.

- **Lever, Workday** — planned, no adapter built yet. None of the
  registry's `platform=custom` companies were found on public Greenhouse
  or Lever boards when checked (2026-09-17) - if a new company should be
  added, check there before assuming it needs the generic scraper. (Note:
  a couple of `platform=custom` companies - 3M, Duke Energy - turned out
  to run Workday and work fine through the generic browser scraper
  without a dedicated adapter; only build one if the generic scraper
  can't handle a Workday site.)

## Limitations

- Role classification (`src/role_classifier.py`) is deterministic
  keyword matching, not ML-based — titles it hasn't seen may land in
  `Other`.
- Alert matching uses each user's declared interests (`data/users.csv`),
  not a per-user stored resume — there's no per-user resume storage yet,
  so monitor-run alerts can't do skill-level scoring (only the
  Streamlit dashboard's Recommendations tab does, from a freshly uploaded
  resume).
- Custom company career-page monitoring is scrape-only and not yet
  connected to the database pipeline.

## Roadmap

1. For each remaining `platform=custom` company, check whether its career
   site is actually Workday, iCIMS-branded-standalone, or another platform
   with a discoverable JSON API (open the site in a real browser and watch
   the network tab for `/api/` or `myworkdayjobs.com` calls) before
   assuming a scraper is the only option - Jibe was found this way.
2. Generic Lever adapter (`company_monitors/lever_monitor.py` doesn't
   exist yet - create it following the pattern of the other adapters in
   that folder), verified against at least one real Lever-hosted company
   before enabling more.
3. Workday support (tenant-specific, deferred until Greenhouse/Lever are
   stable).
4. The generic browser scraper (`generic_browser_monitor.py`) covers 24
   of 59 `custom` companies as of 2026-09-17 - investigate the remaining
   35 individually (some are DNS/timeout failures worth retrying, others
   need a different search-trigger approach or may genuinely block
   headless browsers).
5. Per-user stored resumes so monitor-run alerts can score by skill match,
   not just declared interest.
6. Set up a scheduler (Windows Task Scheduler, cron, etc.) so the monitor
   runs periodically instead of only on manual invocation.
7. SMS alerts are wired in via email-to-SMS gateway (see Environment
   variables above) - untested end-to-end until `.env` has real Gmail
   App Password + carrier gateway values filled in.
