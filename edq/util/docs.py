import logging
import os
import pathlib
import re
import shutil
import subprocess
import typing
import venv
import warnings

import git
import pdoc

import edq.clilib.pdoc
import edq.util.dirent

_logger = logging.getLogger(__name__)

DEFAULT_FILE_PATTERNS: str = '!.*_test'
DEFAULT_MAIN_BRANCH: str = 'main'

REQUIREMENTS_FILANMES: typing.List[str] = [
    'requirements.txt',
    'requirements-dev.txt',
]

def build_site(
    repo_root_dir: str,
    base_package_name: str,
    base_out_dir: str,
    skip_tag_pattern: typing.Union[str, None] = None,
    main_branch: str = DEFAULT_MAIN_BRANCH,
    ) -> None:
    """
    Build a site that includes documentation for each non-skipped tagged version.

    This function makes several assumptions about the repository/package structure.
    For best results, both should mirror this repo/package.
    """

    repo_root_dir = os.path.abspath(repo_root_dir)

    edq.util.dirent.remove(base_out_dir)
    edq.util.dirent.mkdir(base_out_dir)

    out_dir = os.path.join(base_out_dir, 'latest')
    _gen_docs_for_version(repo_root_dir, base_package_name, main_branch, out_dir)

    repo = git.Repo(repo_root_dir)
    for tag in repo.tags:
        if ((skip_tag_pattern is not None) and (re.search(skip_tag_pattern, tag.name))):
            _logger.info("Skipping tag '%s' because of pattern.", tag.name)
            continue

        out_dir = os.path.join(base_out_dir, tag.name)
        _gen_docs_for_version(repo_root_dir, base_package_name, tag.name, out_dir)

def _gen_docs_for_version(
    repo_root_dir: str,
    base_package_name: str,
    git_reference: str,
    out_dir: str,
    ) -> None:
    """
    Generate documentation for a specific git reference.
    This is a little tricky because we have to import the code to document it,
    so we cannot just use this Python process (or venv) to generate the documentation.
    """

    bash_path = shutil.which('bash')
    if (bash_path is None):
        raise ValueError("Could not find `bash`, which is required for generating docs.")

    _logger.info("Generating documentation for '%s'.", git_reference)

    temp_dir = _prep_repo(repo_root_dir, base_package_name, git_reference)
    if (temp_dir is None):
        return

    repo_dir = os.path.join(temp_dir, 'repo')
    venv_dir = os.path.join(temp_dir, 'venv')

    activate_path = os.path.join(venv_dir, 'bin', 'activate')
    gen_docs_path = os.path.join(repo_dir, 'scripts', 'gen_docs.sh')

    command = f"source '{activate_path}' ; '{gen_docs_path}'"
    result = subprocess.run(command, shell = True, executable = bash_path, cwd = repo_dir, capture_output = True, check = False)
    if (result.returncode != 0):
        stdout = result.stdout.decode(edq.util.dirent.DEFAULT_ENCODING)
        stderr = result.stderr.decode(edq.util.dirent.DEFAULT_ENCODING)

        raise ValueError(f"`scripts/gen_docs.sh` did not exit cleanly. Stdout: '{stdout}', Stderr: '{stderr}'")

    build_path = os.path.join(repo_dir, 'build', 'html')
    if (not os.path.exists(build_path)):
        _logger.warning("Could not find the output of `scripts/gen_docs.sh` for version: '%s'.", git_reference)
        return

    edq.util.dirent.copy(build_path, out_dir)

    _logger.info("Completed documentation for '%s'.", git_reference)

def _prep_repo(
    repo_root_dir: str,
    base_package_name: str,
    git_reference: str,
    ) -> typing.Union[str, None]:
    """
    Prepare a copy of the specified repo for documentation and return the base temp dir.

    This will create a temp dir (returned),
    copy the repo to `<temp dir>/repo`,
    clean staging (`git clean -xdf` && `git reset --hard`),
    checkout the reference,
    make a venv at `<temp dir>/venv`,
    and install any dependencies (requirements*.txt) to the venv.
    """

    temp_dir = edq.util.dirent.get_temp_dir(f"edq-build-site-{git_reference}-")
    repo_dir = os.path.join(temp_dir, 'repo')
    venv_dir = os.path.join(temp_dir, 'venv')

    edq.util.dirent.copy(repo_root_dir, repo_dir)

    repo = git.Repo(repo_dir)
    repo.git.clean('-xdf')
    repo.git.reset('--hard')

    repo.git.checkout(git_reference)

    gen_docs_path = os.path.join(repo_dir, 'scripts', 'gen_docs.sh')
    if (not os.path.isfile(gen_docs_path)):
        _logger.warning("Could not find `scripts/gen_docs.sh` for version: '%s'.", git_reference)
        return None

    venv.create(venv_dir, with_pip = True)

    requirements_paths = []
    for filename in REQUIREMENTS_FILANMES:
        path = os.path.join(repo_dir, filename)
        if (os.path.isfile(path)):
            requirements_paths.append(path)

    if (len(requirements_paths) > 0):
        args = [
            os.path.join('bin', 'pip'),
            'install',
        ]

        for requirements_path in requirements_paths:
            args += ['-r', requirements_path]

        result = subprocess.run(args, cwd = venv_dir, capture_output = True, check = False)
        if (result.returncode != 0):
            stdout = result.stdout.decode(edq.util.dirent.DEFAULT_ENCODING)
            stderr = result.stderr.decode(edq.util.dirent.DEFAULT_ENCODING)

            raise ValueError(f"`pip install` did not exit cleanly. Stdout: '{stdout}', Stderr: '{stderr}'")

    return temp_dir

def generate_docs(
    package_dir: str,
    out_dir: str,
    base_package_name: typing.Union[str, None] = None,
    file_pattern: str = DEFAULT_FILE_PATTERNS,
    base_qualified_cli_name: typing.Union[str, None] = None,
    update_cli: bool = True,
    **kwargs: typing.Any) -> None:
    """
    Generate documentation (via pdoc) for a specific package directory.

    This function makes several assumptions about the repository/package structure.
    For best results, both should mirror this repo/package.
    """

    package_dir = os.path.abspath(package_dir)

    if (base_package_name is None):
        base_package_name = os.path.basename(package_dir)

    edq.util.dirent.mkdir(out_dir)

    # Ignore warnings from this bug: https://github.com/mitmproxy/pdoc/issues/822
    warnings.filterwarnings('ignore', message = ".*Import of PODType failed: name 'PODType' is not defined.*")

    pdoc.pdoc(base_package_name, file_pattern, output_directory = pathlib.Path(out_dir))

    if (update_cli):
        edq.clilib.pdoc.update_pdoc(package_dir, base_package_name, out_dir)
