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

## Configuration System

This project provides a configuration system that supplies configuration options to a command line interface (CLI) tool.
The configuration file is named `edq-config.json` by default. Specify a different file name when calling the configuration system to change it.
For this documentation, the default file name (`edq-config.json`) is used.

### Configuration Sources

Configuration options can come from several places. Later sources overwrite earlier ones. The table below explains the sources:

| Sources | Description |
| :-------: | :----------- |
| Global | The default global configuration file, `edq-config.json`, lives in the platform-specific user configuration directory, as recommended by [platformdirs](https://github.com/tox-dev/platformdirs). Use the `--global-config` option to change its location.|
| Local | The search stops when it finds a match. The system resolves local config in this order: `edq-config.json` in the current directory, a supported legacy file in the current directory, then the nearest ancestor `edq-config.json`.|
| CLI | When multiple config files are passed with `--config-file`, the system loads them sequentially. Options in later files override those in earlier ones.|
| CLI Bear | Command-line options (e.g., `--user`, `--token`, `--server`) override all other configuration sources unless specific keys are configured to be ignored.|

#### Global Configuration

The global config file defaults to `<platform-specific user config location>/edq-config.json`.
According to [platformdirs](https://github.com/tox-dev/platformdirs), this location serves as the proper place to store user-related configuration.
You can change the global config location by passing a path to `--global-config` in the command line.
This type of config is best suited for login credentials or persistent user preferences.
Run any CLI tool with `--help` to see the exact path for your platform.

#### Local Configuration

Local configuration files exist in different locations.
The first file found will be used, and other locations will not be searched.
Local config search order:
1. `edq-config.json` in the current directory.
2. A legacy file in the current directory (only if the config system supports a specified legacy file).
3. `edq-config.json` in any ancestor directory on the path to root (or up to a cutoff limit, if specified in the config system).

#### CLI-Specified Config Files

Any files passed via `--config-file` will be loaded in the order they appear on the command line.
Later files will override options from previous ones.

#### Bare CLI Options

Options passed directly on the command line (e.g., `--user`, `--token`, `--server`).
These always override every other configuration source.
The configuration system can be set to ignore specific CLI keys when applying overrides, if needed.