# pyosmeta Changelog

[![PyPI](https://img.shields.io/pypi/v/pyosmeta.svg)](https://pypi.org/project/pyosmeta/)

## [Unreleased]
- Parse up to 100 issues in a request (@lwasser, #94)


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

[Unreleased]: https://github.com/pyopensci/pyosmeta/compare/v0.2.3...HEAD
[v0.2.3]: https://github.com/pyopensci/pyosmeta/compare/v0.15...v0.2.3
[v0.2.2]: https://github.com/pyopensci/pyosmeta/compare/v0.15...v0.2.2
[v0.15]: https://github.com/pyOpenSci/pyosMeta/releases/tag/v0.15
[v.0.2]: https://pypi.org/project/pyosmeta/0.2/
