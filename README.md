# EduLinq Python Utilities

Common utilities used by EduLinq Python projects.

## Installation / Requirements

This project requires [Python](https://www.python.org/) >= 3.8.

The project can be installed from PyPi with:
```
pip3 install edq-utils
```

Standard Python requirements are listed in `pyproject.toml`.
The project and Python dependencies can be installed from source with:
```
pip3 install .
```

## Configuration

Many EduLinq tools share a common configuration system.
This system provides a consistent way to supply options to the CLI tool being used.
While each CLI tool may require additional options, the configuration loading process is the same across the EduLinq ecosystem.

By default, the config file is named `edq-config.json`.
This is customizable and may differ depending on the tool being used.

For the purposes of this documentation we are going to use the default config file name.

### Configuration Sources

Configuration options can come from several places, with later sources overwriting earlier ones:

#### Global Configuration

The default place a global config is looked for is `<platform-specific user config location>/edq-config.json`.
This is considered to be the "proper" place to store user-related configuration, according to [platformdirs](https://github.com/tox-dev/platformdir).
The location where a global config will be looked for can be changed by passing a path to --global-config trough the command line.
This type of config is best suited for login credentials or persistent user preferences.
Run any CLI tool with `--help` to see the exact path on your platform.

#### Local Configuration

If an `edq-config.json` exists in the current working directory, it will be loaded.

Local configuration files can be found in different locations.
The first file found will be used, and other locations will not be searched.

##### Search order for a local config file:

1. `./edq-config.json`
2. `./legacy-config.json`
   *(applies only if the config system is set to support a custome legacy file name)*
3. An `edq-config.json` file located in any ancestor directory on the path to root (or up to a cutoff limit if one is specified).

#### CLI-Specified Config Files

Any files passed via `--config` will be loaded in the order they appear on the command line.
Latter files will override options from previous ones.

#### Bare CLI Options

Options passed directly on the command line (e.g., `--user`, `--token`, `--server`).
These always override every other configuration source.
