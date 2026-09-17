from company_registry_loader import load_enabled_companies
from company_monitors.greenhouse_monitor import get_greenhouse_internships
from database_setup import create_database
from database_monitor import upsert_internship, create_alert_for_new_internship

# Platforms with a normalized adapter that returns internship dicts ready
# for direct SQLite insertion. Other platforms (e.g. "custom") are listed
# in the registry for future company-page monitoring, but custom_monitor
# only returns raw scraped links today, not structured internship
# records - so those companies are reported as skipped rather than
# silently miscounted as failures or successes.
PLATFORM_ADAPTERS = {
    "greenhouse": lambda company: get_greenhouse_internships(
        company["company"],
        company["platform_identifier"]
    ),
}


def run_monitor():

    create_database()

    companies = load_enabled_companies()

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
    }

    for company in companies:

        name = company.get("company", "Unknown")
        platform = company.get("platform", "")

        adapter = PLATFORM_ADAPTERS.get(platform)

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

            else:

                summary["existing_internships_skipped"] += 1

    print_summary(summary)

    return summary


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


if __name__ == "__main__":

    run_monitor()
