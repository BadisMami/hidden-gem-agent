def calculate_match_score(
    user_skills,
    internship_keywords
):

    matches = 0

    for skill in user_skills:

        if skill.lower() in [
            keyword.lower()
            for keyword
            in internship_keywords
        ]:

            matches += 1

    return matches