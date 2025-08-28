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

This system provides a consistent method for supplying configuration options to a CLI tool.
While each CLI tool may require its own additional options, this system standardizes the configuration loading process.

By default, the configuration file is named `edq-config.json`.
This name can be customized by specifying a different file name when calling the configuration system.

For the purposes of this documentation, the default file name is used.

### Configuration Sources

Configuration options can come from several places, with later sources overwriting earlier ones.

<table>
    <tr>
        <th style="text-align: center;">Sources</th>
        <th style="text-align: center;">Description</th>
    </tr>
    <tr>
        <td>Global</td>
        <td>
            The default global configuration file, <code>edq-config.json</code>, is located in the platform-specific user configuration directory.
            This follows the recommendation from <a href="https://github.com/tox-dev/platformdirs">platformdirs</a>.
            You can change its location with the --global-config option.
        </td>
    </tr>
    <tr>
        <td>Local</td>
        <td>
            Local config files can be found in different locations.
            Once a match is found, the search stops.
            Local config is resolved in this order: edq-config.json in current directory, a supported legacy file in the current directory, then the nearest ancestor edq-config.json.
        </td>
    </tr>
    <tr>
        <td>CLI</td>
        <td>
            Config files passed with --config-file are loaded sequentially, and options in later files override those in earlier ones.
        </td>
    </tr>
    <tr>
        <td>CLI Bear</td>
        <td>
            Command-line options (e.g., --user, --token, --server) override all other configuration sources, unless specific keys are configured to be ignored.
        </td>
    </tr>
</table>


#### Global Configuration

The default location a global config is looked for is `<platform-specific user config location>/edq-config.json`.
This is considered to be the "proper" place to store user-related configuration, according to [platformdirs](https://github.com/tox-dev/platformdirs).
The location where a global config will be looked for can be changed by passing a path to `--global-config` through the command line.
This type of config is best suited for login credentials or persistent user preferences.
Run any CLI tool with `--help` to see the exact path on your platform.

#### Local Configuration

Local configuration files can be found in different locations.
The first file found will be used, and other locations will not be searched.
Local config search order is as follows:
1. An `edq-config.json` in the current directory.
2. A legacy file in the current directory. If the config system is set to support a specified legacy file.
3. An `edq-config.json` file located in any ancestor directory on the path to root (or up to a cutoff limit if one is specified to the config system).

#### CLI-Specified Config Files

Any files passed via `--config-file` will be loaded in the order they appear on the command line.
Later files will override options from previous ones.

#### Bare CLI Options

Options passed directly on the command line (e.g., `--user`, `--token`, `--server`).
These always override every other configuration source.
The configuration system can be set to ignore specific CLI keys when applying overrides, if needed.
