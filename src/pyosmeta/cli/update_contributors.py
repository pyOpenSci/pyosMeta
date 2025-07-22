"""
A CLI script that parses through our existing contributor list stored
in pyopensci.github.io repo in the _data/contributors.yml file.

This script should respect if a persons's name is in the contributor file,
then it should be able to retain that name as their desired name (they can update
that file if they wish). It should NOT overwrite that name

It can also use that name when searching for maintainers
"""

import argparse
import pickle
from datetime import datetime

from pydantic import ValidationError
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import create_paths, load_pickle, open_yml_file
from pyosmeta.github_api import GitHubAPI
from pyosmeta.logging import logger
from pyosmeta.models import PersonModel


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
        "handbook",
        "software-submission",
        "metrics",
        "pyosPackage",
        "pyos-sphinx-theme",
        "lessons",
        "pyos-package-template",
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
    for a_contrib in tqdm(web_contribs, desc="Processing all-contribs"):
        username = a_contrib["github_username"]
        tqdm.write(f"Processing {username}")
        with logging_redirect_tqdm():
            try:
                all_contribs[username.lower()] = PersonModel(**a_contrib)
            except ValidationError:
                logger.error(f"Error processing {username}", exc_info=True)

    # Create a list of all contributors across repositories
    github_api = GitHubAPI()
    process_contribs = ProcessContributors(github_api, json_files)
    bot_all_contribs = process_contribs.combine_json_data()

    for key, users in tqdm(
        bot_all_contribs.items(),
        desc="Updating contrib types and searching for new users",
    ):
        for gh_user in users:
            # Find and populate data for any new contributors
            if gh_user not in all_contribs.keys():
                logger.info(f"Missing {gh_user}, adding them now")
                new_contrib = process_contribs.return_user_info(gh_user)
                new_contrib["date_added"] = datetime.now().strftime("%Y-%m-%d")
                all_contribs[gh_user] = PersonModel(**new_contrib)

            # Update contribution type list for all users
            all_contribs[gh_user].add_unique_value("contributor_type", key)

    if update_all:
        for user in tqdm(all_contribs.keys(), dec="Updating all user info"):
            tqdm.write("Updating all user info from github for {user}")
            new_gh_data = process_contribs.return_user_info(user)

            # TODO: turn this into a small update method
            existing = all_contribs[user].model_dump()

            for key, item in new_gh_data.items():
                if key == "mastodon":
                    # Mastodon isn't available in the GH api yet
                    continue
                # Don't replace the Name value from GitHub if there is a name
                # already listed in the contributors.yml file.
                # This allows for users to manually update their names and it
                # won't be overwritten. This also means an update on GitHub will
                # not be updated here which for now is ok. Not everyone has their
                # name listed on GH.
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
                logger.error(
                    f"Username {user} must be new, skipping", exc_info=True
                )

    # Export to pickle which supports updates after parsing reviews
    with open("all_contribs.pickle", "wb") as f:
        pickle.dump(all_contribs, f)


if __name__ == "__main__":
    main()
