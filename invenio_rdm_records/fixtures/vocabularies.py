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
from collections import defaultdict
from os.path import splitext
from pathlib import Path

import pkg_resources
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
# Exceptions
#
class ConflictingFixturesError(Exception):
    """Exception when multiple modules provide same subject."""

    def __init__(self, errors):
        """Constructor."""
        message = "\n".join(errors)
        super().__init__(message)
        self.errors = errors


#
# Fixture
#
class PrioritizedVocabulariesFixtures:
    """Concept of Vocabulary fixtures across locations.

    This class' responsibility is to load different vocabularies in
    this priority order: app_data, then extensions and then this package.

    Earlier vocabularies in this hierarchy are chosen first. But in the case
    of subvocabularies (e.g. subject types), having loaded a subvocabulary
    before, shouldn't prevent loading another one. Only if the same
    subvocabulary is encountered again should it be ignored.

    Concretely, having loaded MeSH subjects shouldn't prevent loading FAST
    subjects even though they are both under the "subjects" vocabulary.
    Another MeSH subject encountered down the hierarchy is ignored however.
    """

    def __init__(self, identity, app_data_folder=None, pkg_data_folder=None,
                 filename="vocabularies.yaml", delay=True):
        """Constructor.

        identity: Identity to use when loading
        app_data_folder: Path object to instance data folder
        pkg_data_folder: Path object to this package's data folder.
                         Defaults to `./data` and really only changeable for
                         tests.
        filename: vocabularies filename to check at each location
        """
        self._identity = identity
        # Path("./app_data") assumes app_data is in current working directory
        self._app_data_folder = app_data_folder or Path("./app_data")
        self._pkg_data_folder = (
            pkg_data_folder or Path(__file__).parent / "data"
        )
        self._filename = filename
        self._delay = delay

    def _entry_points(self):
        """List entrypoints.

        Python now officially recommends importlib.metadata
        (importlib_metadata backport) for entrypoints:
        - https://docs.python.org/3/library/importlib.metadata.html
        - https://packaging.python.org/guides/creating-and-discovering-plugins/
          #using-package-metadata

        but Invenio is much invested in pkg_resources (``entry_points``
        fixture assumes it). So we use pkg_resources for now until
        _entry_points implementation can be changed.
        """
        return list(
            pkg_resources.iter_entry_points('invenio_rdm_records.fixtures')
        )

    def load(self):
        """Load the fixtures.

        Loads in priority

        1- app_data_folder
        2- extensions
        3- this package's fixtures

        Fixtures found later are ignored.
        """
        self._loaded_vocabularies = set()

        # 1- Load from app_data_folder
        filepath = self._app_data_folder / self._filename
        # An instance doesn't necessarily have custom vocabularies
        # and that's ok
        if filepath.exists():
            self.load_vocabularies(filepath)

        # 2- Load from extensions / entry_points
        self.load_from_extensions()

        # 3- Load any default fixtures from invenio_rdm_records
        self.load_vocabularies(self._pkg_data_folder / self._filename)

    def load_from_extensions(self):
        """Load vocabularies from extensions.

        There might be priority conflicts at the extensions level. An
        exception is raised in this case rather than loading any fixture.
        """
        # First check if any conflicts
        vocabulary_modules = defaultdict(list)
        extensions = [ep.load() for ep in self._entry_points()]
        for module in extensions:
            directory = Path(module.__file__).parent
            filepath = directory / self._filename
            for v in self.peek_vocabularies(filepath):
                vocabulary_modules[v].append(module.__name__)

        errors = [
            f"Vocabulary '{v}' cannot have multiple sources {ms}"
            for v, ms in vocabulary_modules.items() if len(ms) > 1
        ]
        if errors:
            raise ConflictingFixturesError(errors)

        # Then load
        for module in extensions:
            directory = Path(module.__file__).parent
            filepath = directory / self._filename
            self.load_vocabularies(filepath)

    def peek_vocabularies(self, filepath):
        """Peek at vocabularies listed in vocabularies file.

        Returns list of vocabularies.
        """
        vocabularies = []
        fixture = VocabulariesFixture(self._identity, filepath)
        for id_, entry in fixture.read():
            if isinstance(entry["data-file"], dict):
                subvocabularies = [
                    f"{id_}.{k}" for k in entry["data-file"].keys()
                ]
                vocabularies.extend(subvocabularies)
            else:
                vocabularies.append(id_)
        return vocabularies

    def load_vocabularies(self, filepath):
        """Load vocabularies listed in vocabularies file."""
        fixture = VocabulariesFixture(
            self._identity,
            filepath,
            delay=self._delay
        )
        self._loaded_vocabularies = fixture.load(
            ignore=self._loaded_vocabularies
        )


class VocabulariesFixture:
    """Vocabularies fixture.

    This class' responsibility is to load the vocabularies in its
    vocabularies file.
    """

    def __init__(self, identity, filepath, delay=True):
        """Initialize the fixture."""
        self._filepath = filepath
        self._identity = identity
        self._delay = delay

    def read(self):
        """Return content of vocabulary file."""
        dir_ = self._filepath.parent
        with open(self._filepath) as f:
            data = yaml.safe_load(f) or {}
            for id_, entry in data.items():
                if isinstance(entry["data-file"], dict):
                    entry["data-file"] = {
                        k: dir_ / v for k, v in entry["data-file"].items()
                    }
                else:
                    entry["data-file"] = dir_ / entry["data-file"]

                yield id_, entry

    def get_records_by_vocabulary(self, vocabulary_id):
        """Get all records of a given vocabulary."""
        for id_, entry in self.read():
            if vocabulary_id != id_:
                continue
            for record in self.iter_datafile(entry["data-file"]):
                yield record

    def load(self, ignore=None):
        """Load the fixture.

        ignore: iterable of ids to ignore

        For subjects (or any vocabulary with a dict of data-file), the id
        that counts is ``<vocabulary id>.<dict key>``.
        """
        ids = set().union(ignore) if ignore else set()

        for id_, entry in self.read():
            # TODO: We need to carefully think about what the workflow for
            #       adding new subjects later is and then modify the code to
            #       allow for it.
            if id_ not in ids:
                try:
                    self.create_vocabulary_type(id_, entry)
                except IntegrityError:
                    # Can only get here when running the code multiple times
                    # on same database. To keep the code simple for now, we
                    # simply skip previously existing types.
                    current_app.logger.info(
                        f"Skipping creation and loading of pre-existing {id_}"
                    )
                    continue

            if isinstance(entry["data-file"], dict):
                # The subvocabularies may not have been loaded
                for key, filepath in entry["data-file"].items():
                    sub_id = f"{id_}.{key}"
                    if sub_id not in ids:
                        self.load_datafile(id_, filepath)
                        ids.add(sub_id)
                ids.add(id_)
            elif id_ not in ids:
                self.load_datafile(id_, entry["data-file"])
                ids.add(id_)

        return ids

    def create_vocabulary_type(self, id_, entry):
        """Create the vocabulary type."""
        pid_type = entry['pid-type']
        current_service.create_type(self._identity, id_, pid_type)

    def load_datafile(self, id_, filepath, delay=None):
        """Load the records from the data file."""
        for record in self.iter_datafile(filepath):
            record['type'] = id_
            delay = delay if delay is not None else self._delay
            if delay:
                create_vocabulary_record.delay(record)
            else:  # mostly for tests
                create_vocabulary_record(record)

    def iter_datafile(self, filepath):
        """Get an entry iterator for a given "data file" entry."""
        return create_iterator(filepath)
