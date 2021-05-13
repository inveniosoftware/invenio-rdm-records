# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Convert an old style vocabulary file to a new style vocabulary file.

Just a temporary utility to use on the CLI.

USAGE: pipenv run python convert_to_vocabulary.py
"""

import csv
from collections import defaultdict
from pathlib import Path

import yaml


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
    prev_row = defaultdict(str)

    for row in dict_reader:  # row is an OrderedDict in fieldnames order
        current_row = row
        for field in row:
            if not current_row[field]:
                current_row[field] = prev_row[field]
            else:
                break
        prev_row = current_row
        yield current_row


class ResourceTypeExporter:
    """Exporter for resource type vocabulary."""

    base_filename = "resource_types"

    def to_dict(self, csv_row):
        """Converts csv_row to new vocabulary dict."""
        return {
            "id": (csv_row["subtype"] or csv_row["type"]),
            "title": {
                "en": csv_row["subtype_name"] or csv_row["type_name"]
            },
            "props": dict(csv_row)
        }

    @property
    def csv_filename(self):
        """Get csv filename."""
        return Path(self.base_filename).with_suffix(".csv")

    @property
    def yaml_filename(self):
        """Get yaml filename."""
        return Path(self.base_filename).with_suffix(".yaml")


if __name__ == "__main__":
    exporter = ResourceTypeExporter()

    csv_filepath = Path(__file__).parent / exporter.csv_filename
    yaml_filepath = (
        Path(__file__).parent.parent /
        Path("fixtures/data/vocabularies") / exporter.yaml_filename
    ).resolve()

    with open(csv_filepath) as csv_file:
        reader = csv.DictReader(csv_file)
        reader = hierarchized_rows(reader)
        with open(yaml_filepath, "w") as yaml_file:
            yaml_doc = yaml.dump(
                [exporter.to_dict(row) for row in reader],
                yaml_file
            )
