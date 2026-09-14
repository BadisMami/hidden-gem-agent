import pandas as pd
import os


CURRENT_FILE = "data/internships.csv"

SNAPSHOT_FILE = (
    "results/monitoring/snapshots/"
    "previous_internships.csv"
)


def compare_internships():

    current = pd.read_csv(CURRENT_FILE)

    if not os.path.exists(SNAPSHOT_FILE):

        current.to_csv(
            SNAPSHOT_FILE,
            index=False
        )

        print(
            "First snapshot created."
        )

        return

    previous = pd.read_csv(
        SNAPSHOT_FILE
    )

    current_titles = set(
        current["title"]
    )

    previous_titles = set(
        previous["title"]
    )

    new_internships = (
        current_titles
        - previous_titles
    )

    if len(new_internships) == 0:

        print(
            "No new internships detected."
        )

    else:

        print(
            "\nNew Internships Found:\n"
        )

        for internship in new_internships:

            print("-", internship)

    current.to_csv(
        SNAPSHOT_FILE,
        index=False
    )


if __name__ == "__main__":
    compare_internships()