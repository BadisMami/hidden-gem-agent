from company_database import load_companies
from datetime import datetime


LOG_FILE = (
    "results/monitoring/monitor_log.txt"
)


def log_message(message):

    timestamp = datetime.now()

    with open(LOG_FILE, "a") as file:

        file.write(
            f"[{timestamp}] {message}\n"
        )


def monitor_companies():

    companies = load_companies()

    print("\n===== Company Monitoring =====\n")

    for _, row in companies.iterrows():

        message = (
            f"Checking company: "
            f"{row['company']}"
        )

        print(message)

        log_message(message)


if __name__ == "__main__":
    monitor_companies()