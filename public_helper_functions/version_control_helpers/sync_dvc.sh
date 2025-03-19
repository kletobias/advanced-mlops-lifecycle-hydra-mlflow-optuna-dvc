#!/bin/bash
# public_helper_functions/version_control/sync_dvc.sh
# bin/version_control/sync_dvc.sh

cd "$(git rev-parse --show-toplevel)" || exit 1
# Check configs directory for yaml files to update
fd --base-directory=configs -u -e yaml -X dvc add

# Check and add data versions csv
fd --base-directory=data '^v\d\.' -e csv -X dvc add
fd --base-directory=data '^v\d\.' -e json -X dvc add
fd --base-directory=data '^v\d\.' -e db -X dvc add
fd --base-directory=data 'v\d_metadata' -e json -X dvc add
