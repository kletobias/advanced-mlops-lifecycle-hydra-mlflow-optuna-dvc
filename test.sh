#!/bin/bash
#===============================================================================
#
#          FILE: test.sh
#
#         USAGE: ./test.sh
#
#   DESCRIPTION: 
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 03/19/2025 12:24:17
#      REVISION:  ---
#===============================================================================

set -o nounset                                  # Treat unset variables as an error

/opt/homebrew/bin/micromamba activate $HOME/micromamba/envs/practice
which python
