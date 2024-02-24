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

[Hatch Environments](https://hatch.pypa.io/latest/environment/#entering-environments) explains
how hatch uses environments.

To deactivate an environment, enter:

`deactivate`

## Running tests

To install tests:

`python -m pip install ".[tests]"`

We use Hatch scripts to automate workflows.

To run tests, you can use:

`hatch run test:run-tests`

## Packaging

pyosMeta uses [hatch](https://hatch.pypa.io) and hatchling as its build back end.

### Build a local package

To create a local sdist and wheel, run:

`hatch build`
