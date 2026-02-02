import io
import os

import bs4

import edq.clilib.model
import edq.util.dirent

def update_pdoc(package_dir: str, base_qualified_name: str, docs_base_dir: str) -> None:
    """
    Update a built pdoc HTML documentation dir with information about CLI utils from the given package dir.
    This will add information (like usage) to the HTML documentation.

    The base docs dir should be such that we can use a module's qualified name to locate the documentation file,
    e.g., `edq.cli.version` -> `<base docs dir>/edq/cli/version.html`.
    """

    package = edq.clilib.model.CLIPackage.from_path(package_dir, 'edq.cli')
    if (package is None):
        raise ValueError(f"Target dir is not a CLI package: '{package_dir}'.")

    _update_package(package, docs_base_dir)

def _update_package(package: edq.clilib.model.CLIPackage, docs_base_dir: str) -> None:
    """ Recursively update the documentation for a package. """

    _update_package_docs(package, docs_base_dir)

    for entry in package.dirents:
        if (isinstance(entry, edq.clilib.model.CLIModule)):
            _update_module_docs(entry, docs_base_dir)
        elif (isinstance(entry, edq.clilib.model.CLIPackage)):
            _update_package(entry, docs_base_dir)
        else:
            raise ValueError(f"Unknown CLI type: '{type(entry)}'.")

def _update_package_docs(package: edq.clilib.model.CLIPackage, docs_base_dir: str) -> None:
    """ Update the documentation for a package. """

    # TODO(eriq)

def _update_module_docs(module: edq.clilib.model.CLIModule, docs_base_dir: str) -> None:
    """ Update the documentation for a module. """

    buffer = io.StringIO()
    module.parser.print_help(file = buffer)
    help_text = buffer.getvalue()
    buffer.close()

    docs_path = _get_docs_path(module, docs_base_dir)

    text = edq.util.dirent.read_file(docs_path)
    document = bs4.BeautifulSoup(text, 'html.parser')

    # Check for previous content.
    tags = document.select('div.edq-cli-docs')
    for tag in tags:
        tag.decompose()

    # Add in new content.
    parents = document.select('.module-info .docstring')
    if (len(parents) != 1):
        raise ValueError(f"Could not find exactly one HTML docstring (found {len(parents)}): '{docs_path}'.")

    content = f"<div class='.edq-cli-docs'><pre><code>{help_text}</code></pre></div>"
    new_tag = bs4.BeautifulSoup(content, 'html.parser')

    parents[0].append(new_tag)

    edq.util.dirent.write_file(docs_path, str(document))

def _get_docs_path(dirent: edq.clilib.model.CLIDirent, docs_base_dir: str) -> str:
    """ Create the relative path for a CLI dirent's HTML documentation from its qualified name. """

    parts = dirent.qualified_name.split('.')
    parts[-1] += '.html'
    return os.path.join(docs_base_dir, *parts)
