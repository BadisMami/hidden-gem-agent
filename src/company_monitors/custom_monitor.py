import requests
from bs4 import BeautifulSoup


def extract_links(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = []

    for link in soup.find_all("a"):

        text = link.get_text(
            strip=True
        )

        href = link.get(
            "href"
        )

        if text and href:

            links.append({
                "text": text,
                "href": href
            })

    return links


def check_company(company):

    try:

        response = requests.get(
            company["career_url"],
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        links = extract_links(
            response.text
        )

        internship_links = []

        good_keywords = [
            "intern",
            "internship",
            "software engineering intern",
            "machine learning intern",
            "data science intern",
            "data engineering intern",
            "embedded",
            "firmware",
            "student"
        ]

        bad_keywords = [
            "product",
            "sports",
            "football",
            "basketball",
            "baseball",
            "volleyball",
            "pricing",
            "customer",
            "demo",
            "features"
        ]

        for link in links:

            text = link["text"].lower()

            skip = False

            for bad_word in bad_keywords:

                if bad_word in text:

                    skip = True
                    break

            if skip:
                continue

            for good_word in good_keywords:

                if good_word in text:

                    internship_links.append(
                        link
                    )

                    break

        return {
            "company": company["company"],
            "status": response.status_code,
            "jobs": internship_links[:20]
        }

    except Exception as e:

        return {
            "company": company["company"],
            "status": "ERROR",
            "error": str(e)
        }


if __name__ == "__main__":

    test_company = {
        "company": "Hudl",
        "career_url": "https://www.hudl.com/jobs/interns"
    }

    result = check_company(
        test_company
    )

    print("\nRESULT:\n")

    for key, value in result.items():

        print(f"{key}: {value}")