import pickle

from pyosmeta.contributors import ProcessContributors

with open("../token.pickle", "rb") as f:
    API_TOKEN = pickle.load(f)

# TODO: remove emails from the website repo YAML
# Maybe for now just create a text file with name, gh username, email?

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

# TODO: Make sure all gh usernames are lower case
for key in all_contribs_dict:
    all_contribs_dict[key]["github_username"] = all_contribs_dict[key][
        "github_username"
    ].lower()
    print(all_contribs_dict[key]["github_username"])

gh_data = process_contribs.get_gh_data(all_contribs_dict.keys(), API_TOKEN)

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
all_contribs_dict_up = process_contribs.update_contrib_data(
    all_contribs_dict, gh_data, update_keys
)

# Turn dict into list for parsing
final_contribs = []
for key in all_contribs_dict_up:
    final_contribs.append(all_contribs_dict_up[key])

final_yaml = "contributors.yml"
# Create updated YAML file and clean to match the website
process_contribs.export_yaml(final_yaml, final_contribs)
process_contribs.clean_yaml_file(final_yaml)


### ONE TIME REORDER OF WEB YAML ###
# web_yml_dict.keys()


# review[package_name] = {
#                 key: review[package_name][key] for key in key_order
#             }
