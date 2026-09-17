# In-progress: expanding company coverage beyond Hudl

Status as of 2026-09-17, stopped mid-session because the user had to step
away. Everything committed at this point is stable and tested - nothing
is left half-edited. This file describes what's done, what's built but
not wired in yet, and what was actively being investigated when work
stopped.

## What's live and working (wired into the registry + monitor service)

Run `python src/internship_monitor_service.py` to pull all of these:

- **Hudl** - Greenhouse (`company_monitors/greenhouse_monitor.py`)
- **Garmin**, **State Farm** - Jibe/SAP SuccessFactors
  (`company_monitors/jibe_monitor.py`)

## What's built and verified live, but NOT yet wired into the registry/service

These two adapter modules exist, were tested against real live data today,
and work correctly - but `data/company_registry.csv` and
`internship_monitor_service.py`'s `PLATFORM_ADAPTERS` dict have **not**
been updated to use them yet. That's the next step, not a bug.

- **`src/company_monitors/eightfold_monitor.py`** -
  `get_eightfold_internships(company_name, api_host, company_domain)`.
  Verified live against John Deere (`careers.deere.com`, domain
  `johndeere.com`) - returned 13 real internships. Run it directly:
  `python src/company_monitors/eightfold_monitor.py`

- **`src/company_monitors/oracle_orc_monitor.py`** -
  `get_oracle_orc_internships(company_name, career_site_host, tenant_host, site_number, site_name)`.
  Verified live against Honeywell (`careers.honeywell.com`, tenant
  `ibqbjb.fa.ocs.oraclecloud.com`, site number `CX_1`, site name
  `Honeywell`) - returned 30 real internships with correct role
  classification (SWE, ML, Embedded, Hardware, Data). Run it directly:
  `python src/company_monitors/oracle_orc_monitor.py`

**To finish wiring these in:**
1. Add rows/columns to `data/company_registry.csv` for John Deere
   (`platform=eightfold`) and Honeywell (`platform=oracle_orc`). The
   existing `platform_identifier` column only holds one value per row;
   Eightfold needs `api_host` + `company_domain`, and Oracle ORC needs
   `career_site_host` + `tenant_host` + `site_number` + `site_name` - either
   extend the registry schema with more columns, or encode multiple values
   in `platform_identifier` with a delimiter (e.g. `:`) and parse it in
   `internship_monitor_service.py`, consistent with how the existing
   `greenhouse`/`jibe` adapters are dispatched.
2. Add `"eightfold": lambda company: get_eightfold_internships(...)` and
   `"oracle_orc": lambda company: get_oracle_orc_internships(...)` to
   `PLATFORM_ADAPTERS` in `internship_monitor_service.py`.
3. Run `python src/internship_monitor_service.py` twice in a row to
   confirm idempotency (0 new internships / 0 new alerts on the second
   run), same as was done for Hudl/Garmin/State Farm.
4. Add mocked pytest coverage for both adapters (`tests/test_eightfold_monitor.py`,
   `tests/test_oracle_orc_monitor.py`), following the pattern in
   `tests/test_jibe_monitor.py`.
5. Update `README.md`'s "Supported platforms" section and `LAB_NOTEBOOK.md`.

## Also fixed today (already committed, already tested)

Both `greenhouse_monitor.py` and the new `eightfold_monitor.py`/
`oracle_orc_monitor.py` now use a word-boundary regex (`\bintern(ship)?s?\b`)
instead of a naive `"intern" in title.lower()` substring check. The naive
check would falsely match titles like "**Intern**al Auditor" or
"**Intern**ational Sales Manager". Caught this while testing Honeywell's
Oracle ORC data, which has real "Internal Auditor" postings that would
otherwise have been inserted as fake internships. A regression test for
this is in `tests/test_greenhouse_monitor.py::test_internal_role_not_mistaken_for_internship`.

## Companies investigated today - platform found but adapter not built

Each of these runs a real, identifiable platform, but building a working
public adapter needs more time than was available this session:

- **RTX, Caterpillar, Fidelity, UPS** - all run **Phenom People**
  (`cdn.phenompeople.com`, `/phb/` paths). The career-site domain itself
  (e.g. `careers.rtx.com/widgets`) is a POST-only endpoint whose body
  couldn't be captured with the available tools. **Breakthrough right
  before stopping**: the real Phenom data API lives on a *different*
  host entirely - `https://content-ir.phenompeople.com/api/{TENANT_CODE}/...`
  (GET requests, e.g. `.../api/UPBUPSGLOBAL/globalSearchConfig?...`).
  Tenant codes seen so far: UPS = `UPBUPSGLOBAL`. This is a real, promising
  lead - the next step is finding the actual job-search `ddoKey` (only
  `getRegionLocales`, `globalSearchConfig`, `categoryMasterDataV2`, and
  `getPiiConsentConfig` were observed; the jobs-list one wasn't reached
  before stopping) and testing it the same way the Eightfold/Oracle ORC
  patterns were cracked.
- **Target** - custom Angular app with `/api/jobsearch` (POST, JSON body).
  Confirmed the endpoint works and returns rich data including a real
  `internshiptype` field, but the exact filter field name in the POST body
  couldn't be determined (many guesses tried: `jobAreas`, `jobareas`,
  `profiles`, `filter`, `$filter`, `internshiptype`, `keyword(s)`,
  `searchText`, `q` - none filtered server-side). Fetching everything
  unfiltered isn't practical (12,462 total jobs, 15/page, no larger
  page-size param found).
- **Progressive** - Talemetry platform. Browser-automation search
  interactions didn't reliably trigger a navigable results page (same
  issue as Cummins and Capital One below), so the actual API call was
  never captured.
- **Cummins** (`cummins.jobs`, custom Nuxt.js app) and **Capital One**
  (`www.capitalonecareers.com`, TalentBrew front-end) - same interaction
  issue as Progressive.

## Companies not checked at all yet

3M (`careers.3m.com` didn't load - possibly geo/network-blocked), Delta
(`careers.delta.com` also didn't load), Lockheed Martin (front-end is a
lockheedmartin.com marketing page; the real job-search app wasn't found
before stopping), L3Harris, Raymond James, Publix, Best Buy, Nike,
Chipotle, Strava.

## Recommended next session approach

1. Wire in Eightfold + Oracle ORC (concrete, already-verified work -
   do this first).
2. Chase the Phenom `content-ir.phenompeople.com/api/{TENANT}/` lead -
   if the jobs-search `ddoKey` is found, it unlocks 4 companies at once
   (RTX, Caterpillar, Fidelity, UPS) rather than needing separate
   investigation for each.
3. For companies where browser-automation clicks aren't reliably
   triggering search (Progressive, Cummins, Capital One), try
   constructing the results URL directly by guessing common query-param
   patterns (`?q=`, `?keywords=`, `?k=`) rather than relying on clicking
   the UI - Target's URL pattern was found this way.
4. Skip Target's exact filter param unless a way to inspect the live
   POST body becomes available (e.g. a proxy or a different browser
   tool) - guessing further isn't a good use of time.
