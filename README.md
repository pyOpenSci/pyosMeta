# pyosmeta

[![PyPI](https://img.shields.io/pypi/v/pyosmeta.svg)](https://pypi.org/project/pyosmeta/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/pyopensci/update-web-metadata/blob/master/LICENSE)
[![CITE DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13159326.svg)](https://doi.org/10.5281/zenodo.13159326)

<!--- Tests, Coverage, and CI badges -->
[![Run pyos meta tests](https://github.com/pyOpenSci/pyosMeta/actions/workflows/run-tests.yml/badge.svg)](https://github.com/pyOpenSci/pyosMeta/actions/workflows/run-tests.yml)
[![codecov](https://codecov.io/gh/pyOpenSci/pyosMeta/graph/badge.svg?token=GOXKA8Z44X)](https://codecov.io/gh/pyOpenSci/pyosMeta)
[![Update Contribs & reviewers](https://github.com/pyOpenSci/pyosMeta/actions/workflows/test-update-contribs.yml/badge.svg)](https://github.com/pyOpenSci/pyosMeta/actions/workflows/test-update-contribs.yml)
[![Publish to PyPI](https://github.com/pyOpenSci/pyosMeta/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/pyOpenSci/pyosMeta/actions/workflows/publish-pypi.yml)
[![.github/workflows/test-run-script.yml](https://github.com/pyOpenSci/pyosMeta/actions/workflows/test-run-script.yml/badge.svg)](https://github.com/pyOpenSci/pyosMeta/actions/workflows/test-run-script.yml)

## Description

**pyosmeta** provides the tools and scripts used to manage [pyOpenSci](https://pyopensci.org)'s contributor and peer
review metadata.
This repo contains several modules and several CLI scripts, including:

- `parse-history`
- `update-contributors`
- `update-reviews`
- `update-review-teams`

_Since pyOpenSci uses this tool for its website, we expect this package to have infrequent releases._

## Installation

Using pip:

```console
pip install pyosmeta
```

Using conda:

```console
conda install pyosmeta
```

## Usage

See [CONTRIBUTING.md](./CONTRIBUTING.md).

This repo contains several modules and several CLI scripts, including:

- `parse-history`
  - This script:
    1. gets a list of all contributors
    2. parses through the commit history (locally) to figure out when they were added to the contributor.yml file
    3. then it adds a date_Added key for that person
      This will allow us to ensure the yaml file retains order when users are
      highlighted as "new" and also for diff's in git.
- `update-contributors`
  - This script parses through and updates the existing contributor list stored in pyopensci.github.io repo in the _data/contributors.yml file.
  - That's used to populate the [community page](https://www.pyopensci.org/our-community/), and to update our [metrics page](https://www.pyopensci.org/metrics/).
- `update-reviews`
  - This script parses metadata from and issue and adds it to a .yml file for the website. It also grabs some of the package metadata such as stars, last commit, etc.
  - It outputs a `packages.yml` file with all packages with accepted reviews; information related to the review; basic package stats; and partner information.
- `update-review-teams`
  - This script parses through our packages.yml and contributors.yml.
  - It:
    1. Updates reviewer, editor and maintainer data in the contributor.yml file to ensure all packages they supported are listed there.
    1b: And that they have a listing as peer-review under contributor type
    2. Finally it looks to see if we are missing review participants from the review issues in the contributor file and updates that file.
  - **Warning**: This script assumes that update_contributors and update_reviews has been run. Rather than hit any api's it just updates information from the issues.

_Note: this section will be rewritten to be more user focused._

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/xmnlab"><img src="https://avatars.githubusercontent.com/u/5209757?v=4?s=100" width="100px;" alt="Ivan Ogasawara"/><br /><sub><b>Ivan Ogasawara</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=xmnlab" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Axmnlab" title="Reviewed Pull Requests">👀</a> <a href="#design-xmnlab" title="Design">🎨</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/meerkatters"><img src="https://avatars.githubusercontent.com/u/50787305?v=4?s=100" width="100px;" alt="Meer (Miriam) Williamson"/><br /><sub><b>Meer (Miriam) Williamson</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=meerkatters" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Ameerkatters" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://tiffanyxiao.com/"><img src="https://avatars.githubusercontent.com/u/13580331?v=4?s=100" width="100px;" alt="Tiffany Xiao"/><br /><sub><b>Tiffany Xiao</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=tiffanyxiao" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Atiffanyxiao" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/austinlg96"><img src="https://avatars.githubusercontent.com/u/19922895?v=4?s=100" width="100px;" alt="austinlg96"/><br /><sub><b>austinlg96</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=austinlg96" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Aaustinlg96" title="Reviewed Pull Requests">👀</a> <a href="#design-austinlg96" title="Design">🎨</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/paajake"><img src="https://avatars.githubusercontent.com/u/12656820?v=4?s=100" width="100px;" alt="JAKE"/><br /><sub><b>JAKE</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Apaajake" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/pyOpenSci/pyosMeta/commits?author=paajake" title="Code">💻</a> <a href="#design-paajake" title="Design">🎨</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://luizirber.org"><img src="https://avatars.githubusercontent.com/u/6642?v=4?s=100" width="100px;" alt="Luiz Irber"/><br /><sub><b>Luiz Irber</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=luizirber" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Aluizirber" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bbulpett"><img src="https://avatars.githubusercontent.com/u/6424805?v=4?s=100" width="100px;" alt="Barnabas Bulpett (He/Him)"/><br /><sub><b>Barnabas Bulpett (He/Him)</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=bbulpett" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Abbulpett" title="Reviewed Pull Requests">👀</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/juanis2112"><img src="https://avatars.githubusercontent.com/u/18587879?v=4?s=100" width="100px;" alt="Juanita Gomez"/><br /><sub><b>Juanita Gomez</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=juanis2112" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Ajuanis2112" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.sckaiser.com"><img src="https://avatars.githubusercontent.com/u/6486256?v=4?s=100" width="100px;" alt="Sarah Kaiser"/><br /><sub><b>Sarah Kaiser</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=crazy4pi314" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Acrazy4pi314" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://econpoint.com"><img src="https://avatars.githubusercontent.com/u/20208402?v=4?s=100" width="100px;" alt="Sultan Orazbayev"/><br /><sub><b>Sultan Orazbayev</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=SultanOrazbayev" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3ASultanOrazbayev" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://ml-gis-service.com"><img src="https://avatars.githubusercontent.com/u/31246246?v=4?s=100" width="100px;" alt="Simon"/><br /><sub><b>Simon</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=SimonMolinsky" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3ASimonMolinsky" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://hachyderm.io/web/@willingc"><img src="https://avatars.githubusercontent.com/u/2680980?v=4?s=100" width="100px;" alt="Carol Willing"/><br /><sub><b>Carol Willing</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=willingc" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Awillingc" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://ofek.dev"><img src="https://avatars.githubusercontent.com/u/9677399?v=4?s=100" width="100px;" alt="Ofek Lev"/><br /><sub><b>Ofek Lev</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=ofek" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Aofek" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://webknjaz.me"><img src="https://avatars.githubusercontent.com/u/578543?v=4?s=100" width="100px;" alt="Sviatoslav Sydorenko (Святослав Сидоренко)"/><br /><sub><b>Sviatoslav Sydorenko (Святослав Сидоренко)</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=webknjaz" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Awebknjaz" title="Reviewed Pull Requests">👀</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://www.linkedin.com/in/steven-silvester-90318721/"><img src="https://avatars.githubusercontent.com/u/2096628?v=4?s=100" width="100px;" alt="Steven Silvester"/><br /><sub><b>Steven Silvester</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=blink1073" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Ablink1073" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.linkedin.com/in/pllim/"><img src="https://avatars.githubusercontent.com/u/2090236?v=4?s=100" width="100px;" alt="P. L. Lim"/><br /><sub><b>P. L. Lim</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=pllim" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Apllim" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.uaw4811.org/2024-ulp-charges"><img src="https://avatars.githubusercontent.com/u/12961499?v=4?s=100" width="100px;" alt="Jonny Saunders"/><br /><sub><b>Jonny Saunders</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=sneakers-the-rat" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Asneakers-the-rat" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ehinman"><img src="https://avatars.githubusercontent.com/u/121896266?v=4?s=100" width="100px;" alt="Elise Hinman"/><br /><sub><b>Elise Hinman</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=ehinman" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Aehinman" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/hariprakash619"><img src="https://avatars.githubusercontent.com/u/14228793?v=4?s=100" width="100px;" alt="Hari Prakash Vel Murugan"/><br /><sub><b>Hari Prakash Vel Murugan</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=hariprakash619" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mrgah"><img src="https://avatars.githubusercontent.com/u/11444003?v=4?s=100" width="100px;" alt="mrgah"/><br /><sub><b>mrgah</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=mrgah" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Amrgah" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/klmcadams"><img src="https://avatars.githubusercontent.com/u/58492561?v=4?s=100" width="100px;" alt="Kerry McAdams"/><br /><sub><b>Kerry McAdams</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=klmcadams" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Aklmcadams" title="Reviewed Pull Requests">👀</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/chenghlee"><img src="https://avatars.githubusercontent.com/u/3485949?v=4?s=100" width="100px;" alt="Cheng H. Lee"/><br /><sub><b>Cheng H. Lee</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Achenghlee" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/stevenrayhinojosa-gmail-com"><img src="https://avatars.githubusercontent.com/u/17886818?v=4?s=100" width="100px;" alt="steven"/><br /><sub><b>steven</b></sub></a><br /><a href="https://github.com/pyOpenSci/pyosMeta/commits?author=stevenrayhinojosa-gmail-com" title="Code">💻</a> <a href="https://github.com/pyOpenSci/pyosMeta/pulls?q=is%3Apr+reviewed-by%3Astevenrayhinojosa-gmail-com" title="Reviewed Pull Requests">👀</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification.
Contributions of any kind welcome!

## Contributing

[CONTRIBUTING.md](./CONTRIBUTING.md)

## Development

[Development guide](./development.md)

## Change log

[CHANGELOG.md](./CHANGELOG.md)

## Code of Conduct

Everyone interacting in the pyOpenSci project's codebases, issue trackers, chat rooms, and communication venues is
expected to follow the [pyOpenSci Code of Conduct](https://www.pyopensci.org/handbook/CODE_OF_CONDUCT.html).

## License

[MIT License](./LICENSE)
