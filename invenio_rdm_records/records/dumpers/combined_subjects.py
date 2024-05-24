# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Search dumpers for combined subjects."""

from invenio_records.dumpers import SearchDumperExt

SPLITCHAR = "::"  # explict better than implicit


class CombinedSubjectsDumperExt(SearchDumperExt):
    """Search dumper extension for sombined subjects support.

    It parses the values of the `subjects` field
    in the document and adds entries of the form:
    `<scheme><splitchar><subject>` or `<subject>` in the `combined_subjects` field.

    The combined_subjects field is required for properly aggregating/faceting subjects.

    This dumper needs to be placed after the RelationDumper for subjects as it relies
    on dereferenced scheme + subject pairs.
    """

    def __init__(self, splitchar=SPLITCHAR):
        """Constructor.

        :param splitchar: string to use to combine scheme + subject.
                          It must be identical to the splitchar value used in the
                          CombinedTermsFacet.
        """
        super().__init__()
        self._splitchar = splitchar

    def dump(self, record, data):
        """Dump the data to secondary storage (OpenSearch-like)."""
        subjects = data.get("metadata", {}).get("subjects", [])

        def get_scheme_subject(subject_dict):
            """
            Return [<scheme>, <subject>] or [<subject>] for the given `subject_dict`.

            Assumes subject_dict has been dereferenced at this point.
            """
            result = []
            if "scheme" in subject_dict:
                result.append(subject_dict["scheme"])
            result.append(subject_dict["subject"])
            return result

        # There is no clarity on what keys can be assumed to be present in data
        # (e.g., test_records_communities calls dumps() without "metadata"),
        # so one has to be careful in how the dumped data is inserted back into `data`
        metadata = data.get("metadata", {})
        metadata["combined_subjects"] = [
            self._splitchar.join(get_scheme_subject(subject)) for subject in subjects
        ]
        data["metadata"] = metadata

    def load(self, data, record_cls):
        """Load the data from secondary storage (OpenSearch-like).

        This is run against the parent too (for some reason), so presence of any
        field cannot be assumed.
        """
        if "metadata" in data:
            data["metadata"].pop("combined_subjects", None)
        return data
