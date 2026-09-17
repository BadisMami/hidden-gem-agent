## 2026-09-14

### Completed
- Investigated internship sourcing workflow and monitoring architecture
- Analyzed Hudl careers site and identified Greenhouse job board integration
- Discovered and validated public Greenhouse API endpoint for internship retrieval
- Built first live Greenhouse internship monitor
- Implemented internship filtering logic for Greenhouse job listings
- Successfully retrieved live internship openings from Hudl
- Added support for Software Engineering, Software QA Engineering, and Product Management internship discovery
- Integrated Greenhouse internship data into project internship dataset
- Updated internship records with live opportunities from external sources
- Debugged recommendation pipeline and traced data flow through CSV files, SQLite database, and recommendation engine
- Verified end-to-end internship discovery workflow
- Successfully displayed live Hudl internship opportunities in recommendation results
- Established foundation for future multi-company Greenhouse monitoring

### Status
Phase 1 MVP Complete

First Live Internship Source Integrated

Greenhouse Monitoring Prototype Complete

### Next Steps
- Refactor Greenhouse monitor to support multiple companies
- Store Greenhouse companies in company registry
- Automate internship database updates
- Add additional Greenhouse-based companies
- Implement Lever monitoring support
- Implement Workday monitoring support
- Improve internship role classification and matching logic
- Build automated internship monitoring pipeline
- Add internship change detection
- Add automated notification system

## 2026-09-17

### Completed
- Full repository audit: traced data flow, found `database_loader.py` was
  destroying the SQLite schema on every run via `to_sql(if_exists="replace")`
- Security cleanup: removed hardcoded personal phone numbers from
  `sms_alerts.py`, moved Twilio config to environment variables, added
  `.env.example`, fixed `requirements.txt` (was UTF-16 and missing most
  actual dependencies)
- Migrated `resume_parser.py` from deprecated `fitz` import to `pymupdf`;
  fixed OCR temp-image and uploaded-resume temp-file leaks
- Fixed a real regression in `skills_extractor.py`: "ROS" had been removed
  entirely from `KNOWN_SKILLS` (as a blunt fix for it matching inside
  "Microsoft") instead of using the word-boundary regex the file already
  uses everywhere else; re-added ROS/Arduino/FPGA with proper `\b` boundaries
  and verified "Microsoft" no longer false-matches ROS
- Built `role_classifier.py` (deterministic title -> SWE/ML/Data/Embedded/
  Firmware/Hardware/Cybersecurity/Robotics/Product/Other) and `url_utils.py`
  (`clean_url` for HTML-anchor-polluted URLs)
- Rewrote `database_setup.py` with an idempotent migration that adds the new
  internships schema (`external_job_id`, `source_platform`, `date_discovered`,
  `last_seen`, `is_active`, `dedup_key`) in place, without dropping existing
  rows (handled the case where the old table had no `id`/PK at all)
- Added `database_monitor.py::upsert_internship()` - dedup-aware insert/update
  keyed on `source_platform+company+external_job_id` (or
  `company+title+location+application_url` when no external id exists);
  fixed a crash bug where the old `add_internship()` called
  `get_user_skills()` with no arguments
- Made `greenhouse_monitor.py` fully generic: takes `(company_name,
  board_name)`, detects internships via title OR Employment Type metadata,
  classifies role via `role_classifier`, cleans URLs, extracts
  `external_job_id`. Verified live against Hudl - correctly classifies
  "Product Management Intern" as `Product` instead of `SWE`
- Rewrote `internship_monitor_service.py`: registry-driven dispatch by
  platform, per-company error isolation, run summary, alerts only on newly
  inserted internships. Verified idempotent (second run: 0 new internships,
  0 new alerts) against live Hudl data
- Extended `data/company_registry.csv` with `platform`/`career_url`/
  `platform_identifier`/`enabled` columns; configured Hudl as the first
  verified `greenhouse` entry; merged in the remaining hidden-gem companies
  from `companies.csv` as `platform=custom` (not yet wired to a normalized
  adapter)
