# Development Guide

## Packaging

pyosMeta uses hatch and hatchling as it's build back end.

## Running tests

We use Hatch scripts to automate workflows. 🚀

To run tests there is a single hatch environment parsed with three
script options that you can chose to run.

1. To run only tests with a code coverage report out in the terminal use:

   `hatch run test:run-coverage`

2. To run tests without code coverage report outs use :
   `hatch run test:run-coverage`

3. To run tests with an xml report generated use:
   `hatch run test:run-report`

   The hatch run-report script is the script used in our CI tests action.

### Modify test scripts

To modify how scripts ar run, you can look at this section in our
pyproject.toml file:

```toml
[tool.hatch.envs.test.scripts]
run-coverage = "pytest --cov-config=pyproject.toml --cov=pyosmeta --cov=tests/*"
run-no-cov = "run-coverage --no-cov"
run-report = "run-coverage --cov-report=xml:coverage.xml"
```
