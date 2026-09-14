def create_alert(company,
                 job_title,
                 location):

    alert = f"""
NEW INTERNSHIP FOUND

Company: {company}

Position: {job_title}

Location: {location}
"""

    return alert


if __name__ == "__main__":

    alert = create_alert(
        "Garmin",
        "Embedded Software Intern",
        "Olathe KS"
    )

    print(alert)