<!--
SPDX-FileCopyrightText: 2019 CERN.
SPDX-FileCopyrightText: 2019 Northwestern University.
SPDX-License-Identifier: MIT
-->

# Invenio-RDM-Records

[![CI](https://github.com/inveniosoftware/invenio-rdm-records/workflows/CI/badge.svg)](https://github.com/inveniosoftware/invenio-rdm-records/actions?query=workflow%3ACI+branch%3Amaster)
[![Release](https://img.shields.io/github/tag/inveniosoftware/invenio-rdm-records.svg)](https://github.com/inveniosoftware/invenio-rdm-records/releases)
[![Downloads](https://img.shields.io/pypi/dm/invenio-rdm-records.svg)](https://pypi.python.org/pypi/invenio-rdm-records)
[![License](https://img.shields.io/github/license/inveniosoftware/invenio-rdm-records.svg)](https://github.com/inveniosoftware/invenio-rdm-records/blob/master/LICENSE)

DataCite-based data model for Invenio.

Further documentation is available on
https://inveniordm.docs.cern.ch

## Development

### Install

Choose a version of search and database, then run:

```console
uv run pip install -e .[all]
uv run pip install invenio-search[<opensearch[1]>]
uv run pip install invenio-db[<[mysql|postgresql|]>]
```

### Tests

```console
uv run ./run-tests.sh
```
