import sys
import os
import re
from datetime import date

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from role_classifier import classify_role
from url_utils import clean_url

_INTERN_WORD_RE = re.compile(
    r"\bintern(ship)?s?\b|\bco-?op\b", re.IGNORECASE
)


def _keyword_search_jobs(url, company_name):

    try:
        response = requests.get(
            url,
            params={"keywords": "intern", "page": 1, "limit": 100},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        response.raise_for_status()

        return response.json().get("jobs", [])

    except Exception as e:
        print(f"Error fetching jobs for {company_name}: {e}")
        return []


def get_jibe_internships(company_name, api_host):
    """
    Fetch internships from a company's Jibe / SAP SuccessFactors
    Recruiting Marketing career site (the "careers.<company>.com" /
    "jobs.<company>.com" sites backed by a public /api/jobs endpoint).

    Example:
        get_jibe_internships("Garmin", "careers.garmin.com")
        get_jibe_internships("State Farm", "jobs.statefarm.com")

    Unlike Greenhouse (title/metadata sniffing), this platform exposes a
    genuine "Intern" facet (tags3) we can filter on server-side, so
    identification is exact rather than heuristic.
    """

    url = f"https://{api_host}/api/jobs"

    params = {
        "page": 1,
        "sortBy": "relevance",
        "descending": "false",
        "internal": "false",
        "tags3": "Intern",
        "limit": 100,
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

    except Exception as e:
        print(
            f"Error fetching jobs for "
            f"{company_name}: {e}"
        )
        return []

    jobs = data.get("jobs", [])

    # Not every Jibe site uses the tags3 "Intern" facet (e.g. Johns
    # Hopkins APL doesn't) - when it matches nothing, fall back to a
    # keyword search filtered on the title instead.
    use_keyword_search = not jobs

    if use_keyword_search:
        jobs = _keyword_search_jobs(url, company_name)

    internships = []
    seen_job_ids = set()

    for job in jobs:

        fields = job.get("data", {}) or {}

        if use_keyword_search:

            if not _INTERN_WORD_RE.search(fields.get("title", "") or ""):
                continue

        elif "Intern" not in (fields.get("tags3") or []):
            continue

        title = fields.get("title", "") or ""

        job_id = fields.get("req_id") or fields.get("slug")

        if job_id is not None:

            if job_id in seen_job_ids:
                continue

            seen_job_ids.add(job_id)

        application_url = (
            fields.get("apply_url")
            or fields.get("canonical_url")
            or ""
        )

        internships.append({
            "company": company_name,
            "title": title,
            "location": fields.get("full_location", "Unknown"),
            "role_type": classify_role(title),
            "application_url": clean_url(application_url),
            "external_job_id": str(job_id) if job_id is not None else None,
            "source_platform": "jibe",
            "date_discovered": date.today().isoformat(),
        })

    return internships


if __name__ == "__main__":

    garmin_jobs = get_jibe_internships("Garmin", "careers.garmin.com")

    print(f"\n{len(garmin_jobs)} Garmin internships:\n")

    for job in garmin_jobs:
        print(job)

    statefarm_jobs = get_jibe_internships(
        "State Farm", "jobs.statefarm.com"
    )

    print(f"\n{len(statefarm_jobs)} State Farm internships:\n")

    for job in statefarm_jobs:
        print(job)
