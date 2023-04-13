import pickle

from pyosmeta.contributors import ProcessContributors

with open("../token.pickle", "rb") as f:
    API_TOKEN = pickle.load(f)

json_files = [
    "https://raw.githubusercontent.com/pyOpenSci/python-package-guide/main/.all-contributorsrc",
    "https://raw.githubusercontent.com/pyOpenSci/software-peer-review/main/.all-contributorsrc",
    "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/.all-contributorsrc",
]

# Get contribs from website
web_yaml_path = "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/_data/contributors.yml"

process_contribs = ProcessContributors(json_files, web_yaml_path, API_TOKEN)
# Combine the cross-repo contribut data
bot_all_contribs_dict = process_contribs.combine_json_data()
# Returns a list of dict objects with gh username as a key
web_yml_dict = process_contribs.load_website_yml()

# Create a single dict containing both website and all-contrib bot users
all_contribs_dict = process_contribs.combine_users(bot_all_contribs_dict, web_yml_dict)

for key in all_contribs_dict:
    all_contribs_dict[key]["github_username"] = all_contribs_dict[key][
        "github_username"
    ].lower()
    print(all_contribs_dict[key]["github_username"])

gh_data = process_contribs.get_gh_data(all_contribs_dict.keys())

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
all_contribs_dict_up = process_contribs.update_contrib_data(all_contribs_dict, gh_data)

with open("all_contribs.pickle", "wb") as f:
    pickle.dump(all_contribs_dict_up, f)

final_contribs = process_contribs.dict_to_list(all_contribs_dict_up)
final_yaml = "contributors.yml"
# Create updated YAML file and clean to match the website
process_contribs.export_yaml(final_yaml, final_contribs)
process_contribs.clean_yaml_file(final_yaml)


### ONE TIME REORDER OF WEB YAML ###
# review[package_name] = {
#                 key: review[package_name][key] for key in key_order
#             }
