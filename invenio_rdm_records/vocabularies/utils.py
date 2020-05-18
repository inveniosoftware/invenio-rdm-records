# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils for vocabulary code."""

from collections import defaultdict


def hierarchized_rows(dict_reader):
    """Yields filled OrderedDict rows according to csv hierarchy.

    Idea is to have the csv rows:

    fooA, barA-1, bazA-1
        , barA-2, bazA-2
    fooB, barB-1, bazB-1
        ,       , bazB-2

    map to these rows

    fooA, barA-1, bazA-1
    fooA, barA-2, bazA-2
    fooB, barB-1, bazB-1
    fooB, barB-1, bazB-2

    This makes it easy for subject matter experts to fill the csv in
    their spreadsheet software, while also allowing hierarchy of data
    a-la yaml and extensibility for other conversions or data down the road.
    """
    prev_row = defaultdict(lambda: "")

    for row in dict_reader:  # row is an OrderedDict in fieldnames order
        current_row = row
        for field in row:
            if not current_row[field]:
                current_row[field] = prev_row[field]
            else:
                break
        prev_row = current_row
        yield current_row
