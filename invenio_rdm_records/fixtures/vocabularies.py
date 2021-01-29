# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Vocabulary fixtures module."""

import csv
import json
from os.path import splitext

import yaml
from invenio_vocabularies.proxies import current_service


#
# Data iterators
#
class DataIterator:
    """Data iterator base class."""

    def __init__(self, data_file):
        """Initialize iterator."""
        self._data_file = data_file


class YamlIterator(DataIterator):
    """YAML data iterator that loads records from YAML files."""

    def __iter__(self):
        """Iterate over records."""
        with open(self._data_file) as fp:
            data = yaml.load(fp)
            if data:  # Allow empty files
                for entry in data:
                    yield entry


class CSVIterator(DataIterator):
    """CSV data iterator that loads records from CSV files."""

    def map_row(self, header, row):
        """Map a CSV row into a record."""
        entry = {}
        for attr, value in zip(header, row):
            if attr == 'tags':
                value = [x.strip() for x in value.split(',')]
            keys = attr.split('__')
            if len(keys) == 1:
                entry[keys[0]] = value
            elif len(keys) == 2:
                if keys[0] not in entry:
                    entry[keys[0]] = {}
                entry[keys[0]][keys[1]] = value
        return entry

    def __iter__(self):
        """Iterate over records."""
        with open(self._data_file) as fp:
            reader = csv.reader(fp, delimiter=';', quotechar='"')
            header = next(reader)
            for row in reader:
                yield self.map_row(header, row)


class JSONLinesIterator(DataIterator):
    """JSON Lines data iterator that loads records from JSON Lines files."""

    def __iter__(self):
        """Iterate over records."""
        with open(self._data_file) as fp:
            for line in fp:
                yield json.loads(line)


#
# Fixture
#
class VocabulariesFixture:
    """Vocabularies fixture."""

    def __init__(self, identity, search_path, filename):
        """Initialize the fixture."""
        self._search_path = search_path
        self._filename = filename
        self._identity = identity

    def load(self):
        """Load the fixture."""
        with open(self._search_path.path(self._filename)) as fp:
            data = yaml.load(fp)
            for id_, entry in data.items():
                self.load_vocabulary(id_, entry)

    def load_vocabulary(self, id_, entry):
        """Load a single vocabulary."""
        pid_type = entry['pid-type']
        # Create the vocabulary type
        current_service.create_type(self._identity, id_, pid_type)
        # Load the data file
        data_file_path = entry.get('data-file')
        if data_file_path:  # Creates pid_type, no data yet
            data_file = self._search_path.path(data_file_path)
            self.load_datafile(id_, data_file)

    def load_datafile(self, id_, data_file):
        """Load the records form the data file."""
        for record in self.iter_datafile(data_file):
            record['type'] = id_
            # TODO: edit out languages which is not configured by the system
            current_service.create(self._identity, record)

    def iter_datafile(self, data_file):
        """Get an row iterator for a given data file."""
        ext = splitext(data_file)[1].lower()
        if ext == '.yaml':
            return YamlIterator(data_file)
        elif ext == '.csv':
            return CSVIterator(data_file)
        elif ext == '.jsonl':
            return JSONLinesIterator(data_file)
        raise RuntimeError(f'Unknown data format: {ext}')
