import requests

url = "https://boards-api.greenhouse.io/v1/boards/hudl/jobs"

data = requests.get(url).json()

for job in data["jobs"]:
    if "Intern" in job["title"]:
        print("=" * 50)
        print("TITLE:", job["title"])
        print("LOCATION:", job["location"]["name"])

        for item in job.get("metadata", []):
            print(item["name"], "=", item["value"])