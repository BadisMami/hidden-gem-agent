from user_profile import create_profile
from recommendation_engine import get_recommendations


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

        for _, row in internships.iterrows():

            print(
                f"{row['company']} | "
                f"{row['title']} | "
                f"{row['location']}"
            )


if __name__ == "__main__":
    main()