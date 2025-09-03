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
By default, configuration files are named `edq-config.json`.
This value is customizable, but this document will assume the default is used.

For example, a configuration file containing the `user` and `pass` options might look like this:
```
{
    "user": "edq-user",
    "pass": "1234567890"
}
```

The table below lists the configuration sources in the order they are evaluated.
All sources are processed in the order shown in the table. 
The value from the later source in the table overrides the earlier one if there are multiple sources.

| Source   | Description |
| :-----:  | :---------- |
| Global   | The global configuration file path is a platform-specific user location by default. |
| Local    | Local configuration is loaded from the first matching file found, starting in the current directory and moving up to ancestor directories until root. |
| CLI File | Files passed with `--config-file` are loaded in order, with later files overriding earlier ones. |
| CLI      | Command-line options override all other configuration sources. |

The system produces an error if a global or local configuration file is unreadable (but not missing), or if a CLI-specified file is unreadable or missing.

#### Global Configuration

The global configuration file defaults to `<platform-specific user configuration location>/edq-config.json`.
The configuration location is chosen according to the [XDG standard](https://en.wikipedia.org/wiki/Freedesktop.org#Base_Directory_Specification) (implemented by [platformdirs](https://github.com/tox-dev/platformdirs)).
The default global configuration location can be changed by passing a path to `--config-global` through the command line.
This type of configuration is best suited for options that follow the user across multiple projects.

#### Local Configuration

Local configuration files are searched in multiple locations, the first file found is used.
The Local config search order is:
1. `edq-config.json` in the current directory.
2. A legacy file in the current directory (only if a legacy file is preconfigured).
3. `edq-config.json` in any ancestor directory on the path to root.

#### CLI-Specified Config Files

Any files passed via `--config-file` will be loaded in the order they appear on the command line.
Later files will override options from previous ones.

Below is an example of a CLI specified configuration path:
```
python3 -m edq.cli.config.list --config-file <file-name>.json --config-file ~/.secrets/<file-name>.json
```

#### CLI Configuration

Configuration options are structured as key value pairs.
Keys cannot contain the "=" character.
Configuration options are passed to the command line by the `--config` flag in this format `--config <key>=<value>`.
The provided values overrides the values from configuration files.

Below is an example of specifying a configuration option directly from the CLI:
```
python3 -m edq.cli.config.list --config user=edq-user --config pass=1234567890
```

#### CLI Config Options

The table below lists all the default configuration CLI options available.

| CLI Option       | Description |
| :-------------:  | :---------- |
|`--config-global` | Loads global configuration options from the file provided instead of the default global configuration file path. |
|`--global`        | Writes to or removes from the default global configuration file path. |
| `--local`        | Writes to or removes from the first local configuration file found (check local configuration section for [search order.](#local-configuration)). If no local configuration file is found, an `edq-config.json` file is created in the current directory, and the specified configuration option is written to it. |
|`--config-file`   | For writing options: writes to the specified file. For reading options: loads [CLI specified file](#cli-specified-config-files) configuration options from the specified file. |
| `--config`       | For providing additional CLI configuration parameters to a CLI command. |
| `--show-origin`  | Shows where each configuration's value was obtained from. |
| `--help`         | Displays a help message with detailed descriptions of each option. Shows the exact default global configuration file path for the current platform. |
