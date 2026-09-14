import pandas as pd


def find_matching_users(role_type):

    users = pd.read_csv(
        "data/users.csv"
    )

    matches = []

    for _, row in users.iterrows():

        interests = [
            interest.strip().lower()
            for interest in row["interests"].split(";")
        ]

        if role_type.lower() in interests:

            matches.append(
                row["name"]
            )

    return matches


if __name__ == "__main__":

    users = find_matching_users("SWE")

    print(users)