# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Search mappings for InvenioRDM records and drafts.

The mappings must be identical for both drafts/records and search mappings.
Thus for one JSONSchema version four mappings exists, e.g. for v1.0.0:

- ``os-v1/rdmrecords/drafts/draft-v1.0.0.json``
- ``os-v1/rdmrecords/records/record-v1.0.0.json``
- ``v7/rdmrecords/drafts/draft-v1.0.0.json``
- ``v7/rdmrecords/records/record-v1.0.0.json``

This creates the following aliases:

- ``rdmrecords`` - Contains both records and drafts (and thus also duplicates).
- ``rdmrecords-records`` - Records in multiple different schema versions.
- ``rdmrecords-drafts`` - Drafts in multiple different schema versions.

The only difference between the four mappings for a JSONSchema version is that
v6 mappings has an extra level of nesting for the doctype compared to v7.

Example of v6 mapping:

.. code-block:: python

    {
        "mappings": {
            "_doc": {
                # Mapping
            }
        }
    }

Example of v7 mapping:

.. code-block:: python

    {
        "mappings": {
            # Mapping
        }
    }

The difference is due to the ``doctype`` being removed from Search v7.
"""
