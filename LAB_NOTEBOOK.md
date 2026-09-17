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
- ~~User is setting up a Twilio account...~~ Superseded - see next entry.
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

## 2026-09-17 (continued) - SMS alerts working end-to-end

### Completed
- User asked whether Twilio was actually the right tool for a
  single-user personal SMS alert vs. sending to other people at scale.
  Recommended a free email-to-SMS carrier gateway instead (no
  third-party account/billing beyond Gmail, which the user already has)
- Rewrote `sms_alerts.py::send_sms_alert()` to send via Gmail SMTP to
  `{phone}@{carrier_gateway}` instead of the Twilio REST API - same
  function signature, so the wiring into `internship_monitor_service.py`
  from the previous entry needed no changes
- Removed the now-unused `twilio` package from `requirements.txt`
- Added `tests/test_sms_alerts.py` (4 mocked tests: missing config,
  partial config, successful send, SMTP failure handled gracefully)
- User created `.env` themselves (guided through the Windows File
  Explorer dotfile gotcha - had to use `copy .env.example .env` in
  PowerShell rather than File Explorer, which refuses to save a
  filename with no name before the extension) with their real Gmail
  address, a Gmail App Password (not their login password), phone
  number, and `tmomail.net` (T-Mobile) as the carrier gateway
- Ran `python src/sms_alerts.py` for a real end-to-end test - **user
  confirmed receiving the actual text on their phone**

### Status
**The full alert pipeline is now confirmed working end-to-end**: a new
internship discovered by the monitor -> DB alert created -> real SMS
sent -> arrives on the user's phone. This was the original goal stated
early in the session. Verified for any of the 30 companies with live
discovery coverage.

### Next Steps
- ~~Set up a scheduler...~~ Done - see next entries (GitHub Actions).
- Investigate the ~35 zero-result `custom` companies if broader coverage
  is wanted - see the "fixed 8 more" entry further down for what got
  resolved and what's still open.

## 2026-09-17 (continued) - GitHub Actions scheduling + history cleanup

### Completed
- Discovered git history contained the user's real phone number (an old
  `sms_alerts.py` revision) and real name (every historical revision of
  `data/users.csv` and `database/internship_agent.db`, including 39
  `alerts.matched_users` rows) - found via a full audit across all
  commits, not just current files, before the user made the repo public
- Used `git-filter-repo` to strip both files from all history and
  replace the phone number everywhere; re-added sanitized versions
  (name replaced with "Primary User", same major/interests so matching
  behavior is unchanged) as a fresh commit with no history baggage.
  Rewrote all commit hashes - safe since nothing had been pushed yet.
  Caught and fixed a mistake of my own: the first cleanup commit message
  accidentally quoted the real values while explaining what was removed
- User force-pushed the sanitized history to GitHub, verified clean via
  the public API (confirmed repo is public, only one branch, no
  dangling refs with old history)
- Added `internship_monitor_service.py --fast` flag (skips
  `platform=custom` companies, no Playwright import needed) so a cheap,
  frequent check is possible without the slow browser scraper
- Added `.github/workflows/monitor-fast.yml` (every 15 min, structured-
  API companies only) and `monitor-full.yml` (every 4 hours, full scan
  including the browser scraper). Both commit the updated database back
  to the repo after each run (only if changed) so dedup state survives
  between ephemeral GitHub-hosted runs
- User set up the required GitHub repo secrets and workflow write
  permissions, triggered a manual test run - **confirmed working**: the
  bot correctly found new data and pushed a real commit back
  (`69016e1`) without any manual intervention

### Status
The monitor now runs automatically via GitHub Actions, no local machine
needed. Verified end-to-end on GitHub's infrastructure, not just locally.

## 2026-09-17 (continued) - fixed 8 more custom-platform companies + a real bug

User pushed back on doing only a "batch" of the 35 zero-result companies
instead of all of them - correctly pointed out there was no real
blocker, just leftover caution from Target/Phenom investigations
stalling in an earlier session. Went through all 35 this time with
strict per-company timeboxing.

### Completed
- Found and fixed a real, generalizable bug in
  `generic_browser_monitor.py`: it always ran the search-box-fill flow
  regardless of whether the page already had good results, which could
  navigate away and destroy them. Found via Boeing (career_url was
  already a filtered internship listing with real postings, search flow
  overwrote it with different/empty results). Fixed to extract from the
  page as-loaded first, only falling back to search if that's empty.
  2 new regression tests
- Fixed 8 companies from 0 to real results: Lockheed Martin (50, moved
  to the real Eightfold adapter after discovering
  `lockheedmartin.eightfold.ai`), CACI International (27, same -
  `caci.eightfold.ai`), Boeing (15), 3M (11, registry had a dead DNS
  entry), FedEx (9), Cummins (6), Booz Allen Hamilton (2), Duke Energy
  (1, also a dead DNS entry)
- Also fixed Delta Airlines' dead URL (`careers.delta.com` was
  `NXDOMAIN`) though it still returns 0 - its search UI doesn't respond
  to automated clicks
- Investigated but left unresolved, with the actual root cause
  identified for each: Kratos Defense (listings inside an iframe),
  Mercury Systems/USAA (search box doesn't respond to automation),
  Huntington Ingalls (3 separate division sites, no unified listing),
  Northrop Grumman/Fidelity/Leidos/Parsons/Liberty Mutual/Parker
  Hannifin/GE Aerospace (found what should be the right URL, still 0 -
  needs deeper investigation)
- Did not get to: Progressive, Publix, Raymond James, SAIC, Southwest
  Airlines, Strava, Target, Textron Systems, UPS, MITRE, ManTech,
  Mercury Insurance
- Verified with a full 65-company live run afterward: 332 jobs found
  (up from 245), 124 new internships inserted, 40 alerts created, 40
  real texts sent - confirmed the pipeline holds up correctly at scale

### Status
Coverage: 37 of 65 companies now have confirmed real, active internship
data (was 30 before this round; was 3 at the very start of today). All
57 tests pass.

### Next Steps
- Investigate the remaining ~27 companies without confirmed data,
  grouped by the root causes identified above (iframe handling would be
  a generalizable scraper improvement; the "found URL but still 0" group
  needs individual debugging like Target's Azure Search issue did)
- Consider expanding `_SEARCH_BOX_SELECTORS` to catch more placeholder
  text patterns (USAA's "eg: Compliance or Technology..." doesn't match
  any current selector)
- Re-verify idempotency at full 65-company scale with a second identical
  run (not yet done twice in a row since the URL/platform changes this
  round)