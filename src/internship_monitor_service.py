from company_registry_loader import (
    load_companies
)

from company_monitors.custom_monitor import (
    check_company
)


def run_monitor():

    companies = load_companies()

    print(
        f"Loaded {len(companies)} companies."
    )

    for company in companies:

        if "career_url" not in company:

            continue

        result = check_company(
            company
        )

        print(result)


if __name__ == "__main__":

    run_monitor()