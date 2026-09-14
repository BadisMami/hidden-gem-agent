import pandas as pd


def load_companies():
    return pd.read_csv("data/companies.csv")


def get_company(company_name):

    companies = load_companies()

    result = companies[
        companies["company"].str.lower()
        == company_name.lower()
    ]

    return result


def filter_by_industry(industry):

    companies = load_companies()

    result = companies[
        companies["industry"].str.lower()
        == industry.lower()
    ]

    return result


def filter_by_role(role):

    companies = load_companies()

    role = role.lower()

    if role not in companies.columns:
        return pd.DataFrame()

    result = companies[
        companies[role] == "Yes"
    ]

    return result


if __name__ == "__main__":

    companies = load_companies()

    print(companies)
