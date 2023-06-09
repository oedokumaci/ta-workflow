<div align="center">

This is a CLI tool that helps me manage my TA duties. Feel free to use it for your own TAing purposes.

![Tests](https://github.com/oedokumaci/ta-workflow/actions/workflows/tests.yml/badge.svg)
![Quality](https://github.com/oedokumaci/ta-workflow/actions/workflows/quality.yml/badge.svg)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

&nbsp;

# User Guide

## Requirements

- Python >= 3.10
- OS: Ubuntu, MacOS, Windows

## Installation

Pip installing the package from PyPI is not yet available. Instead, download [from this link](https://github.com/oedokumaci/ta-workflow/archive/refs/heads/main.zip) and unzip. You will also need to change the folder name from ta-workflow-main to ta-workflow (or cd into ta-workflow-main in step 2 below). Alternatively, if you have git installed, simply run 
```bash
git clone https://github.com/oedokumaci/ta-workflow
```
to install the package locally. After downloading, here are the steps to install the dependencies in a virtual environment using [PDM]:

1. `pip install pdm`
2. `cd ta-workflow`
3. `pdm install --prod`

## Usage

### Configuration

First edit the `./config/config.yaml` to your liking. Example config file can be found at `./config/example_config.yaml`.

### Quick Start

After configuring the `./config/config.yaml`, simply run the following command in the project directory.
```bash
pdm run python -m ta_workflow
```

### Detailed Usage
For a list of all the CLI arguments and options, run
```bash
pdm run python -m ta_workflow --help
```

Here is a screenshot of the help message.

<img src=./style/cli.png width="800">

&nbsp;

# Developer Guide

## Makefile
There is a Makefile in the project directory. You can run `make help` to see the available commands as below. The Makefile is also used in the CI/CD pipeline.

<img src=./style/make.png width="600">

## Setup

This project is [PDM]-managed, which is compatible with [PEP 621](https://www.python.org/dev/peps/pep-0621) (also compatible with the <i>rejected</i> [PEP 582](https://www.python.org/dev/peps/pep-0582)). If you are a developer, first `pip install pdm` and then `git clone` the project. Next you can `pdm install` in the project directory, which will install all the dependencies in a [virtual environment](https://pdm.fming.dev/latest/usage/venv/).

## Development

### Pre-commit Hooks

The project also uses pre-commit hooks. Because the project uses [PDM], you **do not** need to `pip install pre-commit`. Instead, run directly
```bash
pdm run pre-commit install
```
in the project directory to install hooks to your local `.git`. Alternatively, you can also activate the virtual environment and run
```bash
pre-commit install
```

[PDM]: https://pdm.fming.dev
