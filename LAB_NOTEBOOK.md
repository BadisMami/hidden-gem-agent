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