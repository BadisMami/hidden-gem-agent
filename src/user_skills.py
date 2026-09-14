from resume_parser import extract_text
from skills_extractor import extract_skills


def get_user_skills(resume_path):

    text = extract_text(
        resume_path
    )

    skills = extract_skills(
        text
    )

    return skills


if __name__ == "__main__":

    resume_path = (
        "data/resumes/badis_resume.pdf"
    )

    skills = get_user_skills(
        resume_path
    )

    print(skills)