- Soft-disabled (`is_active=0`, not deleted) legacy CSV-seeded internship
  rows that were superseded by live Greenhouse data, plus internships from
  companies outside the hidden-gem product direction (OpenAI, Anthropic,
  Palantir, Stripe, Databricks, Snowflake, Anduril, Perplexity) that had
  been seeded into `data/internships.csv` and the database
- Updated `dashboard.py`: search now covers company/title/location/role
  type (was title-only), added a sidebar refresh button
  (`st.cache_data.clear()`), clickable Apply links via `LinkColumn`, a table
  name allowlist on the SQL query, uploaded-resume temp-file cleanup, and
  empty-state messages; verified in-browser via Claude in Chrome
- Added a pytest suite (33 tests) covering role classification, URL
  cleanup, mocked Greenhouse response parsing (title- and metadata-based
  intern detection, HTML-polluted URLs, network failures), dedup/upsert
  behavior, alert-only-on-first-discovery, and skill-extraction regex edge
  cases
- Rewrote `README.md` (previously empty) with architecture, setup, env
  vars, and run instructions

### Status
Success criteria met for the Hudl/Greenhouse milestone: registry-driven
config, generic adapter, live SQLite insertion, idempotent re-runs, alerts
only on first discovery, correct Product vs. SWE classification, dashboard
shows live data with clickable links, per-company failure isolation, no
hardcoded credentials.

