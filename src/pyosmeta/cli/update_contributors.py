import pickle

from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import get_api_token

# TODO: will this still run in gh actions??
# TODO: add update=True like i did for update_reviews
# TODO: still need to add a flag to not update specific fields


def main():
    GITHUB_TOKEN = get_api_token()
    update_all = False

    # TODO - maybe add these as an attr in the contribs class?
    json_files = [
        "https://raw.githubusercontent.com/pyOpenSci/python-package-guide/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/software-peer-review/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/software-review/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/update-web-metadata/main/.all-contributorsrc",
    ]

    # Get existing contribs from pyopensci.github.io repo (website data)
    web_yaml_path = "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/_data/contributors.yml"

    processContribs = ProcessContributors(json_files, GITHUB_TOKEN)

    # Returns a list of dict objects with gh usernames (lowercase) as keys
    # TODO: File io module (could just be a function)
    web_contribs = processContribs.load_website_yml(
        a_url=web_yaml_path, a_key="github_username"
    )
    bot_all_contribs_dict = processContribs.combine_json_data()

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
                    processContribs.check_add_user(gh_user, web_contribs)
                )

            # Update contrib type list
            existing_contribs = web_contribs[gh_user]["contributor_type"]
            # TODO: This helper is used in all three scripts but defined
            # in the contribs class
            web_contribs[gh_user][
                "contributor_type"
            ] = processContribs.update_contrib_list(existing_contribs, key)

    if update_all:
        gh_data = processContribs.get_gh_data(web_contribs)
        web_contribs = processContribs.update_contrib_data(web_contribs, gh_data)

    # Export data
    # Pickle supports updates after parsing reviews
    with open("all_contribs.pickle", "wb") as f:
        pickle.dump(web_contribs, f)

    # TODO: clean export yml if from fileio class and used in all three scripts
    processContribs.clean_export_yml(web_contribs, "contributors.yml")


### ONE TIME REORDER OF WEB YAML ###
# review[package_name] = {
#                 key: review[package_name][key] for key in key_order
#             }
if __name__ == "__main__":
    main()
