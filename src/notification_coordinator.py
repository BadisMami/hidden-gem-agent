import pandas as pd
import os

from alert_history import save_alert
from alert_engine import create_alert
from user_matcher import find_matching_users


CURRENT_FILE = "data/internships.csv"

SNAPSHOT_FILE = (
    "results/monitoring/snapshots/"
    "previous_internships.csv"
)


def detect_new_internships():

    current = pd.read_csv(CURRENT_FILE)

    if not os.path.exists(
        SNAPSHOT_FILE
    ):

        current.to_csv(
            SNAPSHOT_FILE,
            index=False
        )

        print(
            "Initial snapshot created."
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

    new_titles = (
        current_titles
        - previous_titles
    )

    if len(new_titles) == 0:

        print(
            "No new internships."
        )

    else:

        print(
            "\nAlerts Generated:\n"
        )

        for internship in new_titles:

            row = current[
                current["title"]
                == internship
            ].iloc[0]

            alert = create_alert(
                row["company"],
                row["title"],
                row["location"]
            )

            print(alert)

            matched_users = (
                find_matching_users(
                    row["role_type"]
                )
            )

            print(
                "Matched Users:"
            )

            for user in matched_users:
                print(f"- {user}")

            print()

    current.to_csv(
        SNAPSHOT_FILE,
        index=False
    )


if __name__ == "__main__":
    detect_new_internships()