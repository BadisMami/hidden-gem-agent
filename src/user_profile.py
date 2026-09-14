import json
import os


def create_profile():

    profile = {}

    profile["name"] = input("Name: ")
    profile["major"] = input("Major: ")

    print("\nInterests:")
    print("1. SWE")
    print("2. ML")
    print("3. Embedded")
    print("4. Firmware")
    print("5. Robotics")
    print("6. Cybersecurity")

    interests = input(
        "\nEnter interests separated by commas: "
    )

    profile["interests"] = [
        x.strip() for x in interests.split(",")
    ]

    return profile


def save_profile(profile):

    os.makedirs(
        "results/profiles",
        exist_ok=True
    )

    filename = (
        f"results/profiles/{profile['name']}.json"
    )

    with open(filename, "w") as file:
        json.dump(
            profile,
            file,
            indent=4
        )


if __name__ == "__main__":

    user = create_profile()

    save_profile(user)

    print("\nProfile Created:\n")
    print(user)