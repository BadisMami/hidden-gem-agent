from resume_parser import extract_text
from skills_extractor import extract_skills

resume_path = "data/resumes/badis_resume.pdf"

text = extract_text(resume_path)

skills = extract_skills(text)

print("\nSkills Found:\n")

for skill in skills:
    print("-", skill)