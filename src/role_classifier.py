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


# The role categories I actually want texts for. Every internship is
# still stored and classified, but only these trigger an alert.
TARGET_ROLES = {"SWE", "ML", "Embedded", "Robotics"}


def is_target_role(role_type):

    return role_type in TARGET_ROLES


# PhD/Master's/MBA-only postings. Deliberately doesn't match a bare "MS"
# or "graduate" - those collide with "MS Office", "new grad", etc.
_GRAD_ONLY_RE = re.compile(
    r"\bph\.?\s?d\b|\bdoctoral\b|\bdoctorate\b|\bpost-?doc|"
    r"\bmaster'?s\b|\bmasters\b|\bmaster of\b|\bmba\b|\bgraduate student",
    re.IGNORECASE
)

_UNDERGRAD_RE = re.compile(r"\bundergrad", re.IGNORECASE)


def is_grad_only(title):
    """
    True for internships aimed at PhD/Master's/MBA students. A title that
    also mentions undergrads (e.g. "Undergraduate and Master's R&D
    Intern") is still open to undergrads, so it doesn't count.
    """

    if not title:
        return False

    return bool(_GRAD_ONLY_RE.search(title)) and not _UNDERGRAD_RE.search(title)


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
