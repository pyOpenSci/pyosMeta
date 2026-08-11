# Contributing

Thanks for your interest in contributing to pyosMeta. We welcome issues, pull
requests, documentation improvements, and questions.

## Code of conduct

Everyone participating in pyOpenSci projects is expected to follow the
[pyOpenSci Code of Conduct](https://www.pyopensci.org/handbook/CODE_OF_CONDUCT.html).

## How to contribute

1. Open an issue to discuss a bug or idea (optional for small docs fixes).
2. Fork the repo and create a branch from `main`.
3. Set up a local environment using the [Development Guide](./development.md).
4. Make your changes, add or update tests when behavior changes, and run:

   ```console
   hatch run test:run-no-cov
   ```

5. Update [CHANGELOG.md](./CHANGELOG.md) under **Unreleased** when you change
   package behavior or public docs that users rely on.
6. Open a pull request with a clear description of the change and why.

## Where to look for more detail

| Doc | What’s in it |
|---|---|
| [README.md](./README.md) | What pyosmeta is and how the metadata workflow fits the website |
| [development.md](./development.md) | Local setup, running CLIs, tests, build, and release |
| [CHANGELOG.md](./CHANGELOG.md) | Release history |

## Questions

If you’re unsure where something belongs or how to test a change, open an issue
or ask in the PR — we’re happy to help.
