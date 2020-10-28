#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
# Copyright (C) 2019-2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# # Quit on errors
# set -o errexit

# # Quit on unbound symbols
# set -o nounset

check_manifest () {
    python -m check_manifest --ignore ".*-requirements.txt"
}

check_sphinx () {
  python -m sphinx.cmd.build -qnNW docs docs/_build/html
}

check_pytest () {
  docker-services-cli up es postgresql redis
  python -m pytest
  tests_exit_code=$?
  docker-services-cli down
  exit "$tests_exit_code"
}


if [ $# -eq 0 ]
then
  check_manifest
  check_sphinx
  check_pytest
else
  for arg in "$@"
  do
      case $arg in
          --check-manifest) check_manifest;;
          --check-sphinx) check_sphinx;;
          --check-pytest) check_pytest;;
      esac
  done
fi
