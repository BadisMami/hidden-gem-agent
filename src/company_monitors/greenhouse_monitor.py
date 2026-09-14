import requests
import pandas as pd


def get_greenhouse_internships(company_name, board_name):
    """
    Fetch internships from a Greenhouse job board.

    Example:
        get_greenhouse_internships("Hudl", "hudl")
        get_greenhouse_internships("Databricks", "databricks")
    """

    url = f"https://boards-api.greenhouse.io/v1/boards/{board_name}/jobs"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        jobs = data.get("jobs", [])

        internships = []

        for job in jobs:
            title = job.get("title", "")

            if "intern" in title.lower():

                internships.append({
                    "company": company_name,
                    "title": title,
                    "location": job.get("location", {}).get(
                        "name",
                        "Unknown"
                    ),
                    "role_type": "SWE",
                    "application_url": job.get(
                        "absolute_url",
                        ""
                    )
                })

        return internships

    except Exception as e:
        print(
            f"Error fetching jobs for "
            f"{company_name}: {e}"
        )
        return []


def save_internships(
    internships,
    output_file="data/internships.csv"
):
    """
    Append internships to the master database.
    """

    if not internships:
        print("No internships found.")
        return

    new_df = pd.DataFrame(internships)

    try:
        existing_df = pd.read_csv(output_file)

        combined_df = pd.concat(
            [existing_df, new_df],
            ignore_index=True
        )

        combined_df = (
            combined_df
            .drop_duplicates(
                subset=[
                    "company",
                    "title",
                    "location"
                ]
            )
        )

        combined_df.to_csv(
            output_file,
            index=False
        )

    except FileNotFoundError:
        new_df.to_csv(
            output_file,
            index=False
        )

    print(
        f"Added {len(internships)} "
        f"internships to {output_file}"
    )


if __name__ == "__main__":

    hudl_jobs = get_greenhouse_internships(
        "Hudl",
        "hudl"
    )

    print("\nHudl Internships:\n")

    for job in hudl_jobs:
        print(job)

    save_internships(hudl_jobs)