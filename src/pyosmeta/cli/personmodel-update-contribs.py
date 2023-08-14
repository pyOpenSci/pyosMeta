import argparse
import os
import pickle

import pydantic
from pydantic import ValidationError

from pyosmeta.contributors import PersonModel, ProcessContributors
from pyosmeta.file_io import clean_export_yml, open_yml_file

print(pydantic.__version__)
# TODO - fix the website by renaming   packages-editor, packages-submitted:
# packages-reviewed: to use underscores. this will just make life easier


def main():
    parser = argparse.ArgumentParser(
        description="A CLI script to update pyOpenSci contributors"
    )
    parser.add_argument(
        "--update",
        type=str,
        help="Will force update contrib info from GitHub for every contributor",
    )
    args = parser.parse_args()

    if args:
        update_all = True

    base_url = "https://raw.githubusercontent.com/pyOpenSci/"
    end_url = "/main/.all-contributorsrc"
    repos = [
        "python-package-guide",
        "software-peer-review",
        "pyopensci.github.io",
        "software-review",
        "update-web-metadata",
    ]
    json_files = [base_url + repo + end_url for repo in repos]

    # Get existing contribs from pyopensci.github.io repo (website data)
    web_yaml_path = base_url + "pyopensci.github.io/main/_data/contributors.yml"

    web_contribs = open_yml_file(web_yaml_path)

    # Populate all existing contribs into model objects
    all_contribs = {}
    for a_contrib in web_contribs:
        try:
            if a_contrib["github_username"].lower() == "arianesasso":
                print("pause")
            all_contribs[a_contrib["github_username"].lower()] = PersonModel(
                **a_contrib
            )
        except ValidationError as ve:
            print(a_contrib["github_username"])
            print(ve)

    print("Done processing all-contribs")
    # TODO - maybe add these as an attr in the contribs class?
    base_url = "https://raw.githubusercontent.com/pyOpenSci/"
    end_url = "/main/.all-contributorsrc"
    repos = [
        "python-package-guide",
        "software-peer-review",
        "pyopensci.github.io",
        "software-review",
        "update-web-metadata",
    ]
    json_files = [base_url + repo + end_url for repo in repos]

    # Create a list of all contributors across repositories
    process_contribs = ProcessContributors(json_files)
    bot_all_contribs = process_contribs.combine_json_data()

    # TODO this is much slower than it should be
    print("Updating contrib types and searching for new users now")
    # bot_all contris is a dict of x contrib types with an associated list of
    # users who contributed to that type.
    for key, users in bot_all_contribs.items():
        print(key)
        for gh_user in users:
            # Find and populate data for any new contributors
            if gh_user not in all_contribs.keys():
                print("Missing", gh_user, "Adding them now")
                new_contrib = process_contribs.get_user_info(gh_user)
                all_contribs[gh_user] = PersonModel(**new_contrib)

            # Update contribution type list for all users
            existing_contribs = all_contribs[gh_user].contributor_type
            all_contribs[
                gh_user
            ].contributor_type = process_contribs.update_contrib_list(
                existing_contribs, key
            )

    if update_all:
        for user in all_contribs.keys():
            print("Updating all user info from github", user)
            new_contrib = process_contribs.get_user_info(user)
            # Update person's data (should skip update for any text
            # with # noupdate flag)
            all_contribs[user] = all_contribs[user].update(new_contrib)

    # Export to pickle which supports updates after parsing reviews
    with open("all_contribs.pickle", "wb") as f:
        pickle.dump(all_contribs, f)

    alist = []
    for key, item in all_contribs.items():
        alist.append(item.model_dump())

    # Test export
    print(os.getcwd())
    clean_export_yml(alist, os.path.join("_data", "contribs.yml"))


if __name__ == "__main__":
    main()
