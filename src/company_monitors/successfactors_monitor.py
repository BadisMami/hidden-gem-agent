import sys
import os
import re
import html
from datetime import date

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from role_classifier import classify_role
from url_utils import clean_url

_INTERN_WORD_RE = re.compile(
    r"\bintern(ship)?s?\b|\bco-?op\b", re.IGNORECASE
)

# One search-result row. Each row renders its title link twice (desktop
# and mobile layouts), hence the dedup on href below.
_ROW_RE = re.compile(
    r'<tr class="data-row".*?</tr>', re.IGNORECASE | re.DOTALL
)
_TITLE_LINK_RE = re.compile(
    r'<a href="(/job/[^"]+)" class="jobTitle-link"[^>]*>([^<]+)</a>',
    re.IGNORECASE
)
_LOCATION_RE = re.compile(
    r'<span class="jobLocation">\s*([^<]+?)\s*</span>', re.IGNORECASE
)
_JOB_ID_RE = re.compile(r"/(\d+)/?$")


def get_successfactors_internships(company_name, host, max_pages=8):
    """
    Fetch internships from a SAP SuccessFactors "Career Site Builder"
    site (the ones with /search/?q=... and /job/<slug>/<id>/ URLs), by
    reading its server-rendered search results page.

    Example:
        get_successfactors_internships(
            "Huntington Ingalls Industries", "careers.huntingtoningalls.com"
        )
    """

    page_size = 25  # fixed by the site

    internships = []
    seen_hrefs = set()

    for page in range(max_pages):

        try:
            response = requests.get(
                f"https://{host}/search/",
                params={"q": "intern", "startrow": page * page_size},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            response.raise_for_status()

        except Exception as e:
            print(f"Error fetching jobs for {company_name}: {e}")
            break

        rows = _ROW_RE.findall(response.text)

        for row in rows:

            link = _TITLE_LINK_RE.search(row)

            if not link:
                continue

            href, title = link.group(1), html.unescape(link.group(2)).strip()

            if href in seen_hrefs or not _INTERN_WORD_RE.search(title):
                continue

            seen_hrefs.add(href)

            location = _LOCATION_RE.search(row)
            job_id = _JOB_ID_RE.search(href)

            internships.append({
                "company": company_name,
                "title": title,
                "location": (
                    html.unescape(location.group(1)) if location
                    else "Unknown"
                ),
                "role_type": classify_role(title),
                "application_url": clean_url(f"https://{host}{href}"),
                "external_job_id": job_id.group(1) if job_id else href,
                "source_platform": "successfactors",
                "date_discovered": date.today().isoformat(),
            })

        if len(rows) < page_size:
            break

    return internships


if __name__ == "__main__":

    jobs = get_successfactors_internships(
        "Huntington Ingalls Industries", "careers.huntingtoningalls.com"
    )

    print(f"\n{len(jobs)} HII internships:\n")

    for job in jobs:
        print(job)
