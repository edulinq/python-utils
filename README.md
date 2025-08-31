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

This project provides a configuration system that supplies options (e.g., `user`, `token`) to a command-line interface (CLI) tool.
The configuration system follows a tiered order, incorporating both files and command-line options.

### Configuration Sources

The configuration system loads options from JSON files located across multiple directories.
It searches for these files when invoked, they are not created automatically.
By default, it looks for files named `edq-config.json`, this is customizable.

For example, a configuration file containing the `user` and `token` options might look like this:
```
{
    "user": "edq-user",
    "token": "1234567890"
}
```

The table below lists configuration sources in the order they are evaluated, from the first source at the top row to the last source at the bottom row.
All sources are processed in the order show in the table: if an option appears only in one source, it is included as is.
If the same option appears in multiple sources, the value from the later source in the table overrides the earlier one.

| Sources  | Description |
| :-----:  | :---------- |
| Global   | Global configuration file defaults to a platform-specific user location and can be changed with the `--global-config` option.|
| Local    | Local configuration is loaded from the first matching file found, starting in the current directory and moving up to ancestor directories.|
| CLI      | Files passed with `--config-file` are loaded in order, with later files overriding earlier ones.|
| CLI Bear | Command-line options override all other configuration sources.|

The system produces an error if a global or local configuration file is unreadable (but not missing), or if a CLI-specified file is unreadable or missing.

#### Global Configuration

The global configuration file defaults to `<platform-specific user configuration location>/edq-config.json`.
According to [platformdirs](https://github.com/tox-dev/platformdirs), this location serves as the proper place to store user-related configuration.
The global configuration location is changed by passing a path to `--global-config` to the command line.
This type of configuration is best suited for login credentials or persistent user preferences.
Run any CLI command with `--help` to see the exact path for the current platform under the flag `--global-config`.

Below is an example of specifying a global config path:
```
cli-tool <command> --global-config /path/to/file/<file-name>.json
```

#### Local Configuration

Local configuration files are searched in multiple locations, first file found is used.
Once a file is located, the search for local configuration stops.
Local config search order:
1. `edq-config.json` in the current directory.
2. A legacy file in the current directory (only if a specified legacy file is passed to the configuration system).
3. `edq-config.json` in any ancestor directory on the path to root (or up to a cutoff directory limit, if specified to the configuration system).

#### CLI-Specified Config Files

Any files passed via `--config-file` will be loaded in the order they appear on the command line.
Later files will override options from previous ones.

Below is an example of a CLI specified configuration path:
```
cli-tool <command> --config-file /path/to/file/<file-name>.json
```

#### Bare CLI Options

Options passed directly on the command line (e.g., `--user`, `--token`, `--server`).
These always override every other configuration source.
The configuration system skips specific CLI options when applying overrides if certain keys are passed to it.

Below is an example of specifying a config option directly from the CLI:
```
cli-tool <command> --user=edq-user --token=12345
```