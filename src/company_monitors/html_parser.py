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


if __name__ == "__main__":

    html = """
    /careers
        Software Engineering Intern
    </a>

    /jobs
        Machine Learning Intern
    </a>
    """

    print(
        extract_links(html)
    )