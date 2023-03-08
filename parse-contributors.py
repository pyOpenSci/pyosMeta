import pickle

from pyosmeta.contributors import ProcessContributors

with open("../token.pickle", "rb") as f:
    API_TOKEN = pickle.load(f)

# TODO (maybe) this is slightly different than the website format.
# here the name doesn't have a - next to it - rather it is the first item
# all meta associated with the name is then indented.
# This might be ok i may just have to revisit the website loops
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
# Returns a list of dict objects
web_yml_dict = process_contribs.load_website_yml()

# Create a single dict containing both website and all-contrib bot users
all_contribs_dict = process_contribs.combine_users(bot_all_contribs_dict, web_yml_dict)

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
all_contribs_dict_updated = process_contribs.update_contrib_data(
    all_contribs_dict, gh_data, update_keys
)

final_filename = "contributors.yml"
# Create updated YAML file and clean to match the website
process_contribs.export_yaml(
    filename=final_filename, data_dict=all_contribs_dict_updated
)

# TODO see if we need this step now with the new format?process_contribs.clean_yaml_file(final_filename)
