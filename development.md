# Development Guide

To work on pyosMeta, you'll use [uv](https://docs.astral.sh/uv/) to set up the development environment and run the package's CLI scripts.

You'll use Hatch for running tests and for building/publishing releases. pyosMeta's test scripts and versioning are defined via Hatch (see [Running tests](#running-tests) and [pyosMeta build](#pyosmeta-build) below).

## Setup a development environment

### Install uv

Follow the [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/), then open a new terminal and run `uv --version` to verify it's available.

### Create the environment and install dependencies

From the repo root, run:

```console
uv sync --extra dev
```

This creates a `.venv` in the repo, installs `pyosmeta` in editable mode, and installs the `dev` dependencies (pytest, black, flake8, pre-commit, etc.) defined in `pyproject.toml`.

### Setup a token to authenticate with the GitHub API

Most of the CLI scripts call the GitHub API, so you'll need a token:

1. [Create a fine-grained personal access token](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api?apiVersion=2022-11-28#about-tokens) with "Repository Access" set to "Public Repositories (read-only)". No other configuration needed.
2. Duplicate the `.env-default` file and rename the copy to `.env`.
3. Assign your token to the `GITHUB_TOKEN` variable in the `.env` file.

### Run the CLI scripts

Use `uv run` to execute any of the package's CLI entry points without manually activating the virtual environment:

```console
uv run update-contributors
uv run update-reviews
uv run update-review-teams
uv run parse-history
uv run fetch-rss-feed
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for what each script does and the flags it accepts (e.g. `uv run update-contributors --update update_all`).

If you'd rather activate the virtual environment directly, run `source .venv/bin/activate`, then call the scripts directly (e.g. `update-contributors`). To deactivate, run `deactivate`.

## Running tests

To run tests, you need to [install hatch](https://www.pyopensci.org/python-package-guide/tutorials/get-to-know-hatch.html#install-hatch) alongside uv.

Hatch scripts automate the test workflows. 🚀

To run tests, there is a single hatch environment that can be used with one of three
script options.

1. To run only tests with a code coverage report out in the terminal, use:

   `hatch run test:run-coverage`

2. To run tests without code coverage reports, use:
   `hatch run test:run-no-cov`

3. To run tests with an XML report generated, use:
   `hatch run test:run-report`

   The `run-report` script is the one used in the CI test action.

When you run a Hatch command, Hatch will search for an existing environment. If it doesn't exist, it will create it using the instructions provided in the `pyproject.toml` file. It will automatically install pyosMeta in development mode in that environment.

### Modify test scripts

If you need to modify or update test scripts, go to the `[tool.hatch.envs.test.scripts]` table in the `pyproject.toml` file to see the available scripts and their definitions.

```toml
[tool.hatch.envs.test.scripts]
run-coverage = "pytest --cov-config=pyproject.toml --cov=pyosmeta --cov=tests/*"
run-no-cov = "run-coverage --no-cov"
run-report = "run-coverage --cov-report=xml:coverage.xml"
```

## pyosMeta build

pyosMeta uses `hatchling` as its build backend.

### Build a local package

To build the package locally and create a local `sdist` and `wheel`, run:

`hatch build`

### Package versioning

pyosMeta uses `hatch-vcs`, which uses `setuptools_scm` under the hood to track versions. `hatch-vcs`
uses the most current git tag in the repository to determine what version of the package is being built. This means that if you try to build the package locally and haven't fetched all tags, it could create a dated version of the package (locally)!
Under the hood, `hatch-vcs` generates a `_version_generated.py` file when it builds using the latest tag.

The `_version_generated.py` file should NEVER
be committed to version control. It should be ignored via the `.gitignore` file.

When you run `hatch build`, Hatch will:

1. Create a `dist` directory with the wheel and the package `sdist` tarball. You can see the version of `pyosMeta` in the name of those files:

```console
dist/
   pyosmeta-1.0.0.post27-py3-non-any.whl
   pyosmeta-1.0.0.post27.tar.gz
```

1. Invoke build to call `setuptools_scm` (via `hatch-vcs`) to create a `_version_generated.py` file in the pyosMeta package directory:

```console
pyosmeta/
    pyosmeta/
        _version_generated.py
```

The release workflow is automated and can be triggered and run using the
GitHub.com interface.

pyosMeta's release workflow follows [semantic versioning](https://semver.org/) best practices:

- MAJOR version when you make incompatible API changes
- MINOR version when you add functionality in a backward-compatible manner
- PATCH version when you make backward-compatible bug fixes

### How to make a release to PyPI

```{note}
The build workflow explained below will run on every merge to the main branch of pyosMeta to ensure that the distribution files are still valid.
```

To make a release:

- ✔️ 1. Determine with the other maintainers what release version you are moving to.
- ✔️ 2. Create a new **pull request** that does the following:

  - Organizes the `CHANGELOG.md` unreleased items into added, fixed, and changed sections
  - Lists contributors to this release using GitHub handles
  - Adds the version number of that specific release.

Below is an example of the changelog changes made when
pyosMeta was bumped to version 1.0.

```text
## Unreleased

## [v1.4] - 2024-11-22

* Fix: Parse archive and JOSS links to handle markdown links and validate DOI links are valid. Added python-doi as a dependency to ensure archive/DOI URLs fully resolve (@banesullivan)

### Added

* Add: new repos to track contribs (@lwasser)

### Fixed

* Fix: EiC field not processing correctly  (@lwasser, #234)
* Fix: Updated documentation throughout with a focus on how a user's name is accessed and updated (@lwasser)
* Fix: ReviewUser object name can be optional. There are times when we don't have the actual person's name only the GH username (@lwasser)

### Contributors to this release
@banesullivan, @lwasser

```

- ✔️ 3. Once another maintainer approves the pull request (if that is needed), you can merge it.

You are now ready to make the actual release.

- ✔️ 4. In GitHub.com go to `Releases` and prepare a new release. When you create that release you can specify the tag for this release.

Use `v` in the tag number to maintain consistency with previous releases.

This is the ONLY manual step in the release workflow. Be sure to create the correct tag number: example `v1.0.1` for a patch version.

Copy the updated changelog information into the release body or use the <kbd>Generate Release Notes</kbd> button to generate release notes automatically.

- ✔️ 5. Hit `Publish release`

When you publish the release, a GitHub action will be enabled that builds the wheel and SDist.

![Animated gif showing what the publish to pypi release workflow looks like](images/release.gif)

- ✔️ 6. Authorize the deploy step of the build: The final step is to authorize the deployment to PyPI. pyosMeta's build uses a GitHub environment called `PyPI` that is connected to the pyosMeta PyPI account using PyPI's trusted publisher workflow. Only the core maintenance team can authorize an action to run using this environment.

![Once you have created a release, as a maintainer, you can approve the automated deployment process for `pyosMeta` by going to the actions tab and clicking on the current publish-pypi.yml workflow run.](/images/release-deploy.gif)

Congratulations! You've just created a pyosMeta release.
