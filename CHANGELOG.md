# pyosmeta Changelog

[![PyPI](https://img.shields.io/pypi/v/pyosmeta.svg)](https://pypi.org/project/pyosmeta/)

## [Unreleased]

## [v0.2.5] - 2024-06-10
- Fix: bug where if a github username has a name after it returns a invalid cleaned github username (@lwasser)

## [v0.2.4] - 2024-03-29

### Added

- Add support for partners and emeritus_editor in contributor model (@lwasser, #133)
- Add support for pagination in github issue requests  (@lwasser, #139)
- Add tests for all utils functions (@lwasser, #122)

### Changed

#### Bug Fixes

- Fix: Bug where date_accepted is removed (@lwasser, #129)

#### Refactor

- Fix: Parse up to 100 issues in a request (@lwasser, #94)
- Fix: refactor parse issue header (@lwasser, #91)
- Fix: Refactor and organize modules (@lwasser, #76)
- Fix: Rename and organize `clean.py` module into `utils_parse` and `utils_clean` (@lwasser, @willingc, #121)
- Fix: Refactor all issue related GitHub methods to gh_client module (@lwasser, #125)
- Fix: Refactor all contributor GitHub related methods into gh_client module from contributors module (@lwasser, #125)

#### CI

- Update ci workflow versions (@willingc, #113)
- Separate build from publish steps for added security in pypi publish workflow (@lwasser, #113)

## [v0.2.3] - 2024-02-29

This version adds automation of our workflows, including using `hatch`
for builds, automated GitHub actions for linting and testing, coverage reporting, and
dynamic versioning. This release adds basic functionality for Partner support.

### Added

- Use `hatch_vcs` for dynamic versioning (@lwasser, #82)
- Partner support to package (#92, @lwasser)
- Code coverage setup (#97, @lwasser)

### Changed

- Migrate to pytest for tests and setup hatch scripts (#89, @lwasser)
- Add validation step to categories attr in pydantic model (#105, @lwasser)
- Update pypi publish to use hatch (#82, @lwasser)
- Move data accepted cleanup to pydantic field alias / validation step (@lwasser)

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

[Unreleased]: https://github.com/pyopensci/pyosmeta/compare/v0.2.4...HEAD
[v0.2.4]: https://github.com/pyopensci/pyosmeta/compare/v0.2.3...v0.2.4
[v0.2.3]: https://github.com/pyopensci/pyosmeta/compare/v0.15...v0.2.3
[v0.2.2]: https://github.com/pyopensci/pyosmeta/compare/v0.15...v0.2.2
[v0.15]: https://github.com/pyOpenSci/pyosMeta/releases/tag/v0.15
[v.0.2]: https://pypi.org/project/pyosmeta/0.2/
