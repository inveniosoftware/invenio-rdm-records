..
    Copyright (C) 2019 CERN.
    Copyright (C) 2019 Northwestern University.


    Invenio-RDM-Records is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

====================
 Invenio-RDM-Records
====================

.. image:: https://github.com/inveniosoftware/invenio-rdm-records/workflows/CI/badge.svg
        :target: https://github.com/inveniosoftware/invenio-rdm-records/actions?query=workflow%3ACI+branch%3Amaster

.. image:: https://img.shields.io/github/tag/inveniosoftware/invenio-rdm-records.svg
        :target: https://github.com/inveniosoftware/invenio-rdm-records/releases

.. image:: https://img.shields.io/pypi/dm/invenio-rdm-records.svg
        :target: https://pypi.python.org/pypi/invenio-rdm-records

.. image:: https://img.shields.io/github/license/inveniosoftware/invenio-rdm-records.svg
        :target: https://github.com/inveniosoftware/invenio-rdm-records/blob/master/LICENSE

DataCite-based data model for Invenio.

Further documentation is available on
https://invenio-rdm-records.readthedocs.io/

Development
===========

Install
-------

Choose a version of search and database, then run:

.. code-block:: console

    pipenv run pip install -e .[all]
    pipenv run pip install invenio-search[<opensearch[1]>]
    pipenv run pip install invenio-db[<[mysql|postgresql|]>]


Tests
-----

.. code-block:: console

    pipenv run ./run-tests.sh
