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

This project provides a configuration system that supplies configuration options to a command-line interface (CLI) tool from multiple sources.

### Configuration Sources

The configuration system reads options from multiple files located in different directories.
By default the configuration system searches for files named `edq-config.json`, this can be customizable.
For this documentation, the default file name (`edq-config.json`) is used.
Specify a different file name when calling the configuration system to change the default.

If the same configuration option is set in more than one place, the value from the later source overrides the earlier ones.
The table below shows the order in which sources are applied, from top to bottom.

| Sources | Description |
| :------:| :---------- |
| Global | Global config file defaults to a platform-specific user location and can be changed with the `--global-config` option.|
| Local | Local configuration is loaded from the first matching file found, starting in the current directory and moving up to ancestor directories.|
| CLI | Files passed with `--config-file` are loaded in order, with later files overriding earlier ones.|
| CLI Bear | Command-line options override all other configuration sources.|

The system produces an error if a global or local config file is unreadable (but not missing), or if a CLI-specified file is unreadable or missing.

#### Global Configuration

The global config file defaults to `<platform-specific user config location>/edq-config.json`.
According to [platformdirs](https://github.com/tox-dev/platformdirs), this location serves as the proper place to store user-related configuration.
You can change the global config location by passing a path to `--global-config` to the command line.
This type of config is best suited for login credentials or persistent user preferences.
Run any CLI tool with `--help` to see the exact path for the current platform under the flag `--global-config`.

#### Local Configuration

Local configuration files exist in different locations.
The first file found will be used, and other locations will not be searched.
Local config search order:
1. `edq-config.json` in the current directory.
2. A legacy file in the current directory (only if a specified legacy file is passed to the config system).
3. `edq-config.json` in any ancestor directory on the path to root (or up to a cutoff limit, if specified to the config system).

#### CLI-Specified Config Files

Any files passed via `--config-file` will be loaded in the order they appear on the command line.
Later files will override options from previous ones.

#### Bare CLI Options

Options passed directly on the command line (e.g., `--user`, `--token`, `--server`).
These always override every other configuration source.
The configuration system can be set to ignore specific CLI options when applying overrides, if needed.