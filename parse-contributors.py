import pickle

from pyosmeta.contributors import ProcessContributors

with open("../token.pickle", "rb") as f:
    API_TOKEN = pickle.load(f)

json_files = [
    "https://raw.githubusercontent.com/pyOpenSci/python-package-guide/main/.all-contributorsrc",
    "https://raw.githubusercontent.com/pyOpenSci/software-peer-review/main/.all-contributorsrc",
    "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/.all-contributorsrc",
    "https://raw.githubusercontent.com/pyOpenSci/software-review/main/.all-contributorsrc",
    # "https://raw.githubusercontent.com/pyOpenSci/examplepy/main/.all-contributorsrc",
]

# Get contribs from pyopensci.github.io repo (this is what is published online)
web_yaml_path = "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/_data/contributors.yml"

# Instantiate contrib object
processContribs = ProcessContributors(json_files, web_yaml_path, API_TOKEN)

# Returns a list of dict objects with gh usernames (lowercase) as keys
web_yml_dict = processContribs.load_website_yml()

bot_all_contribs_dict = processContribs.combine_json_data()


# TODO - this is all working now BUT for some reason some users
# eg jenny, david, contrib types are not fully updating
# Example david will get the web-contrib added but not packaging guide - but
# he's definitely in the packaging guide json file
# Create a single dict containing both website and all-contrib bot users
all_contribs_dict = processContribs.combine_users(bot_all_contribs_dict, web_yml_dict)

for key in all_contribs_dict:
    all_contribs_dict[key]["github_username"] = all_contribs_dict[key][
        "github_username"
    ].lower()
    print(all_contribs_dict[key]["github_username"])

gh_data = processContribs.get_gh_data(all_contribs_dict.keys())

# Update user yaml file data from GitHub API
update_keys = [
    "twitter",
    "website",
    "location",
    "bio",
    "organization",
    "email",
]

# Append github data to existing dictionary
all_contribs_dict_up = processContribs.update_contrib_data(all_contribs_dict, gh_data)

# Save a pickle locally to support updates after parsing
# reviews
with open("all_contribs.pickle", "wb") as f:
    pickle.dump(all_contribs_dict_up, f)

final_contribs = processContribs.dict_to_list(all_contribs_dict_up)
final_yaml = "contributors.yml"
# Create updated YAML file and clean to match the website
processContribs.export_yaml(final_yaml, final_contribs)
processContribs.clean_yaml_file(final_yaml)


### ONE TIME REORDER OF WEB YAML ###
# review[package_name] = {
#                 key: review[package_name][key] for key in key_order
#             }
