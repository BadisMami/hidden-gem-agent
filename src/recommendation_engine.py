from resume_parser import extract_text
from skills_extractor import extract_skills
from database_matcher import find_internships


def get_recommendations(resume_path, interests):

    text = extract_text(resume_path)

    skills = extract_skills(text)

    recommendations = {}

    for interest in interests:
        recommendations[interest] = (
            find_internships(interest)
        )

    return skills, recommendations