import pandas as pd


def load_internships():
    internships = pd.read_csv(
        "data/internships.csv"
    )

    return internships


if __name__ == "__main__":

    internships = load_internships()

    print("\nInternships:\n")

    print(internships)