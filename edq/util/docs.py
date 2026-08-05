import os
import pathlib
import typing
import warnings

import pdoc

import edq.clilib.pdoc
import edq.util.dirent

DEFAULT_FILE_PATTERNS: str = '!.*_test'

def generate_docs(
    package_dir: str,
    out_dir: str,
    base_package: typing.Union[str, None] = None,
    file_pattern: str = DEFAULT_FILE_PATTERNS,
    base_qualified_cli_name: typing.Union[str, None] = None,
    update_cli: bool = True,
    **kwargs: typing.Any) -> None:
    """
    Generate documentation (via pdoc) for a specific package directory.
    """

    package_dir = os.path.abspath(package_dir)

    if (base_package is None):
        base_package = os.path.basename(package_dir)

    edq.util.dirent.mkdir(out_dir)

    # Ignore warnings from this bug: https://github.com/mitmproxy/pdoc/issues/822
    warnings.filterwarnings('ignore', message = ".*Import of PODType failed: name 'PODType' is not defined.*")

    pdoc.pdoc(base_package, file_pattern, output_directory = pathlib.Path(out_dir))

    if (update_cli):
        edq.clilib.pdoc.update_pdoc(package_dir, base_package, out_dir)
