# Development Guide

Developers can use hatch to simplify set up of a pyosMeta development
environment and executing development tasks.

## Setting up a development environment

### Install hatch

1. Follow the [hatch installation instructions](https://hatch.pypa.io/latest/install/#installation).
2. Open a new terminal and run `hatch --version` to verify that `hatch` is available.

### Open a local dev environment using hatch

In a terminal, enter:

`hatch shell`

You will now have an activated virtual environment.

[To learn more about working with Hatch environments, check out this tutorial](https://hatch.pypa.io/dev/tutorials/environment/basic-usage/)
which explains how hatch uses environments.

To deactivate an environment, enter:

`deactivate`

## Running tests

We use Hatch scripts to automate workflows. 🚀

To run tests there is a single hatch environment parsed with three
script options that you can chose to run.

1. To run only tests with a code coverage report out in the terminal use:

   `hatch run test:run-coverage`

2. To run tests without code coverage report outs use:
   `hatch run test:run-no-cov`

3. To run tests with an xml report generated use:
   `hatch run test:run-report`

   The hatch run-report script is the script used in our CI tests action.

### Modify test scripts

To modify how scripts are run, you can look at this section in our
pyproject.toml file:

```toml
[tool.hatch.envs.test.scripts]
run-coverage = "pytest --cov-config=pyproject.toml --cov=pyosmeta --cov=tests/*"
run-no-cov = "run-coverage --no-cov"
run-report = "run-coverage --cov-report=xml:coverage.xml"
```

## Packaging

pyosMeta uses [hatch](https://hatch.pypa.io) and hatchling as its build back end.

### Build a local package

To create a local sdist and wheel, run:

`hatch build`
