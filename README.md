# Hidden Gem Internship Discovery Agent

An agent that automatically discovers technical internships at recognizable
**non-Big-Tech** companies — Target, Chipotle, Progressive, State Farm, John
Deere, Garmin, Hudl, and similar "hidden gem" employers that CS/CE students
don't usually think to check. It's tailored to one person (me): only
SWE, ML, Embedded, Firmware, Robotics, and Hardware/FPGA internships trigger a
text. It is a discovery and alerting tool, not an application tracker: it does not track saved jobs, applied status, or
interview history.

## Architecture

```
data/company_registry.csv (which companies, which platform, enabled?)
        |
        v
internship_monitor_service.py  --dispatches by platform-->  company_monitors/
        |                                                    greenhouse, jibe, eightfold,
        |                                                    oracle_orc, workday,
        |                                                    successfactors, taleo, adp,
        |                                                    generic_browser (custom)
        v
database_monitor.py (dedup-aware upsert)
        |
        v
database/internship_agent.db (SQLite - runtime source of truth)
        |
        +--> dashboard.py (Streamlit: search, alerts, companies)
        +--> database_alerts.py (alerts on new target-role matches)
```

Company monitoring is registry-driven: `data/company_registry.csv` lists each
company's `platform` and its `platform_identifier` (format per platform below;
`custom` companies use `career_url` instead).
`internship_monitor_service.py`
loads only `enabled=yes` rows, dispatches to the matching adapter, and
inserts normalized internship records directly into SQLite via a
dedup-aware `upsert_internship()` — re-running the monitor never creates
duplicate rows, and alerts are only generated the first time a job is seen.
A repost of a role I was already texted about (same company + title) in the
last 14 days doesn't text again.

Every posting is stored and classified by `role_classifier.py`, but only
roles in `TARGET_ROLES` (`SWE`, `ML`, `Embedded`, `Firmware`, `Robotics`, `Hardware`, defined in
`src/role_classifier.py`) create an alert and a text. Edit that set to
change what you get texted about.

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
of truth for internships and alerts.

```powershell
# Create or safely migrate the schema (idempotent, preserves existing rows)
python src/database_setup.py
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
clickable Apply links, filtered to my target roles by default), Alerts
(newest first), Companies (the registry). Use the sidebar "Refresh Data" button
after running the monitor to pick up new rows without restarting Streamlit.

## Tests

```powershell
python -m pytest tests/ -v
```

Covers role classification, URL cleanup, mocked Greenhouse parsing,
internship dedup/upsert behavior, alert-only-on-new-job logic, and
target-role alert filtering.

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

Structured adapters (real title/location/apply-link fields from the
platform's own API). `platform_identifier` format in parentheses:

- **Greenhouse** (`board_token`) - Hudl.
- **Jibe** (`api_host`) - Garmin, State Farm, Johns Hopkins APL. Uses the
  `tags3=Intern` facet, falling back to a keyword search for sites
  without it (APL).
- **Eightfold.ai** (`api_host|company_domain`) - John Deere, Lockheed
  Martin, Eaton, CACI, Northrop Grumman (`jobs.northropgrumman.com|ngc.com`).
- **Oracle Recruiting Cloud** (`career_site_host|tenant_host|site_number|site_name`)
  - Honeywell.
- **Workday** (`<tenant>.wd<N>.myworkdayjobs.com|tenant|site`) - Leidos,
  Parsons, General Dynamics IT, Booz Allen, Home Depot, USAA. Find the
  tenant/site in any job link on the company's careers site.
- **SuccessFactors Career Site Builder** (`host`) - HII (shipbuilding and
  Mission Technologies sites). Parses the server-rendered `/search/?q=intern`
  page.
- **Taleo** (`host|career_section|portal_id`) - Textron Systems. The
  `portal` id is on the `rest/jobboard/searchjobs` request in the browser's
  network tab.
- **ADP Workforce Now** (`site_name|client_id`, needs the browser) -
  Mercury Systems. ADP's API needs a session token, so the page is loaded
  in the headless browser and its own API response is read.

Every keyword-search adapter re-filters titles with a word-boundary
`intern|internship|co-op` regex, so "Internal Auditor" / "International"
results don't leak through.

Best-effort fallback for everything else:

- **`custom`** - `generic_browser_monitor.py` loads `career_url` in headless
  Chromium (including iframes), takes links whose text contains
  "intern"/"internship" and whose URL has a 4+ digit job id, and if there
  are none, tries the page's job-search box. Point `career_url` at the
  site's intern search-results page when one exists (MITRE, SAIC, ManTech
  do this) - landing pages often have no job links at all. Location is
  always "Unknown".

## Limitations

- Role classification (`src/role_classifier.py`) is deterministic
  keyword matching - titles it hasn't seen land in `Other` and never
  alert. Generic titles like "2027 Engineering Intern" are `Other`.
- Some `custom` companies still return nothing (the site blocks headless
  browsers or needs multi-step interaction). Check the network tab for a
  Workday / Eightfold / Taleo / SuccessFactors API before trying anything
  else - most "custom" sites turned out to be one of those.
