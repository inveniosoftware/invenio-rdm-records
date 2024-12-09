# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Search dumpers for subject hierarchy support."""

from invenio_records.dumpers import SearchDumperExt


class SubjectHierarchyDumperExt(SearchDumperExt):
    """Search dumper extension for subject hierarchy support.

    It parses the values of the `subjects` field in the document, builds hierarchical
    parent notations, and adds entries to the `hierarchy` field for each subject in award.

    This dumper needs to be placed after the RelationDumper for subjects as it relies
    on dereferenced subjects with scheme, subject, and props.

    Example
    "subjects" :
        [
            {
            "id" : "euroscivoc:425",
            "subject" : "Energy and fuels",
            "scheme" : "EuroSciVoc",
            "props" : {
                "parents" : "euroscivoc:25,euroscivoc:67",
            },
            "@v" : "ef9f1c4c-b469-4645-a4b2-0db9b1c42096::1"
            }
        ]

    The above subject is dumped with hierarchy field and is transformed to

    "subjects" :
        [
            {
            "id" : "euroscivoc:425",
            "subject" : "Energy and fuels",
            "scheme" : "EuroSciVoc",
            "props" : {
                "parents" : "euroscivoc:25,euroscivoc:67",
                "hierarchy" : [
                    "euroscivoc:25",
                    "euroscivoc:25,euroscivoc:67",
                    "euroscivoc:25,euroscivoc:67,euroscivoc:425"
                ]
            },
            "@v" : "ef9f1c4c-b469-4645-a4b2-0db9b1c42096::1"
            }
        ]
    """

    def __init__(self, splitchar=","):
        """Constructor.

        :param splitchar: string to use to combine subject ids in hierarchy
        """
        super().__init__()
        self._splitchar = splitchar

    def dump(self, record, data):
        """Dump the data to secondary storage (OpenSearch-like)."""
        awards = data.get("metadata", {}).get("funding", [])

        def build_hierarchy(parents_str, current_subject_id):
            """Build the hierarchy by progressively combining parent notations."""
            if not parents_str:
                return [
                    current_subject_id
                ]  # No parents, so the hierarchy is just the current ID.

            parents = parents_str.split(self._splitchar)  # Split the parent notations
            hierarchy = []
            current_hierarchy = parents[0]  # Start with the top-level parent

            hierarchy.append(current_hierarchy)
            for parent in parents[1:]:
                current_hierarchy = f"{current_hierarchy}{self._splitchar}{parent}"
                hierarchy.append(current_hierarchy)

            hierarchy.append(
                f"{current_hierarchy}{self._splitchar}{current_subject_id}"
            )
            return hierarchy

        for award in awards:
            subjects = award.get("award", {}).get("subjects", [])
            for subject in subjects:
                parents = subject.get("props", {}).get("parents", "")
                current_subject_id = subject.get("id", "")
                if current_subject_id:
                    subject_hierarchy = build_hierarchy(parents, current_subject_id)
                    subject.setdefault("props", {})["hierarchy"] = subject_hierarchy

        if awards:
            data["metadata"]["funding"] = awards

    def load(self, data, record_cls):
        """Load the data from secondary storage (OpenSearch-like).

        This is run against the parent too (for some reason), so presence of any
        field cannot be assumed.
        """
        pass
