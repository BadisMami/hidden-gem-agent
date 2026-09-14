import pandas as pd


def load_companies():
    return pd.read_csv("data/companies.csv")


def find_companies(role):

    companies = load_companies()

    role = role.lower()

    column_map = {
        "swe": "swe",
        "software engineering": "swe",
        "ml": "ml",
        "machine learning": "ml",
        "data": "data",
        "embedded": "embedded",
        "embedded systems": "embedded",
        "firmware": "firmware",
        "robotics": "robotics",
        "cybersecurity": "cybersecurity"
    }

    if role not in column_map:
        return []

    column = column_map[role]

    matches = companies[
        companies[column] == "Yes"
    ]

    return matches["company"].tolist()


if __name__ == "__main__":

    role = input(
        "Enter a role (SWE, ML, Embedded, Firmware, Robotics): "
    )

    matches = find_companies(role)

    print("\nRecommended Companies:\n")

    for company in matches:
        print("-", company)