import re

# Ordered (most specific / most easily confused with SWE first). The first
# category whose keyword appears in the title wins - order is deliberate,
# e.g. "Robotics Software Intern" must classify as Robotics, not SWE, and
# "Product Management Intern" must not classify as SWE just because it's
# a technical internship.
ROLE_KEYWORDS = [
    ("Product", [
        "product management",
        "product manager",
        "product management intern",
    ]),
    ("Cybersecurity", [
        "cybersecurity",
        "cyber security",
        "security engineer",
        "security analyst",
        "infosec",
        "application security",
    ]),
    ("Robotics", [
        "robotics",
        "robot",
        "autonomy",
    ]),
    ("ML", [
        "machine learning",
        "artificial intelligence",
        "ai engineer",
        "ai research",
        "ai safety",
        "computer vision",
        "deep learning",
        "nlp",
        "ml engineer",
        "ml research",
    ]),
    ("Data", [
        "data science",
        "data scientist",
        "data engineering",
        "data engineer",
        "data analytics",
        "data analyst",
    ]),
    ("Embedded", [
        "embedded",
    ]),
    ("Firmware", [
        "firmware",
    ]),
    ("Hardware", [
        "hardware",
        "fpga",
        "asic",
        "electrical engineering",
    ]),
    ("SWE", [
        "software engineer",
        "software engineering",
        "software development",
        "software quality assurance",
        "quality assurance engineer",
        "full stack",
        "fullstack",
        "backend",
        "back end",
        "frontend",
        "front end",
        "web developer",
        "application developer",
        "devops",
    ]),
]


def classify_role(title):
    """
    Deterministically classify an internship title into a role category.

    Returns one of: SWE, ML, Data, Embedded, Firmware, Hardware,
    Cybersecurity, Robotics, Product, Other.
    """

    if not title:
        return "Other"

    normalized = re.sub(r"\s+", " ", title).strip().lower()

    for category, keywords in ROLE_KEYWORDS:

        for keyword in keywords:

            if keyword in normalized:

                return category

    return "Other"
