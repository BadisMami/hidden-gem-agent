import re


def clean_text(text):

    replacements = {

        "Py Torch": "PyTorch",
        "Tensor Flow": "TensorFlow",
        "Node JS": "Node.js",
        "Node Js": "Node.js",
        "Nodejs": "Node.js",
        "Fast API": "FastAPI",
        "Springboot": "Spring Boot",
        "Postgres SQL": "PostgreSQL",
        "Mongo DB": "MongoDB",
        "Git Hub": "GitHub",
        "Type Script": "TypeScript",

        # OCR corrections
        "Dicker": "Docker",
        "Linu": "Linux",
        "Kubertes": "Kubernetes",
        "MougiDB": "MongoDB",
        "PosaseSQL": "PostgreSQL",
        "Reet": "React",
        "Fat API": "FastAPI",
        "LangChais": "LangChain",
        "TensoeFow": "TensorFlow",
        "TopeScrpt": "TypeScript",

        "Reggt": "React",
        "Kuburlet": "Kubernetes",
        "LuzuDB": "MongoDB",
        "FclueSqL": "PostgreSQL",
        "Llus": "Linux",
        "LAuLec": "Docker",
        "P tla": "Python",
        "Typuernip": "TypeScript",
        "Tenrn Fkx": "TensorFlow",
        "LangChal": "LangChain",
    }

    for bad, good in replacements.items():

        text = text.replace(
            bad,
            good
        )

    return text


KNOWN_SKILLS = [

    "Python",
    "C++",
    "C",
    "Java",
    "JavaScript",
    "TypeScript",

    "React",
    "Node.js",
    "FastAPI",
    "Spring",
    "Spring Boot",

    "SQL",
    "PostgreSQL",
    "MongoDB",

    "Docker",
    "Kubernetes",
    "Linux",

    "Git",
    "GitHub",

    "Machine Learning",
    "Artificial Intelligence",
    "Computer Vision",
    "RAG",

    "PyTorch",
    "TensorFlow",
    "LangChain",
    "OpenCV",
    "ONNX",
    "Google ADK",

    "Jenkins",
    "JIRA",

    "Azure",
    "AWS"
]

KNOWN_SKILLS = sorted(
    KNOWN_SKILLS,
    key=len,
    reverse=True
)

SPECIAL_PATTERNS = {
    "C++": r"c\+\+",
    "Node.js": r"node(\.js)?",
    "FastAPI": r"fastapi",
    "Spring Boot": r"spring boot",
    "Google ADK": r"google adk",
    "Machine Learning": r"machine learning",
    "Artificial Intelligence": r"artificial intelligence",
    "Computer Vision": r"computer vision",
    "LangChain": r"langchain",
    "TensorFlow": r"tensorflow",
    "PyTorch": r"pytorch",
    "TypeScript": r"typescript"
}


def extract_skills(text):

    text = clean_text(text)

    found_skills = []

    for skill in KNOWN_SKILLS:

        if skill in SPECIAL_PATTERNS:

            pattern = SPECIAL_PATTERNS[skill]

        else:

            pattern = (
                r"\b"
                + re.escape(skill)
                + r"\b"
            )

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found_skills.append(
                skill
            )

    return found_skills


if __name__ == "__main__":

    sample_text = """
    Python
    C++
    TypeScript
    FastAPI
    React
    Node.js
    Docker
    Kubernetes
    MongoDB
    PostgreSQL
    """

    skills = extract_skills(
        sample_text
    )

    print("Skills Found:")
    print(skills)
