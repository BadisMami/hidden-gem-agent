import argparse

from company_registry_loader import load_enabled_companies
from company_monitors.greenhouse_monitor import get_greenhouse_internships
from company_monitors.jibe_monitor import get_jibe_internships
from company_monitors.eightfold_monitor import get_eightfold_internships
from company_monitors.oracle_orc_monitor import get_oracle_orc_internships
from company_monitors.generic_browser_monitor import get_browser_scraped_internships
from database_setup import create_database
from database_monitor import upsert_internship, create_alert_for_new_internship
from sms_alerts import send_sms_alert


def _eightfold_adapter(company):

    api_host, company_domain = company["platform_identifier"].split("|")

    return get_eightfold_internships(
        company["company"], api_host, company_domain
    )


def _oracle_orc_adapter(company):

    career_site_host, tenant_host, site_number, site_name = (
        company["platform_identifier"].split("|")
    )

    return get_oracle_orc_internships(
        company["company"],
        career_site_host,
        tenant_host,
        site_number,
        site_name
    )


def _make_custom_adapter(browser):
    """
    "custom" platform companies have no known structured API. Falls back
    to a real (shared, headless) browser scraping career_url directly -
    best-effort, since these sites vary wildly and some actively resist
    automated browsing. Companies with a verified platform (greenhouse,
    jibe, eightfold, oracle_orc) always use their dedicated adapter
    instead, since it's far more accurate.
    """

    def adapter(company):

        return get_browser_scraped_internships(
            company["company"],
            company["career_url"],
            browser=browser
        )

    return adapter


# Platforms with a normalized adapter that returns internship dicts ready
# for direct SQLite insertion. "custom" uses a generic browser-based
# fallback (see _make_custom_adapter) rather than a per-platform API,
# since most of those companies' actual ATS hasn't been individually
# verified yet.
def _build_platform_adapters(browser):

    return {
        "greenhouse": lambda company: get_greenhouse_internships(
            company["company"],
            company["platform_identifier"]
        ),
        "jibe": lambda company: get_jibe_internships(
            company["company"],
            company["platform_identifier"]
        ),
        "eightfold": _eightfold_adapter,
        "oracle_orc": _oracle_orc_adapter,
        "custom": _make_custom_adapter(browser),
    }


def run_monitor(skip_custom=False):
    """
    skip_custom=True skips platform="custom" companies entirely (the ones
    needing the slow headless-browser scraper), without even importing
    Playwright. Intended for a frequent, lightweight scheduled run (e.g.
    every 15 minutes) that only re-checks the fast, structured-API
    companies (greenhouse/jibe/eightfold/oracle_orc) - pair with a
    separate, much less frequent full run (skip_custom=False) that also
    covers the "custom" companies, since scraping ~60 sites with a real
    browser takes minutes, not seconds, and doesn't need to happen nearly
    as often to still catch new postings.
    """

    create_database()

    companies = load_enabled_companies()

    if skip_custom:
        companies = [c for c in companies if c.get("platform") != "custom"]

    summary = {
        "companies_checked": len(companies),
        "companies_successful": 0,
        "companies_failed": 0,
        "companies_skipped": 0,
        "jobs_retrieved": 0,
        "internships_matched": 0,
        "new_internships_inserted": 0,
        "existing_internships_skipped": 0,
        "alerts_created": 0,
        "sms_sent": 0,
    }

    needs_browser = any(
        c.get("platform") == "custom" for c in companies
    )

    if needs_browser:

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True, args=["--disable-http2"]
            )

            try:
                _run_all_companies(
                    companies, _build_platform_adapters(browser), summary
                )
            finally:
                browser.close()

    else:

        _run_all_companies(
            companies, _build_platform_adapters(None), summary
        )

    print_summary(summary)

    return summary


def _run_all_companies(companies, adapters, summary):

    for company in companies:

        name = company.get("company", "Unknown")
        platform = company.get("platform", "")

        adapter = adapters.get(platform)

        if adapter is None:

            print(f"[SKIP] {name}: no adapter for platform '{platform}'")

            summary["companies_skipped"] += 1

            continue

        try:

            internships = adapter(company)

        except Exception as e:

            print(f"[FAIL] {name}: {e}")

            summary["companies_failed"] += 1

            continue

        summary["companies_successful"] += 1
        summary["jobs_retrieved"] += len(internships)
        summary["internships_matched"] += len(internships)

        for internship in internships:

            result = upsert_internship(
                company=internship["company"],
                title=internship["title"],
                location=internship.get("location", ""),
                role_type=internship.get("role_type", "Other"),
                application_url=internship.get("application_url", ""),
                source_platform=internship.get("source_platform", platform),
                external_job_id=internship.get("external_job_id"),
            )

            if result["is_new"]:

                summary["new_internships_inserted"] += 1

                alert = create_alert_for_new_internship(
                    internship["company"],
                    internship["title"],
                    internship.get("location", ""),
                    internship.get("role_type", "Other"),
                )

                if alert:

                    summary["alerts_created"] += 1

                    sms_body = (
                        f"New internship: {internship['company']} - "
                        f"{internship['title']} "
                        f"({internship.get('location', 'Unknown')})\n"
                        f"{internship.get('application_url', '')}"
                    )

                    if send_sms_alert(sms_body):
                        summary["sms_sent"] += 1

            else:

                summary["existing_internships_skipped"] += 1


def print_summary(summary):

    print("\n===== Monitor Run Summary =====\n")

    print(f"Companies checked: {summary['companies_checked']}")
    print(f"Companies successful: {summary['companies_successful']}")
    print(f"Companies failed: {summary['companies_failed']}")
    print(f"Companies skipped (no adapter): {summary['companies_skipped']}")
    print(f"Jobs retrieved: {summary['jobs_retrieved']}")
    print(f"Internships matched: {summary['internships_matched']}")
    print(f"New internships inserted: {summary['new_internships_inserted']}")
    print(
        f"Existing internships skipped: "
        f"{summary['existing_internships_skipped']}"
    )
    print(f"Alerts created: {summary['alerts_created']}")
    print(f"SMS sent: {summary['sms_sent']}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fast",
        action="store_true",
        help=(
            "Skip platform=custom companies (the slow, headless-browser "
            "ones). Only checks companies with a verified structured API "
            "(greenhouse/jibe/eightfold/oracle_orc). Fast enough to run "
            "every few minutes; doesn't require Playwright/Chromium."
        ),
    )
    args = parser.parse_args()

    run_monitor(skip_custom=args.fast)
