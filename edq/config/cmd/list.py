"""
List the current configuration options.
"""

import argparse

CONFIG_FIELD_SEPARATOR: str = "\t"

def run(args: argparse.Namespace) -> int:
    """ Run the target command and return the suggested exit status. """

    config_info = args._config_info

    rows = []
    for (key, value) in config_info.raw_config.items():
        row = [key, str(value)]
        if (args.show_origin):
            config_source_obj = config_info.sources.get(key)

            origin = config_source_obj.path
            if (origin is None):
                origin = config_source_obj.label

            row.append(origin)

        rows.append(CONFIG_FIELD_SEPARATOR.join(row))

    rows.sort()

    if (not args.skip_header):
        header = ["Key", "Value"]
        if (args.show_origin):
            header.append("Origin")

        rows.insert(0, (CONFIG_FIELD_SEPARATOR.join(header)))

    print("\n".join(rows))
    return 0

def modify_parser(parser: argparse.ArgumentParser) -> None:
    """ Add this CLI's flags to the given parser. """

    group = parser.add_argument_group('list options')

    group.add_argument("--show-origin", dest = 'show_origin',
        action = 'store_true',
        help = "Display where each configuration's value was obtained from.",
    )

    group.add_argument("--skip-header", dest = 'skip_header',
        action = 'store_true',
        help = 'Skip headers when displaying configs.',
    )
