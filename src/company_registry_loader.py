import pandas as pd


COMPANY_REGISTRY_PATH = (
    "data/company_registry.csv"
)


def load_companies():

    df = pd.read_csv(
        COMPANY_REGISTRY_PATH
    )

    companies = (
        df.to_dict(
            orient="records"
        )
    )

    return companies


def load_enabled_companies():
    """
    Return only companies marked enabled=yes in the registry, with
    platform/platform_identifier normalized for adapter dispatch.
    """

    companies = load_companies()

    enabled = []

    for company in companies:

        flag = str(company.get("enabled", "")).strip().lower()

        if flag != "yes":
            continue

        company["platform"] = str(
            company.get("platform", "") or ""
        ).strip().lower()

        enabled.append(company)

    return enabled


if __name__ == "__main__":

    companies = load_companies()

    print(
        f"Loaded {len(companies)} companies."
    )

    for company in companies[:5]:

        print(company)