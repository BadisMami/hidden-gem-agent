from skill_matcher import (
    calculate_match_score
)

user_skills = [
    "Python",
    "C++",
    "ROS",
    "FPGA"
]

internship_keywords = [
    "Python",
    "C++",
    "Autonomy"
]

score = calculate_match_score(
    user_skills,
    internship_keywords
)

print(
    f"Match Score: {score}"
)