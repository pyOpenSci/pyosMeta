import argparse
import pickle
from datetime import datetime

from pydantic import ValidationError
from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import create_paths, load_pickle, open_yml_file
from pyosmeta.github_api import GitHubAPI
from pyosmeta.models import PersonModel

# TODO - https://stackoverflow.com
# /questions/55762673/how-to-parse-list-of-models-with-pydantic
# I can use TypeAdapter to convert the json data to model objects!


def main():
    update_dates = False
    update_all = False
    parser = argparse.ArgumentParser(
        description="A CLI script to update pyOpenSci contributors"
    )
    parser.add_argument(
        "--update",
        type=str,
        help="Force update contrib info from GitHub for every contributor",
    )
    args = parser.parse_args()
    update_value = args.update

    if update_value:
        update_all = True

    repos = [
        "python-package-guide",
        "software-peer-review",
        "pyopensci.github.io",
        "software-review",
        "pyosmeta",
    ]
    json_files = create_paths(repos)

    # Get existing contribs from pyopensci.github.io repo (website data)
    base_url = "https://raw.githubusercontent.com/pyOpenSci/"
    web_yaml_path = (
        base_url + "pyopensci.github.io/main/_data/contributors.yml"
    )

    web_contribs = open_yml_file(web_yaml_path)

    # Populate all existing contribs into model objects
    all_contribs = {}
    for a_contrib in web_contribs:
        print(a_contrib["github_username"])
        try:
            all_contribs[a_contrib["github_username"].lower()] = PersonModel(
                **a_contrib
            )
        except ValidationError as ve:
            print(a_contrib["github_username"])
            print(ve)

    print("Done processing all-contribs")

    # Create a list of all contributors across repositories
    github_api = GitHubAPI()
    process_contribs = ProcessContributors(github_api, json_files)
    bot_all_contribs = process_contribs.combine_json_data()

    print("Updating contrib types and searching for new users now")
    for key, users in bot_all_contribs.items():
        for gh_user in users:
            # Find and populate data for any new contributors
            if gh_user not in all_contribs.keys():
                print("Missing", gh_user, "Adding them now")
                new_contrib = process_contribs.return_user_info(gh_user)
                new_contrib["date_added"] = datetime.now().strftime("%Y-%m-%d")
                all_contribs[gh_user] = PersonModel(**new_contrib)

            # Update contribution type list for all users
            all_contribs[gh_user].add_unique_value("contributor_type", key)

    if update_all:
        for user in all_contribs.keys():
            print("Updating all user info from github", user)
            new_gh_data = process_contribs.return_user_info(user)

            # TODO: turn this into a small update method
            existing = all_contribs[user].model_dump()

            for key, item in new_gh_data.items():
                if key == "mastodon":
                    # Mastodon isn't available in the GH api yet
                    continue
                # Don't replace the value if there is a noupdate flag
                # TODO: This approach doesn't work, ruemal-yaml doesn't
                # preserve inline comments
                if key == "name" and existing[key]:
                    continue
                else:
                    existing[key] = item

            all_contribs[user] = PersonModel(**existing)

    # One time only - add contrib added date
    if update_dates:
        history = load_pickle("contrib_dates.pickle")

        for user, data in all_contribs.items():
            try:
                setattr(data, "date_added", history[user])
            except KeyError:
                print(f"Username {user} must be new, skipping")

    # Export to pickle which supports updates after parsing reviews
    with open("all_contribs.pickle", "wb") as f:
        pickle.dump(all_contribs, f)


if __name__ == "__main__":
    main()
