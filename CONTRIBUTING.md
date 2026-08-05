# Contributing

To run `update-review-teams`, you'll need to run both `update-reviews` and `update-contributors` first to create the required input `.pickle` files.

The scripts run as follows.

## Local setup

See the [Development Guide](./development.md) for how to set up a local
development environment with `uv`, including installing dependencies and
setting up your `GITHUB_TOKEN` for the GitHub API.

Each script is available through the command line via entry points specified in the `pyproject.toml` file. Run them with `uv run`.

## update-contributors script

To run you can use:

`uv run update-contributors`

if needed, 1--update update_all1 flag will update the contributor profile information, including name, using whatever information is available on their public GitHub account (website, location, organization, Twitter, etc). It will also check that the website in their profile works; if not, remove it so it doesn't fail the website's CI tests.

This flag will rarely need to be used.

`uv run update-contributors --update update_all`

This script parses data from all-contributors bot `.json`
files in the following repos:

* [python-package-guide](https://github.com/pyOpenSci/python-package-guide)
* [software-peer-review](https://github.com/pyOpenSci/software-peer-review) (peer review guide)
* [pyopensci.github.io](https://github.com/pyOpenSci/pyopensci.github.io) (website)
* [software-review](https://github.com/pyOpenSci/software-review)
* [pyosMeta](https://github.com/pyOpenSci/pyosMeta) *(this repo)*
* [handbook](https://github.com/pyOpenSci/handbook)
* [software-submission](https://github.com/pyOpenSci/software-submission) where peer review happens
* [metrics](https://github.com/pyOpenSci/metrics)
* [pyosPackage](https://github.com/pyOpenSci/pyosPackage)
* [pyos-sphinx-theme](https://github.com/pyOpenSci/pyos-sphinx-theme)
* [lessons](https://github.com/pyOpenSci/lessons)
* [pyos-package-template](https://github.com/pyOpenSci/pyos-package-template)

This list is defined in the `repos` variable in
[`update_contributors.py`](./src/pyosmeta/cli/update_contributors.py), which
is the source of truth. Update the list there first, and then update this
doc to match.

Running this script:

1. Parses through all of the all-contributors bot `.json` files across pyOpenSci's repos to gather contributors.
   This allows pyOpenSci to [acknowledge contributors on the website](https://www.pyopensci.org/our-community/#pyopensci-community-contributors)
   who aren't always making explicit code contributions (and thus might not have commits). These contributors are
   reviewing guidebooks, participating in peer review, and performing other important tasks that are critical to
   pyOpenSci's mission. pyOpenSci acknowledges all contributions, regardless of volume or size.
2. Updates the existing [contributors.yml](https://github.com/pyOpenSci/pyopensci.github.io/blob/main/data/contributors.yml)
   file found in the website repo with new contributors and the contributor role (package guides, code workflows, peer review, etc).
   If you run the script using `--update update_all`, it will also use the GitHub API to update the users' metadata from their GitHub profile.

If you use the `--update update_all` flag, it will:

* Update contributor profile information, including name, using whatever information is available on their public
  GitHub account (website, location, organization, Twitter, etc).
* Check that the website in their profile works; if not, remove it so it doesn't fail the website's CI tests.

Without the `--update` flag, running `update-contributors` will only add any new users that
are not already in the website's `contributors.yml` file to an output `.pickle` file.

### Returns

* `all-contributors.pickle` file that will be used in the final `update-review-teams` script to update all reviewer contribution data.

## update-reviews script

To run:

`uv run update-reviews` or
`uv run update-reviews --update update_all`

This script parses through pyOpenSci's (*accepted*) review issues to find packages that have been accepted. It then grabs each
review's editor, reviewers, and package authors/maintainers. This information is used to:

1. Update a contributor's peer review metadata in the `contributors.yml` file in the third script.
2. Update the website's package listing with the package's DOI and documentation URL.
3. Update the package's stats, including stars and contributors, using the GitHub API.

It also collects the GitHub ID and user information for:

* reviewers,
* submitting authors,
* editors, and
* maintainers.

Finally, it updates GitHub statistics for each package, including stars, last commit date, and more repo metadata.

### Returns

This returns a `packages.pickle` file that will be used in the final script, which bridges data between the first two scripts.

## update-review-teams script

This script is a bridge between `update-contributors` and `update-reviews`. It uses the pickle files output from
the first two scripts to update each contributor's peer review contributions, including:

1. packages submitted or reviewed
2. packages for which the contributor served as an editor
3. contributor types associated with peer review, including:

* peer-review
* package-maintainer
* package-reviewer
* package-editor

These general contributor types are used to drive the
[website's contributor search and filter functionality](https://www.pyopensci.org/our-community/index.html#pyopensci-community-contributors).

It also updates the contributor's name in the review data (often the GitHub username is present but the first
and last name are missing). This lets pyOpenSci publish maintainer names (rather than GitHub usernames)
[on the website's package listing](https://www.pyopensci.org/python-packages.html#explore-our-accepted-scientific-python-open-source-packages).

To run:

`uv run update-review-teams`

### Returns

This final script uses the two pickle files to update information. It returns two output files:

1. `data/contributors.yml`
2. `data/packages.yml`

Both are stored in the `data/` directory, mirroring the pyOpenSci website's directory structure (see our website repo here)[https://www.github.com/pyopensci/pyopensci.github.io).

## How these scripts are used at pyOpenSci

The scripts above are called in the [GitHub
actions located here](https://github.com/pyOpenSci/pyopensci.github.io/tree/main/.github/workflows). These actions can be run manually via workflow dispatch and also run on a cron job that updates the metadata periodically.

### Data that these scripts update / maintain

* [website contributors.yml file](https://github.com/pyOpenSci/pyopensci.github.io/blob/main/data/contributors.yml)
* [website packages.yml file is here](https://github.com/pyOpenSci/pyopensci.github.io/blob/main/data/packages.yml).

## Rate limiting

TODO: right now this isn't an issue but it will be in the future I suspect....
Rate limiting - how to handle this...

## pyosMeta build and release guide

See the [Development Guide](./development.md#pyosmeta-build) for how to build
`pyosmeta` locally and how to make a release to PyPI (both use Hatch).
