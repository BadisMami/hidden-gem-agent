def calculate_match_score(
    user_skills,
    internship_title
):
    """
    Calculate a relevance score based on
    resume skills matching keywords in
    the internship title.
    """

    score = 0

    title = internship_title.lower()

    keyword_map = {
        "Python": [
            "python",
            "machine learning",
            "ai",
            "artificial intelligence",
            "computer vision",
            "deep learning"
        ],

        "C++": [
            "software",
            "engineering"
        ],

        "ROS": [
            "autonomy",
            "robotics",
            "navigation",
            "robot"
        ],

        "FPGA": [
            "fpga",
            "firmware"
        ],

        "Arduino": [
            "embedded"
        ],

        "SQL": [
            "data",
            "analytics"
        ],
        "Linux": [
            "systems",
            "platform"
        ],
        "Git": [
            "software"
        ]
    }

    for skill in user_skills:

        if skill in keyword_map:

            for keyword in keyword_map[skill]:

                if keyword in title:

                    score += 1

    return score


if __name__ == "__main__":

    skills = [
        "Python",
        "C++",
        "ROS",
        "FPGA"
    ]

    internships = [
        "Autonomy Engineer Intern",
        "Machine Learning Intern",
        "FPGA Engineering Intern",
        "Accounting Intern",
        "Computer Vision Intern",
        
    ]

    for internship in internships:

        score = calculate_match_score(
            skills,
            internship
        )

        print(
            f"{internship}: Score = {score}"
        )