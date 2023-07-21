import pickle
from os.path import exists

from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import get_api_token

# TODO: Turn this into a conditional that checks for a .env file and
# if that doesn't exist then assume it's being run in actions.


def main():
    GITHUB_TOKEN = get_api_token()

    json_files = [
        "https://raw.githubusercontent.com/pyOpenSci/python-package-guide/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/software-peer-review/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/software-review/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/update-web-metadata/main/.all-contributorsrc",
    ]

    # Get contribs from pyopensci.github.io repo (this is what is published online)
    web_yaml_path = "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/_data/contributors.yml"

    # Instantiate contrib object
    processContribs = ProcessContributors(json_files, GITHUB_TOKEN)

    # Returns a list of dict objects with gh usernames (lowercase) as keys
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
                print("Need to add:", gh_user)
                # TODO - maybe i just update contrib types all at once?
                web_contribs.update(
                    processContribs.check_add_user(gh_user, web_contribs)
                )

            # Update contrib type list
            existing_contribs = web_contribs[gh_user]["contributor_type"]
            web_contribs[gh_user][
                "contributor_type"
            ] = processContribs.update_contrib_list(existing_contribs, key)

    # TODO:
    # It might make sense to do this if update=True flag exists
    # alternatively we just run it as a separate step once a month??
    # BUT add a flag for rows in case someone wants to pin information??

    # This step gets new gh data for every user in dictionary
    # provided to it
    # gh_data = processContribs.get_gh_data(web_contribs)
    # this step then updates each contributors data from that gh_data
    # retrieved above
    # all_contribs_dict_up = processContribs.update_contrib_data(
    #     all_contribs_dict, gh_data
    # )

    # Export data
    # Pickle supports updates after parsing reviews
    with open("all_contribs.pickle", "wb") as f:
        pickle.dump(web_contribs, f)

    processContribs.clean_export_yml(web_contribs, "contributors.yml")


### ONE TIME REORDER OF WEB YAML ###
# review[package_name] = {
#                 key: review[package_name][key] for key in key_order
#             }
if __name__ == "__main__":
    main()
