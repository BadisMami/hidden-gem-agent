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

`data/companies.csv` / `company_database.py` / `company_matcher.py` are a
separate, older reference table (role-flag columns) used for manual company
lookup and are not part of the live-monitoring pipeline.

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

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

SMS alerts via Twilio are optional. Copy `.env.example` to `.env` and set:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `NOTIFICATION_PHONE_NUMBER`

If unset, `src/sms_alerts.py` prints a message and skips sending rather than
failing. `.env` is gitignored — never commit real credentials.

## Supported platforms

- **Greenhouse** — fully generic (`get_greenhouse_internships(company_name,
  board_name)`), verified live against Hudl's public job board API.
- **Jibe / SAP SuccessFactors Recruiting Marketing** — fully generic
  (`get_jibe_internships(company_name, api_host)`), verified live against
  Garmin (`careers.garmin.com`, 34 live internships as of 2026-09-17) and
  State Farm (`jobs.statefarm.com`). This platform exposes a genuine
  `tags3=Intern` server-side filter, so detection is exact rather than
  keyword-guessed. Many large non-tech enterprises run career sites on
  this platform under a `careers.<company>.com` or `jobs.<company>.com`
  domain with a public `/api/jobs` endpoint - worth checking for any new
  hidden-gem company before assuming a custom scraper is needed.
- **Custom company career pages** — a best-effort link-scraper
  (`company_monitors/custom_monitor.py`) exists but is not yet wired into
  the monitor service's SQLite pipeline (it returns raw scraped links, not
  normalized internship records - verified against real sites, it mostly
  finds navigation/landing-page links rather than individual job postings,
  since most of these sites are JS-rendered SPAs a plain HTTP fetch can't
  see through). Companies on `platform=custom` are reported as "skipped
  (no adapter)" in the monitor summary rather than fed misleading data.
- **Lever, Workday** — planned, not yet implemented (`lever_monitor.py`,
  `workday_monitor.py` are empty stubs). None of the registry's remaining
  `platform=custom` companies were found on public Greenhouse or Lever
  boards when checked (2026-09-17).

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
2. Generic Lever adapter (`company_monitors/lever_monitor.py`), verified
   against at least one real Lever-hosted company before enabling more.
3. Workday support (tenant-specific, deferred until Greenhouse/Lever are
   stable).
4. Wire `custom_monitor.py` output into a normalized-internship adapter
   only if a company genuinely has no structured API - it currently only
   finds navigation links, not individual postings.
4. Per-user stored resumes so monitor-run alerts can score by skill match,
   not just declared interest.
5. SMS/email notifications on new alerts (Twilio integration exists but is
   optional and untested end-to-end due to trial-account restrictions).
