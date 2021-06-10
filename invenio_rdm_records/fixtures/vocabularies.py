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
from flask import current_app
from invenio_vocabularies.proxies import current_service
from sqlalchemy.exc import IntegrityError

from .tasks import create_vocabulary_record


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
            # Allow empty files
            data = yaml.safe_load(fp) or []
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


def create_iterator(data_file):
    """Creates an iterator from a file."""
    ext = splitext(data_file)[1].lower()
    if ext == '.yaml':
        return YamlIterator(data_file)
    elif ext == '.csv':
        return CSVIterator(data_file)
    elif ext == '.jsonl':
        return JSONLinesIterator(data_file)
    raise RuntimeError(f'Unknown data format: {ext}')


class DataIteratorIterator:
    """Iterator over iterators."""

    def __init__(self, data_files):
        """Initialize iterator."""
        self._data_files = data_files

    def __iter__(self):
        """Iterate over iterators."""
        for data_file in self._data_files.values():
            yield from create_iterator(data_file)


#
# Fixture
#
class VocabulariesFixture:
    """Vocabularies fixture."""

    def __init__(self, identity, search_paths, filename):
        """Initialize the fixture."""
        self._search_paths = search_paths
        self._filename = filename
        self._identity = identity

    def _open_vocabularies(self):
        """Open vocabulary file and return its content."""
        for path in self._search_paths:
            filepath = path / self._filename

            # Providing a vocabularies.yaml file is optional
            if not filepath.exists():
                continue

            with open(filepath) as fp:
                data = yaml.safe_load(fp) or {}
                for id_, entry in data.items():
                    if isinstance(entry["data-file"], dict):
                        entry["data-file"] = {
                            k: path / v for k, v in entry["data-file"].items()
                        }
                    else:
                        entry["data-file"] = path / entry["data-file"]

                    yield id_, entry

    def get_records_by_vocabulary(self, vocabulary_id):
        """Get all records of a given vocabulary."""
        for id_, entry in self._open_vocabularies():
            if vocabulary_id != id_:
                continue
            for record in self.iter_datafile(entry["data-file"]):
                yield record

    def load(self):
        """Load the fixture.

        Fixtures found sooner in self._search_paths have priority.
        """
        ids = set()

        for id_, entry in self._open_vocabularies():
            if id_ not in ids:
                try:
                    self.load_vocabulary(id_, entry)
                except IntegrityError:
                    current_app.logger.info(
                        f"Skipping creation of {id_}, already existing"
                    )
                    continue
                ids.add(id_)

    def load_vocabulary(self, id_, entry, delay=True):
        """Load a single vocabulary."""
        pid_type = entry['pid-type']
        # Create the vocabulary type
        current_service.create_type(self._identity, id_, pid_type)
        # Load the data file
        self.load_datafile(id_, entry["data-file"], delay=delay)

    def load_datafile(self, id_, data_file_or_dict, delay=True):
        """Load the records from the data file."""
        for record in self.iter_datafile(data_file_or_dict):
            record['type'] = id_
            if delay:
                create_vocabulary_record.delay(record)
            else:  # mostly for tests
                create_vocabulary_record(record)

    def iter_datafile(self, data_file_or_dict):
        """Get an entry iterator for a given "data file" entry."""
        if isinstance(data_file_or_dict, dict):
            return DataIteratorIterator(data_file_or_dict)
        else:
            return create_iterator(data_file_or_dict)
