
# PyOS Consolidate Contributor Data & Update Review Metadata

This repo contains a small module and some scripts that parse through GitHub repos in the pyOpenSci organization.

To begin;
1. create a local environment and activate it.
2. Install the required dependencies via the requirement.txt file by running the following command;
`pip install -r requirements.txt`

For an action to work will need to figure out the token part: https://github.com/orgs/community/discussions/46376

## Setup token to authenticate with the GitHub API

To run this you need to [create a TOKEN that can be used to access the GitHub
API.](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api?apiVersion=2022-11-28#about-tokens)

After obtaining a token;
1. Duplicate the `.env-default` file and rename the copy to `.env`
2. Assign your token to the `API_TOKEN` variable in the `.env` file.


## How to run each script

`python3 parse-contributors.py`

The parse-contributors.py script does the following:

1. It grabs the all-contribs.json files from each repository and turns that json data into a dictionary of all unique contributors across repos. Repos include:
   - peer review guide
   - packaging guide
   - website
   - software-review
2. It then:

- Updates their profile information including name (TODO: only update name if
  name is empty) using whatever information is available their public github
  account for website, location, organization, twitter, etc).
- Checks to see that the website in their profile works, if not removes it so it doesn't begin to fail our website ci tests.

Returns

- `contributors.yml` file to be added to the \_data directory of our website. This format can be easily parsed by jekyll.

### TODO's - parse-contributors.py

- In some cases users haven't updated their names on github and as such, if a
  name exists, we should leave it as is in the contributors.yml file.

### `python3 parse_review_issues.py.py`

To run:
`python3 parse_review_issues.py.py`

This script parses through all pyOpenSci software review issues where the package was accepted. It then collects the
GitHub id and user information for

- reviewers,
- submitting authors,
- editors and
- TODO: _SOON TO BE ADDED_ maintainers.

It also goes to the repo for each package and updates stats
such as stars, last commit date and more repo metadata.

### Returns

This returns a `packages.yml` file that can be used to update
the website

TODOs:

- now it doesn't grab all maintainers. That was a recent addition to our template.

### `python3 update_reviewers.py`

To run:
`python3 update_reviewers.py`

This script uses the updated contributor and review information
created from the scripts above. It then adds / updates the packages that
each contributor has reviewed, served as editor or submitted. In some cases if the person has not been added to our contributors.yml file it will first add then and grab their
github metadata. Then update their roles in the review process.

## Rate limiting

Rate limiting - how to handle this...

## Update contributors across repositories

The contributors script parses data from:

TODO: check which repos we actually are parsing...

- software-review repo
- python-package-guide repo
- peer-review-guide repo
- software-review repo

The first script updates contributor data by:

1. Grabbing each contributor `.json` file generated by the all-contributors bot in each repository
2. Parsing the website contributors.yml from the website.
3. Adding all contributors identified in step 1 to the website yaml file.
4. Finally it updates contributor metadata using each user's GitHub profile to get website, location, twitter handle, etc (if it is available)

This script allows pyOpenSci to quickly update the website contributor list with the current list of contributors. It also ensures contributor metadata is current (or up to date with what the user is maintaining on their GitHub user page)

## Update contributors across repositories

To update package and review metadata you can
use `parse_review_issues.py.py`.

This script:

- Parses each issue that has a label of 6/`pyOS-approved 🚀🚀🚀`.
- Grabs crucial metadata including the reviewers and editors for each.
- Finally it grabs package metadata to add to the packages.yml file including stats around last commit date, package stars and other github metrics.
- It should also add people who have participated in peer review who are NOT listed currently in the website contributors.yml file

python3 parse_review_issues.py

## Using this

Create environment:

`mamba env create -f environment.yml`

```
❯ hatch new pyosMeta2
pyosmeta2
├── pyosmeta2
│   ├── __about__.py
│   └── __init__.py
├── tests
│   └── __init__.py
├── LICENSE.txt
├── README.md
└── pyproject.toml
```

Hatch also seems to create an init and a about that has a standard version.

# How do i use Hatch with a conda environment?

looks like i have to install a plugin for this... wondering if i want to go with PDM for now? Or Poetry?

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/xmnlab"><img src="https://avatars.githubusercontent.com/u/5209757?v=4?s=100" width="100px;" alt="Ivan Ogasawara"/><br /><sub><b>Ivan Ogasawara</b></sub></a><br /><a href="https://github.com/pyOpenSci/update-web-metadata/commits?author=xmnlab" title="Code">💻</a> <a href="https://github.com/pyOpenSci/update-web-metadata/pulls?q=is%3Apr+reviewed-by%3Axmnlab" title="Reviewed Pull Requests">👀</a> <a href="#design-xmnlab" title="Design">🎨</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/meerkatters"><img src="https://avatars.githubusercontent.com/u/50787305?v=4?s=100" width="100px;" alt="Meer (Miriam) Williamson"/><br /><sub><b>Meer (Miriam) Williamson</b></sub></a><br /><a href="https://github.com/pyOpenSci/update-web-metadata/commits?author=meerkatters" title="Code">💻</a> <a href="https://github.com/pyOpenSci/update-web-metadata/pulls?q=is%3Apr+reviewed-by%3Ameerkatters" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://tiffanyxiao.com/"><img src="https://avatars.githubusercontent.com/u/13580331?v=4?s=100" width="100px;" alt="Tiffany Xiao"/><br /><sub><b>Tiffany Xiao</b></sub></a><br /><a href="https://github.com/pyOpenSci/update-web-metadata/commits?author=tiffanyxiao" title="Code">💻</a> <a href="https://github.com/pyOpenSci/update-web-metadata/pulls?q=is%3Apr+reviewed-by%3Atiffanyxiao" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/austinlg96"><img src="https://avatars.githubusercontent.com/u/19922895?v=4?s=100" width="100px;" alt="austinlg96"/><br /><sub><b>austinlg96</b></sub></a><br /><a href="https://github.com/pyOpenSci/update-web-metadata/commits?author=austinlg96" title="Code">💻</a> <a href="https://github.com/pyOpenSci/update-web-metadata/pulls?q=is%3Apr+reviewed-by%3Aaustinlg96" title="Reviewed Pull Requests">👀</a> <a href="#design-austinlg96" title="Design">🎨</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/paajake"><img src="https://avatars.githubusercontent.com/u/12656820?v=4?s=100" width="100px;" alt="JAKE"/><br /><sub><b>JAKE</b></sub></a><br /><a href="https://github.com/pyOpenSci/update-web-metadata/pulls?q=is%3Apr+reviewed-by%3Apaajake" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://luizirber.org"><img src="https://avatars.githubusercontent.com/u/6642?v=4?s=100" width="100px;" alt="Luiz Irber"/><br /><sub><b>Luiz Irber</b></sub></a><br /><a href="https://github.com/pyOpenSci/update-web-metadata/commits?author=luizirber" title="Code">💻</a> <a href="https://github.com/pyOpenSci/update-web-metadata/pulls?q=is%3Apr+reviewed-by%3Aluizirber" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bbulpett"><img src="https://avatars.githubusercontent.com/u/6424805?v=4?s=100" width="100px;" alt="Barnabas Bulpett (He/Him)"/><br /><sub><b>Barnabas Bulpett (He/Him)</b></sub></a><br /><a href="https://github.com/pyOpenSci/update-web-metadata/commits?author=bbulpett" title="Code">💻</a> <a href="https://github.com/pyOpenSci/update-web-metadata/pulls?q=is%3Apr+reviewed-by%3Abbulpett" title="Reviewed Pull Requests">👀</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
