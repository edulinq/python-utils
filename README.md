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

This project provides a configuration system that supplies options (e.g., user name, password) to a command-line interface ([CLI](https://en.wikipedia.org/wiki/Command-line_interface)) tool.
The configuration system follows a tiered order, allowing options to be specified and overridden from both files and command-line options.

### Configuration Sources

In addition to CLI options, the configuration system loads options from [JSON](https://en.wikipedia.org/wiki/JSON) files located across multiple directories.
By default, config files are named `edq-config.json`.
This value is customizable, but this document will assume the default is used.

For example, a configuration file containing the `user` and `token` options might look like this:
```
{
    "user": "edq-user",
    "token": "1234567890"
}
```

The table below lists the configuration sources in the order they are evaluated.
All sources are processed in the order shown in the table: if an option appears only in one source, it is included as is.
If the same option appears in multiple sources, the value from the later source in the table overrides the earlier one.

| Source   | Description |
| :-----:  | :---------- |
| Global   | Global configuration file defaults to a platform-specific user location and can be changed with the `--global-config` option. |
| Local    | Local configuration is loaded from the first matching file found, starting in the current directory and moving up to ancestor directories until root. |
| CLI File | Files passed with `--config-file` are loaded in order, with later files overriding earlier ones. |
| CLI      | Command-line options override all other configuration sources. |

The system produces an error if a global or local configuration file is unreadable (but not missing), or if a CLI-specified file is unreadable or missing.

#### Global Configuration

The global configuration file defaults to `<platform-specific user configuration location>/edq-config.json`.
The configuration location is chosen according to the [XDG standard](https://en.wikipedia.org/wiki/Freedesktop.org#Base_Directory_Specification) (implemented by [platformdirs](https://github.com/tox-dev/platformdirs)).
The global configuration location can be changed by passing a path to `--global-config` to the command line.
This type of configuration is best suited for login credentials or persistent user preferences.
Run any CLI command with `--help` to see the exact path for the current platform under the flag `--global-config`.

#### Local Configuration

Local configuration files are searched in multiple locations, the first file found is used.
The Local config search order is:
1. `edq-config.json` in the current directory.
2. A legacy file in the current directory (only if a legacy file is preconfigured).
3. `edq-config.json` in any ancestor directory on the path to root .

#### CLI-Specified Config Files

Any files passed via `--config-file` will be loaded in the order they appear on the command line.
Later files will override options from previous ones.

Below is an example of a CLI specified configuration path:
```
python3 -m edq.cli.config.list --config-file <file-name>.json --config-file ~/.secrets/<file-name>.json
```

#### Bare CLI Options

Options passed directly on the command line (e.g., `--user`, `--token`, `--server`).
These always override every other configuration source.

Below is an example of specifying a config option directly from the CLI:
```
python3 -m edq.cli.config.list --user=edq-user --token=12345
```