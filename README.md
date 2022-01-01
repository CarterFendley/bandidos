# Bandidos

## Setup for development

First clone this repository,

```bash
git clone https://github.com/CarterFendley/bandidos.git
```

Navigate to the cloned repository and install the package via pip in development mode.

```bash
cd bandidos
python3 -m pip install -e .
```

If you make changes to the package (as opposed to the source code) such as adding dependencies in `setup.cfg` you might need to run the following command to use pip to make sure new dependencies are installed.

```bash
python3 -m pip install --upgrade -e .
```