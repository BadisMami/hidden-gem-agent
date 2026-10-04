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


def get_workday_internships(company_name, host, tenant, site, max_pages=10):
    """
    Fetch internships from a Workday career site ("<tenant>.wd<N>.
    myworkdayjobs.com/<site>") through the public CXS search endpoint the
    site's own JavaScript calls.

    Example:
        get_workday_internships(
            "Leidos", "leidos.wd5.myworkdayjobs.com", "leidos", "External"
        )

    Workday's search is relevance-ranked and fuzzy ("intern" also pulls
    in "International ..." roles), so actual internships come first and
    titles are re-filtered with a word-boundary regex. Paging stops at
    the first page with no internship titles at all, since everything
    after it is just weaker keyword matches.
    """

    url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"

    page_size = 20  # Workday rejects anything larger

    internships = []
    seen_paths = set()

    for page in range(max_pages):

        try:
            response = requests.post(
                url,
                json={
                    "appliedFacets": {},
                    "limit": page_size,
                    "offset": page * page_size,
                    "searchText": "intern",
                },
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            response.raise_for_status()

            postings = response.json().get("jobPostings") or []

        except Exception as e:
            print(f"Error fetching jobs for {company_name}: {e}")
            break

        page_matches = 0

        for posting in postings:

            title = posting.get("title", "") or ""

            if not _INTERN_WORD_RE.search(title):
                continue

            page_matches += 1

            path = posting.get("externalPath", "") or ""

            if path in seen_paths:
                continue

            seen_paths.add(path)

            bullets = posting.get("bulletFields") or []

            internships.append({
                "company": company_name,
                "title": title,
                "location": posting.get("locationsText") or "Unknown",
                "role_type": classify_role(title),
                "application_url": clean_url(
                    f"https://{host}/en-US/{site}{path}"
                ),
                # bulletFields[0] is the requisition id on every tenant
                # checked; fall back to the URL path, which is also unique.
                "external_job_id": bullets[0] if bullets else path,
                "source_platform": "workday",
                "date_discovered": date.today().isoformat(),
            })

        if len(postings) < page_size or page_matches == 0:
            break

    return internships


if __name__ == "__main__":

    jobs = get_workday_internships(
        "Leidos", "leidos.wd5.myworkdayjobs.com", "leidos", "External"
    )

    print(f"\n{len(jobs)} Leidos internships:\n")

    for job in jobs:
        print(job)
