# pyosmeta Changelog

[![PyPI](https://img.shields.io/pypi/v/pyosmeta.svg)](https://pypi.org/project/pyosmeta/)

See [GitHub releases](https://github.com/pyOpenSci/pyosMeta/releases) page for additional information.

## [Unreleased]

## [v1.7.3] - 2025-08-07

* Fix: gracefully fail when collecting repository metrics outside of GitHub (@banesullivan, #300)

### Contributors to this release ✨

@banesullivan

## [v1.7.2] - 2025-05-20

* Fix: support multiple editors and EiCs (@banesullivan, #290)
* Fix: bug in contributor collection, incorrect repo names (@lwasser, #296)

### Contributors to this release ✨

@banesullivan, @lwasser

## [v1.7.1] - 2025-05-20

* Fix: remove sigstore from pypi publish workflow (@lwasser, #286)

## [v1.7] - 2025-05-19

### Added

* Added `tqdm` as a dependency to improve progress monitoring when running data processing scripts (@banesullivan)
* Test missing community partnerships section (@banesullivan, #268)
* enh: use graphql to consolidate api calls by (@lwasser, #267)
* Consistent logging by @banesullivan in <https://github.com/pyOpenSci/pyosMeta/pull/270>
* enh(ci): Add zizmor to `pre-commit-config.yaml` (@klmcadams, #283)
* enh(docs): Docstrings to docs (@mrgah, #281)

### Fixed

* Use a consistent logger for informational/debug outputs. Using print statements can make it tough to track down which line of code emitted the message and using the `warnings` module will suppress recurring warnings (@banesullivan)
* Fix: update deprecated sigstore action by (@lwasser, #265)
* Remove duplicate "Add help-wanted issues to help wanted board" job by (@banesullivan, #269)
* Update reviews script fail on error (@banesullivan, #272)
* Only use pre-commit ci autofix on automated PRs (@banesullivan, #275)
* enh(docs): update pyosmeta release workflow docs (@lwasser, #278)

### Thank you!! New Contributors to this release ✨

@klmcadams, @mrgah

## [v1.6] - 2025-02-17

### What's Changed

* [hotfix] handle packages that lack a description on GitHub by @banesullivan in <https://github.com/pyOpenSci/pyosMeta/pull/257>
* In CONTRIBUTING.md, add more specifics on configuring API token #194 by @hariprakash619 in <https://github.com/pyOpenSci/pyosMeta/pull/255>
* docs: add hariprakash619 as a contributor for doc by @allcontributors in <https://github.com/pyOpenSci/pyosMeta/pull/256>
* Reorder badges and add more CI badges in README by @willingc in <https://github.com/pyOpenSci/pyosMeta/pull/258>
* Update CHANGELOG.md for 1.6 by @willingc in <https://github.com/pyOpenSci/pyosMeta/pull/260>
* Update contributor and review data by @github-actions in <https://github.com/pyOpenSci/pyosMeta/pull/251>
* Update contributor and review data by @github-actions in <https://github.com/pyOpenSci/pyosMeta/pull/253>
* Update contributor and review data by @github-actions in <https://github.com/pyOpenSci/pyosMeta/pull/262>

### New Contributors

* @hariprakash619 made their first contribution in <https://github.com/pyOpenSci/pyosMeta/pull/255>

## [v1.5] - 2025-01-14

* Fix: Parse archive and JOSS links to handle markdown links and validate DOI links are valid. Added python-doi as a dependency to ensure archive/DOI URLs fully resolve (@banesullivan)
* Add: new `active` status under `ReviewModel` which is set to `False` if the `"archived"` label is present on a review to mark the package as inactive (@banesullivan)

## [v1.4] - 2024-11-22

* Fix: Parse archive and JOSS links to handle markdown links and validate DOI links are valid. Added python-doi as a dependency to ensure archive/DOI URLs fully resolve (@banesullivan)

Notes: it looks like i may have mistakenly bumped to 1.3.7 in august. rather than try to fix on pypi we will just go with it to ensure our release cycles are smooth given no one else uses this package except pyopensci.

### Added

* Add: new repos to track contribs (@lwasser)

### Fixed

* Fix: Eix field not processing correctly  (@lwasser, #234)
* Fix: Updated documentation throughout with a focus on how a user's name is accessed and updated (@lwasser)
* Fix: ReviewUser object name can be optional. There are times when we don't have the actual person's name only the GH username (@lwasser)

## [v1.3.7] - 2024-08-27

* Add: after-date to api call and return clearer 401 message when token needs a refresh. (@lwasser)

## [v0.3.6] - 2024-08-15

* Add: pyos Repos that contributors contribute to  (@lwasser, #197)

## [v0.3.5] - 2024-08-15

This is a tiny release to add support for pr and issue aggregation in our metrics.

### Add

* Add: Endpoint variable to support both prs and issues to GitHubAPI (@lwasser)
* Add: Tests for the contributors module & file_io (@willingc)

## [v0.3.4] - 2024-08-01

### Fixes

* Fix: Edit .env-default file to correct syntax (@ehinman, #196)
* Fix: Update api endpoint test to check for any valid endpoint (@willingc, #199)
* Fix: emeritus and advisory roles default to false + bug fix (@lwasser, #200, #202)
* Fix: allow for issues with multiple labels & fix presubmission ingest (@lwasser)
* Fix: move to BSD-3 license so pyOS aligns with project Jupyter (@lwasser)

### :sparkles: Thank you to the new contributors in this release :sparkles:

@ehinman

## [v0.3.2] - 2024-07-04

### Fixes

* Fix parsing of partnerships by (@sneakers-the-rat, #187)
* Get labels from issue metadata (@sneakers-the-rat, #189)

## [v0.3.1] - 2024-07-04

* Add: add emeritus_editor to personModel (@lwasser, #182)

## [v0.3] - 2024-07-04

This is a bump that supports a big refactor to make our code more maintainable. Many thanks to @sneakers-the-rat. It also
makes our CI more robust thanks to (@blink1073)

### What's Changed

* Fix: Refactor of the API specifically updating the issue parser to make it more maintainable (@sneakers-the-rat, #174)
* Fix: fix sigstore release build (@blink1073, #175)

## [v0.2.6] - 2024-07-02

This is a small patch that fixes a bug in the code discovered by @pllim and adds ruff thanks to @blink1073

### What's Changed

* Adopt ruff by @blink1073 in <https://github.com/pyOpenSci/pyosMeta/pull/164>
* Fix undeclared fix_indent by @pllim in <https://github.com/pyOpenSci/pyosMeta/pull/166>
* Test cli on pull requests by @blink1073 in <https://github.com/pyOpenSci/pyosMeta/pull/170>

### New Contributors

* @pllim made their first contribution in <https://github.com/pyOpenSci/pyosMeta/pull/166>

**Full Changelog**: <https://github.com/pyOpenSci/pyosMeta/compare/v0.2.5...v0.2.6>

## [v0.2.5] - 2024-06-10

* Fix: bug where if a github username has a name after it returns a invalid cleaned github username (@lwasser)

## [v0.2.4] - 2024-03-29

### Added

* Add support for partners and emeritus_editor in contributor model (@lwasser, #133)
* Add support for pagination in github issue requests  (@lwasser, #139)
* Add tests for all utils functions (@lwasser, #122)

### Changed

#### Bug Fixes

* Fix: Bug where date_accepted is removed (@lwasser, #129)

#### Refactor

* Fix: Parse up to 100 issues in a request (@lwasser, #94)
* Fix: refactor parse issue header (@lwasser, #91)
* Fix: Refactor and organize modules (@lwasser, #76)
* Fix: Rename and organize `clean.py` module into `utils_parse` and `utils_clean` (@lwasser, @willingc, #121)
* Fix: Refactor all issue related GitHub methods to gh_client module (@lwasser, #125)
* Fix: Refactor all contributor GitHub related methods into gh_client module from contributors module (@lwasser, #125)

#### CI

* Update ci workflow versions (@willingc, #113)
* Separate build from publish steps for added security in pypi publish workflow (@lwasser, #113)

## [v0.2.3] - 2024-02-29

This version adds automation of our workflows, including using `hatch`
for builds, automated GitHub actions for linting and testing, coverage reporting, and
dynamic versioning. This release adds basic functionality for Partner support.

### Added

* Use `hatch_vcs` for dynamic versioning (@lwasser, #82)
* Partner support to package (#92, @lwasser)
* Code coverage setup (#97, @lwasser)

### Changed

* Migrate to pytest for tests and setup hatch scripts (#89, @lwasser)
* Add validation step to categories attr in pydantic model (#105, @lwasser)
* Update pypi publish to use hatch (#82, @lwasser)
* Move data accepted cleanup to pydantic field alias / validation step (@lwasser)

Thank you to all contributors to this release. Special thanks
to @ofek for assistance with `hatch`, @pradyunsg for packaging guidance, @webknjaz
and @woodruffw for help troubleshooting Trusted Publisher releases to PyPI, and @willingc for guidance in software
development best practices.

## [v0.2.2] - 2024-02-27

This version tested our production release process to PyPI.

## [v0.15] - 2023-12-20

This release was tagged in git and GitHub but not released to PyPI.

## [v.0.2] - 2023-08-17

Initial release to PyPI.

[Unreleased]: https://github.com/pyopensci/pyosmeta/compare/v1.6...HEAD
[v1.6]: https://github.com/pyopensci/pyosmeta/compare/v1.5...v1.6
[v1.5]: https://github.com/pyopensci/pyosmeta/compare/v1.4...v1.5

<!--- Historical versioning: prior to automation -->
[v0.2.4]: https://github.com/pyopensci/pyosmeta/compare/v0.2.3...v0.2.4
[v0.2.3]: https://github.com/pyopensci/pyosmeta/compare/v0.15...v0.2.3
[v0.2.2]: https://github.com/pyopensci/pyosmeta/compare/v0.15...v0.2.2
[v0.15]: https://github.com/pyOpenSci/pyosMeta/releases/tag/v0.15
[v.0.2]: https://pypi.org/project/pyosmeta/0.2/
