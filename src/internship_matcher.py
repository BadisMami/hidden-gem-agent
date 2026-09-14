import pandas as pd


def find_internships(role):

    internships = pd.read_csv(
        "data/internships.csv"
    )

    matches = internships[
        internships["role_type"].str.lower()
        == role.lower()
    ]

    return matches


if __name__ == "__main__":

    role = input(
        "Enter role (SWE, ML, Embedded, Firmware): "
    )

    results = find_internships(role)

    print("\nMatching Internships:\n")

    print(results)