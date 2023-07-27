import argparse
import pickle

from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import clean_export_yml, load_website_yml

# TODO: will this still run in gh actions??
# TODO: add update=True like i did for update_reviews
# TODO: still need to add a flag to not update specific fields
# TODO: if i use composition and there are helpers in a class
# that are used in a method that i call via composition are the helpers
# still available?


def main():
    update_all = False
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

    # Get existing contribs from pyopensci.github.io repo (website data)
    web_yaml_path = base_url + "pyopensci.github.io/main/_data/contributors.yml"

    process_contribs = ProcessContributors(json_files)

    # Returns a list of dict objects with gh usernames (lowercase) as keys
    # TODO: File io module (could just be a function)
    web_contribs = load_website_yml(url=web_yaml_path, key="github_username")
    bot_all_contribs_dict = process_contribs.combine_json_data()

    # Parse through each user in the web yaml, if they don't exist, add them
    # finally - update contrib types
    for key, users in bot_all_contribs_dict.items():
        for gh_user in users:
            # Add any new contributors
            if gh_user not in web_contribs.keys():
                print("I found a new contributor! Adding:", gh_user)
                web_contribs.update(
                    # TODO: this is also used in the other 2 scripts
                    # but add user info is in the contribs class - i do
                    # think it belongs there
                    process_contribs.check_add_user(gh_user, web_contribs)
                )

            # Update contrib type list
            existing_contribs = web_contribs[gh_user]["contributor_type"]
            # TODO: This helper is used in all three scripts but defined
            # in the contribs class
            web_contribs[gh_user][
                "contributor_type"
            ] = process_contribs.update_contrib_list(existing_contribs, key)

    if update_all:
        gh_data = process_contribs.get_gh_data(web_contribs)
        web_contribs = process_contribs.update_contrib_data(web_contribs, gh_data)

    # Export data
    # Pickle supports updates after parsing reviews
    with open("all_contribs.pickle", "wb") as f:
        pickle.dump(web_contribs, f)


if __name__ == "__main__":
    main()
