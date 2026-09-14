from internship_ranker import (
    score_internship
)

skills = [
    "Python",
    "C++",
    "ROS",
    "FPGA"
]

print(
    score_internship(
        skills,
        "Autonomy Software Engineering Intern"
    )
)

print(
    score_internship(
        skills,
        "Accounting Intern"
    )
)