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


if __name__ == "__main__":

    companies = load_companies()

    print(
        f"Loaded {len(companies)} companies."
    )

    for company in companies[:5]:

        print(company)