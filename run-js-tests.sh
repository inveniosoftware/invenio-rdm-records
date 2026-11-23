#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
# Copyright (C) 2026 CESNET.
#
# Run JavaScript tests for this repository.

set -o errexit
set -o nounset

# Use WORKING_DIR from environment if provided (CI), otherwise calculate from script location
if [ -n "${WORKING_DIR:-}" ]; then
    JS_DIR="$WORKING_DIR"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    JS_DIR="$SCRIPT_DIR/invenio_rdm_records/assets/semantic-ui/js/invenio_rdm_records"
fi

WATCH_MODE=false

cd "$JS_DIR"

# Parse arguments
for arg in "$@"; do
    case ${arg} in
        -i|--install)
            if [ -f package-lock.json ]; then
                npm ci
            else
                npm install
            fi
            exit 0
            ;;
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./run-js-tests.sh [options] [npm test options]"
            echo ""
            echo "Options:"
            echo "  -i, --install    Install dependencies only"
            echo "  -w, --watch      Run tests in watch mode (default: CI mode)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run-js-tests.sh                      Run tests once (CI mode - default)"
            echo "  ./run-js-tests.sh -w                   Run tests in watch mode"
            echo "  ./run-js-tests.sh --testPathPattern=DepositFilesService"
            exit 0
            ;;
    esac
done

# Default to CI mode (non-watch) unless -w/--watch is specified
if [ "$WATCH_MODE" = false ]; then
    CI=true npm test -- --watchAll=false "$@"
else
    npm test -- "$@"
fi
