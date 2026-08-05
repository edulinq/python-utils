#!/bin/bash

# Create HTML documentation for the current code.

readonly THIS_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd | xargs realpath)"
readonly ROOT_DIR="${THIS_DIR}/.."

readonly BASE_PACKAGE="edq"
readonly PACKAGE_DIR="${ROOT_DIR}/${BASE_PACKAGE}"
readonly DEFAULT_OUT_DIR="${ROOT_DIR}/build/html"

function main() {
    if [[ $# -gt 1 ]]; then
        echo "USAGE: $0 [out dir]"
        exit 1
    fi

    set -o pipefail
    trap exit SIGINT

    local outputDir=$DEFAULT_OUT_DIR
    if [[ $# -gt 0 ]]; then
        outputDir=$1
    fi

    cd "${ROOT_DIR}"

    mkdir -p "${outputDir}"

    python3 -m edq.cli.doc.gen-docs "${PACKAGE_DIR}" --out-dir "${outputDir}"
    if [[ $? -ne 0 ]] ; then
        echo "Failed to generate docs."
        return 2
    fi

    return 0
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
