import json
import os
from datetime import datetime

ALERT_FILE = "results/alerts/alert_history.json"


def save_alert(company, title, location, users):

    os.makedirs(
        "results/alerts",
        exist_ok=True
    )

    alert = {
        "timestamp": str(datetime.now()),
        "company": company,
        "title": title,
        "location": location,
        "matched_users": users
    }

    alerts = []

    if os.path.exists(ALERT_FILE):

        with open(ALERT_FILE, "r") as file:
            alerts = json.load(file)

    alerts.append(alert)

    with open(ALERT_FILE, "w") as file:
        json.dump(
            alerts,
            file,
            indent=4
        )