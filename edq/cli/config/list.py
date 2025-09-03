import sys

import edq.core.argparser

DESCRIPTION = "List your current configuration options."

def run(args):
    config_list = []
    for (key, value) in args._config.items():
        config_str = f"{key}\t{value}"
        if (args.show_origin):
            config_source_obj = args._config_sources.get(key)
            config_str += f"\t{config_source_obj.path}"

        config_list.append(config_str)

    print("\n".join(config_list))
    return 0

def main():
    return run(edq.core.argparser.get_default_parser(DESCRIPTION).parse_args())

if (__name__ == '__main__'):
    sys.exit(main())