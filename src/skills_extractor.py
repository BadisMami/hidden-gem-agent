KNOWN_SKILLS = [
    "Python",
    "C++",
    "C",
    "Java",
    "JavaScript",
    "Git",
    "GitHub",
    "Linux",
    "Docker",
    "SQL",
    "PyTorch",
    "TensorFlow",
    "ROS",
    "React",
    "Arduino",
    "STM32",
    "FPGA",
    "Azure"
]

def extract_skills(text):
    found_skills = []

    for skill in KNOWN_SKILLS:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    return found_skills


if __name__ == "__main__":
    sample_text = """
    Python
    C++
    Linux
    Git
    PyTorch
    """

    skills = extract_skills(sample_text)

    print("Skills Found:")
    print(skills)