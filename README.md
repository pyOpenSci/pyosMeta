# update-web-metadata

A repo with code to update contributor and package metadata on the website

Create envt
`mamba env create -f environment.yml`

```
❯ hatch new pyosMeta2
pyosmeta2
├── pyosmeta2
│   ├── __about__.py
│   └── __init__.py
├── tests
│   └── __init__.py
├── LICENSE.txt
├── README.md
└── pyproject.toml
```

Hatch also seems to create an init and a about that has a standard version.

# How do i use Hatch with a conda environment?

looks like i have to install a plugin for this... wondering if i want to go with PDM for now? Or Poetry?
