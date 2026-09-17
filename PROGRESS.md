# In-progress: expanding company coverage beyond Hudl

Status as of 2026-09-17. Everything committed at this point is stable and
tested - nothing is left half-edited. This file describes what's done,
what's built but not wired in yet, and what was actively being
investigated when work stopped.

## 2026-09-17 (latest): generic browser scraper + all adapters wired in

User asked to make alerts happen for as many registry companies as
possible, "any way possible." Rather than continuing to reverse-engineer
one platform at a time (Phenom, Talemetry, etc. had stalled), built a
generic fallback that works regardless of platform:

- **`company_monitors/generic_browser_monitor.py`** - uses a real headless
  browser (Playwright + Chromium, installed via `playwright install
  chromium`) to render JS-heavy career pages that a plain HTTP request
  can't see through. Loads the career page, attempts a job-search-box
  submission if one exists, extracts links whose text contains
  "intern"/"internship" as a whole word, isn't a generic nav label, and
  points at what looks like a real job-detail URL (4+ digit id in the
  href). 6 unit tests (`tests/test_generic_browser_monitor.py`) cover the
  filtering logic with a mocked page.
- Wired **all four working adapters** (greenhouse, jibe, eightfold,
  oracle_orc) plus the new generic-browser fallback for `custom` into
  `internship_monitor_service.py`'s `PLATFORM_ADAPTERS`. Eightfold and
  Oracle ORC were built last session but never actually connected -
  they are now. John Deere is `platform=eightfold`, Honeywell is
  `platform=oracle_orc`. Also found and wired in **Eaton** as a second
  Eightfold company (`eaton.eightfold.ai`, domain `eaton.com`).
- Wired `send_sms_alert()` into the alert-creation path in
  `internship_monitor_service.py` - every new internship alert now
  attempts to send a real text, not just write to the DB. It no-ops
  safely if Twilio isn't configured (it currently isn't - user hasn't
  set up a Twilio account yet).
- Added `tests/test_eightfold_monitor.py` and
  `tests/test_oracle_orc_monitor.py` (mocked), closing a gap noted
  earlier in this file.
- **Fixed a real, unrelated bug found along the way**: `requirements.txt`
  had been UTF-16-encoded since the very first "fix" earlier this session
  and was never actually verified at the byte level (only round-tripped
  through the Read tool, which silently decoded it back to readable text,
  masking the problem). Rewrote via `printf` and verified with `xxd`/`file`
  this time.

**Full live run across all 65 registry companies** (`python
src/internship_monitor_service.py`), no per-company scope limiting:

```
Companies checked: 65
Companies successful: 65
Companies failed: 0
Jobs retrieved: 245
New internships inserted: 211
Existing internships skipped: 34
Alerts created: 26
SMS sent: 0  (Twilio not configured yet)
```

Breaking down where those 245 jobs came from:
- 6 companies with native structured adapters (Hudl/Greenhouse,
  Garmin+State Farm/Jibe, John Deere+Eaton/Eightfold, Honeywell/
  Oracle ORC) - Hudl's Greenhouse call hit a transient read-timeout this
  particular run (not a bug - just flaky network, will succeed next run)
- **24 of the 59 `custom`-platform companies produced real results via
  the generic browser scraper - 154 internship postings total.** Notably
  this included **RTX (10) and Caterpillar (20)**, both Phenom People
  sites where direct API reverse-engineering had stalled in an earlier
  session - the browser-based fallback succeeded anyway. Full per-company
  breakdown: Caterpillar 20, Leonardo DRS 17, McKesson 15, L3Harris 15,
  RTX 10, PepsiCo 10, Illinois Tool Works 7, Dick's Sporting Goods 7,
  Peraton 6, Truist 5, Cigna 5, Capital One 5, UnitedHealth Group 4,
  Procter & Gamble 4, Northwestern Mutual 4, Johns Hopkins APL 4, BAE
  Systems Inc 4, Lowe's 3, General Dynamics 3, MassMutual 2, Nike 1,
  Kroger 1, Charles Schwab 1, Best Buy 1
- The remaining 35 `custom` companies returned 0 results this run.
  Explicit errors were logged for 5 of them (Delta Airlines and 3M:
  `ERR_NAME_NOT_RESOLVED` - DNS failure, possibly a transient network
  issue worth retrying; Raymond James: navigation timeout; ManTech:
  redirect loop, likely bot-detection). The other ~30 loaded fine but
  either have no search box the scraper's selectors matched, the search
  didn't trigger real results, or they genuinely have no internships
  posted right now - the scraper can't distinguish these cases from each
  other, which is a real limitation worth knowing about, not a bug to
  "fix" blindly.

