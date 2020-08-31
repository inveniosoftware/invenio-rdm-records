# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Search Engine's class."""

from invenio_search import RecordsSearch


class BibliographicRecordsSearch(RecordsSearch):
    """Main Bibliographic Record search class."""

    class Meta:
        """Configuration for Bibliographic Records search."""

        index = 'records'
        doc_types = None
        fields = ('*', )
