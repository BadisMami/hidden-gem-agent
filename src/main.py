from user_profile import create_profile
from recommendation_engine import get_recommendations
from internship_ranker import score_internship


def main():

    print("\n===== Hidden Gem Internship Agent =====\n")

    profile = create_profile()

    resume_path = (
        "data/resumes/badis_resume.pdf"
    )

    skills, recommendations = (
        get_recommendations(
            resume_path,
            profile["interests"]
        )
    )

    print("\nSkills Found:\n")

    for skill in skills:
        print("-", skill)

    print("\nRecommended Internships:\n")

    for interest, internships in recommendations.items():

        print(f"\n{interest} Opportunities:\n")

        ranked_results = []

        for _, row in internships.iterrows():

            score = score_internship(
                skills,
                row["title"]
            )

            ranked_results.append(
                (
                    score,
                    row
                )
            )

        ranked_results.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        for score, row in ranked_results:

            print(
                f"{row['company']} | "
                f"{row['title']} | "
                f"{row['location']} | "
                f"Score: {score}"
            )


if __name__ == "__main__":
    main()