### Next Steps
- Build a normalized adapter for `platform=custom` companies so they flow
  into SQLite like Greenhouse does (today they're reported as "skipped, no
  adapter" in the monitor summary)
- Implement generic Lever support, verified against a real Lever-hosted
  company before enabling more
- Add per-user stored resumes so monitor-run alerts can score by skill
  match rather than only declared interest
- Consider consolidating `companies.csv`/`company_database.py` (role-flag
  reference table) with `company_registry.csv` (monitoring config) if the
  duplication becomes a maintenance burden

## 2026-09-17 (continued) - Jibe/SuccessFactors adapter

### Completed
- User asked for coverage beyond Hudl. Checked whether the other 22
  registry companies had public Greenhouse or Lever boards under their
  obvious name slugs - none did (large enterprises here mostly don't run
  startup-style ATS boards)
- Tested `custom_monitor.py` against real career pages (Garmin, John Deere,
  Target, Chipotle): confirmed it only surfaces navigation/landing-page
  links ("Internships" category page, even a false-positive marketing page
  matching the word "student"), not individual job postings - wiring this
  into the database as-is would have inserted misleading fake internship
  records, so it was deliberately not connected
- Used a real browser (network tab inspection) to find Garmin's actual
  job-data API: `careers.garmin.com/api/jobs` - a public, unauthenticated
  JSON endpoint from the "Jibe" / SAP SuccessFactors Recruiting Marketing
  platform, with a genuine `tags3=Intern` server-side filter (exact
  detection, not keyword guessing) and structured fields (req_id, title,
  full_location, apply_url)
- Verified the same `/api/jobs` pattern against all other `platform=custom`
  registry companies; State Farm (`jobs.statefarm.com`) also runs Jibe and
  returned live data (currently 0 internships posted - verified as a real
  empty result, not a broken filter). The rest returned 403/404/302/500 -
  not verified, left as `platform=custom`, not guessed at further
- Built `company_monitors/jibe_monitor.py::get_jibe_internships()`,
  wired into `internship_monitor_service.py`, added
  `tests/test_jibe_monitor.py` (5 mocked tests)
- Configured Garmin and State Farm as `platform=jibe` in
  `company_registry.csv` with their real API hosts as `platform_identifier`
- Ran the monitor live: 34 real Garmin internships inserted (9 alerts for
  the registered SWE/ML/Embedded-interested user), State Farm correctly
  returned 0. Re-ran to confirm idempotency: 0 new, 0 new alerts

### Status
Coverage expanded from 1 to 2 live-monitored companies (Hudl via
Greenhouse, Garmin + State Farm via Jibe), 20 companies remain
`platform=custom` pending individual investigation (no adapter built for
suspected-not-yet-verified platforms).

### Next Steps
- Investigate the remaining 20 `platform=custom` companies one at a time
  in a real browser (watch the network tab on their careers page) rather
  than guessing - Jibe was found this way, more may be on it or on
  Workday/iCIMS-standalone

## 2026-09-17 (continued) - registry expansion + generic scraper fallback

### Completed
- Curated 25 more hidden-gem companies into `data/company_registry.csv`
  via web search (McKesson, Cigna, Liberty Mutual, USAA, MassMutual,
  Northwestern Mutual, Truist, Charles Schwab, Edward Jones, Southwest
  Airlines, FedEx, Home Depot, Lowe's, Dick's Sporting Goods, Kroger,
  Illinois Tool Works, GE Aerospace, Boeing, Duke Energy, UnitedHealth
  Group, Parker Hannifin, Eaton, Mercury Insurance, PepsiCo, Procter &
  Gamble) - all with real, sourced career URLs
- Added 17 defense contractors spanning big/medium/small tiers per user
  request (Northrop Grumman, General Dynamics, BAE Systems Inc,
  Huntington Ingalls Industries, Leidos, Booz Allen Hamilton, SAIC, CACI
  International, Textron Systems, Leonardo DRS, Kratos Defense, Mercury
  Systems, ManTech, Parsons Corporation, Peraton, MITRE Corporation,
  Johns Hopkins Applied Physics Laboratory). Registry grew from 23 to
  65 companies total across the session
- Built `company_monitors/generic_browser_monitor.py` - a headless-browser
  (Playwright/Chromium) fallback that can attempt discovery against any
  `platform=custom` career page regardless of underlying ATS, since a
  plain HTTP request can't render most of these sites' JS. Filters
  results by word-boundary intern-title match, excludes generic nav
  labels, and requires a job-id-shaped URL to reject category-page links
- Finished wiring in `eightfold_monitor.py` and `oracle_orc_monitor.py`
  (built but not connected in the previous entry) - John Deere is
  `platform=eightfold`, Honeywell is `platform=oracle_orc`. Found and
  added Eaton as a second Eightfold company along the way
- Wired `send_sms_alert()` into the alert-creation path - a real text is
  now attempted for every new match (no-ops safely without Twilio
  credentials configured, which the user hasn't done yet - that requires
  account creation Claude Code can't perform on their behalf)
- Fixed a real bug: `requirements.txt` had been UTF-16-encoded since the
  very first "fix" of it and was never verified at the byte level
- Full live run across all 65 companies: 245 jobs retrieved, 211 new
  internships inserted, 26 alerts created. The generic browser scraper
  found real results for 24 of 59 `custom`-platform companies (154
  postings), including RTX and Caterpillar where direct API
  investigation had previously stalled

### Status
Live, structured monitoring for 6 companies (Hudl, Garmin, State Farm,
John Deere, Eaton, Honeywell). Best-effort browser-scraped monitoring
covering 24 more companies with real data. 35 `custom` companies still
return nothing (blocked/no matching search box/genuinely no postings -
indistinguishable without per-company follow-up). SMS code path is live
but untested end-to-end since Twilio isn't configured.

### Next Steps
- User is setting up a Twilio account; once credentials are provided,
  verify `send_sms_alert()` actually delivers a text end-to-end
- Investigate the ~35 zero-result `custom` companies individually if
  broader coverage matters more than effort saved - the generic scraper
  found real data for a wide platform variety already, so remaining
  companies likely need either a different search-trigger approach or
  are genuinely blocking headless browsers
- No scheduler exists yet - monitor only runs when manually invoked
- Re-run the full 65-company monitor a second time to confirm idempotency
  held at this scale (verified previously only for the native-adapter
  subset)
- Same Lever/per-user-resume/companies.csv-consolidation items as above