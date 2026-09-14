def score_internship(
    user_skills,
    internship_title
):

    score = 0

    title = internship_title.lower()

    keyword_map = {
        "Python": ["python"],
        "C++": ["software"],
        "ROS": ["autonomy", "robotics"],
        "FPGA": ["fpga", "firmware"],
        "Arduino": ["embedded"],
        "SQL": ["data"]
    }

    for skill in user_skills:

        if skill in keyword_map:

            for keyword in keyword_map[skill]:

                if keyword in title:

                    score += 1

    return score