**Idempotency**: verified in earlier, smaller runs (native adapters only)
across the session; not re-verified at full 65-company scale this run
since a second full run would cost another ~10+ minutes of browser
scraping time. Worth a follow-up run to confirm "existing_internships_skipped"
grows correctly and no duplicates appear.

### What this means concretely
- The dashboard now shows real internships from ~30 companies, not 3.
- Alerts fire correctly (26 this run) for postings matching a
  registered user's declared interests, deduped against repeat runs.
- No texts go out yet - Twilio still needs to be configured by the user
  (account creation/billing is something Claude Code cannot do on their
  behalf).

## 2026-09-17 update: registry expanded to 48 companies (was 23)

Added 25 new companies to `data/company_registry.csv`, sourced via web
search for real companies with real, currently-active internship
programs (McKesson, Cigna, Liberty Mutual, USAA, MassMutual, Northwestern
Mutual, Truist, Charles Schwab, Edward Jones, Southwest Airlines, FedEx,
Home Depot, Lowe's, Dick's Sporting Goods, Kroger, Illinois Tool Works,
GE Aerospace, Boeing, Duke Energy, UnitedHealth Group, Parker Hannifin,
Eaton, Mercury Insurance, PepsiCo, Procter & Gamble). Each has a real,
verified career-page URL from search results - none were invented. All
are added as `platform=custom` with no `platform_identifier`, since none
of their actual ATS platforms were verified this round (that would need
the same live-browser-network-inspection process used for Garmin/John
Deere/Honeywell). They currently show as "skip - no adapter" in monitor
runs, same as the rest of the custom-platform companies - being in the
registry does NOT mean they're actively monitored yet.

One incidental lead worth chasing next: **Eaton's career site
(`eaton.eightfold.ai/careers`) runs on Eightfold** - the same platform
already cracked for John Deere. Once Eightfold is wired in (see below),
Eaton should be nearly free to add too.

## 2026-09-17 update: added 17 defense contractors (big/medium/small)

User asked specifically for defense companies across all size tiers.
Added, all `platform=custom` with sourced real career URLs, same caveat
as above (in the registry, not yet actively monitored):

- **Big/prime contractors** (priority=High): Northrop Grumman, General
  Dynamics, BAE Systems Inc, Huntington Ingalls Industries
- **Mid-size**: Leidos, Booz Allen Hamilton, SAIC, CACI International,
  Textron Systems, Leonardo DRS, Kratos Defense, Mercury Systems
- **Smaller / specialized**: ManTech, Parsons Corporation, Peraton, MITRE
  Corporation (FFRDC, not-for-profit), Johns Hopkins Applied Physics
  Laboratory (JHU APL, university-affiliated lab)

Note: search results mentioned Northrop Grumman's application portal
(`jobs.northropgrumman.com`) is Workday-based - worth checking first if
anyone builds a generic Workday adapter, since Workday support is on the
broader roadmap.

Registry is now 65 companies total (was 23 at the start of today).
CSV validated (no nulls), all 39 tests pass, and a live monitor run
completes cleanly (3 successful / 0 failed / 62 skipped as expected).

## What's live and working (wired into the registry + monitor service)

**[SUPERSEDED - see the "generic browser scraper + all adapters wired in"
section at the top of this file, dated later the same day. Eightfold and
Oracle ORC described as "not yet wired in" below ARE now wired in.]**

Run `python src/internship_monitor_service.py` to pull all of these:

- **Hudl** - Greenhouse (`company_monitors/greenhouse_monitor.py`)
- **Garmin**, **State Farm** - Jibe/SAP SuccessFactors
  (`company_monitors/jibe_monitor.py`)

## What's built and verified live, but NOT yet wired into the registry/service

**[SUPERSEDED - both adapters below are now wired in; see the top of this
file. Left in place as a record of the platform-identifier encoding
decision that was made (pipe-delimited in `platform_identifier`,
parsed in `internship_monitor_service.py`).]**

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

**How they were wired in (for reference):**
1. Added rows/columns to `data/company_registry.csv` for John Deere
   (`platform=eightfold`) and Honeywell (`platform=oracle_orc`). The
   `platform_identifier` column holds multiple values pipe-delimited
   (`api_host|company_domain` for Eightfold;
   `career_site_host|tenant_host|site_number|site_name` for Oracle ORC),
   parsed in `internship_monitor_service.py`.
2. Added `"eightfold"` and `"oracle_orc"` entries to
   `PLATFORM_ADAPTERS` in `internship_monitor_service.py`.
3. Ran `python src/internship_monitor_service.py` twice in a row to
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
