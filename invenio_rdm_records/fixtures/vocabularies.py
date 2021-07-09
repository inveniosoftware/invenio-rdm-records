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
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.models import VocabularyScheme, \
    VocabularyType
from sqlalchemy.orm import load_only

from ..proxies import current_rdm_records
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
# Fixture Loading
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
        self._loaded_vocabularies = set()

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
        # Prime with existing (sub)vocabularies
        v_type_ids = [
            v.id for v in VocabularyType.query.options(load_only("id")).all()
        ]
        v_subtype_ids = [
            f"{v.parent_id}.{v.id}" for v in
            VocabularyScheme.query.options(
                load_only("id", "parent_id")
            ).all()
        ]
        self._loaded_vocabularies = set(v_type_ids + v_subtype_ids)

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
            vocabularies.extend(entry.covered_ids)
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
        self._identity = identity
        self._filepath = filepath
        self._delay = delay

    def read(self):
        """Return content of vocabularies file."""
        dir_ = self._filepath.parent
        with open(self._filepath) as f:
            data = yaml.safe_load(f) or {}
            for id_, entry in data.items():
                # Some vocabularies are non-generic
                if id_ == "subjects":
                    entry = SubjectsVocabularyEntry(dir_, id_, entry)
                else:
                    entry = GenericVocabularyEntry(dir_, id_, entry)

                yield id_, entry

    def get_records_by_vocabulary(self, vocabulary_id):
        """Get all records of a given vocabulary."""
        for id_, entry in self.read():
            if vocabulary_id != id_:
                continue
            for record in entry:
                yield record

    def load(self, ignore=None):
        """Load the whole fixture.

        ignore: iterable of ids to ignore

        For subjects (or any vocabulary with a dict of data-file), the id
        that counts is ``<vocabulary id>.<dict key>``.

        Returns all vocabulary ids loaded so far.
        """
        ids = set().union(ignore) if ignore else set()

        for id_, entry in self.read():
            ids.update(
                entry.load(self._identity, ignore=ids, delay=self._delay)
            )

        return ids


class GenericVocabularyEntry:
    """Vocabulary fixture with single data-file."""

    def __init__(self, directory, id_, entry):
        """Constructor."""
        self._dir = directory
        self._id = id_
        self._entry = entry
        # There is logic to take care of this choice in tasks.py
        self._service_str = "vocabulary_service"

    def __iter__(self):
        """Iterator."""
        filepath = self._dir / self._entry["data-file"]
        yield from create_iterator(filepath)

    @property
    def covered_ids(self):
        """Just the id of the vocabulary covered by this entry as a list."""
        return [self._id]

    def create_vocabulary_type(self, identity):
        """Create the vocabulary type."""
        pid_type = self._entry['pid-type']
        current_service.create_type(identity, self._id, pid_type)

    def load(self, identity, ignore=None, delay=None):
        """Load the data file if self._id not in ignore.

        Return the loaded id as 1 item list.
        """
        ignore = ignore or set()

        if self._id not in ignore:
            self.create_vocabulary_type(identity)

            for record in self:
                record['type'] = self._id
                if delay:
                    create_vocabulary_record.delay(self._service_str, record)
                else:  # mostly for tests
                    create_vocabulary_record(self._service_str, record)
            return [self._id]

        return []


class SubjectsVocabularyEntry:
    """Vocabulary fixture for subjects vocabulary."""

    def __init__(self, directory, id_, entry):
        """Constructor."""
        self._dir = directory
        self._parent_id = id_
        self._entry = entry

        ids = [s["id"] for s in self.schemes()]
        # Raise if duplicate (conflicting)
        if len(ids) != len(set(ids)):
            raise ConflictingFixturesError(
                f"Duplicate subtypes found for {self._parent_id}"
            )

        self._service_str = "subjects_service"
        self._service = getattr(current_rdm_records, self._service_str)

    def schemes(self):
        """Return schemes."""
        return self._entry.get("schemes", [])

    def __iter__(self):
        """Iterator."""
        for scheme in self.schemes():
            filepath = self.dir_ / scheme.get("data-file")
            yield from create_iterator(filepath)

    @property
    def covered_ids(self):
        """List of ids of the subvocabularies covered by this entry."""
        return [f"{s['id']}" for s in self.schemes()]

    def create_scheme(self, identity, metadata):
        """Create the vocabulary scheme row."""
        id_ = metadata["id"]
        name = metadata.get("name", "")
        uri = metadata.get("uri", "")
        self._service.create_scheme(identity, id_, name=name, uri=uri)

    def load(self, identity, ignore=None, delay=None):
        """Load the data files whose ids are not in ignore."""
        ignore = ignore or set()
        loaded = []

        for scheme in self.schemes():
            id_ = f"{self._parent_id}.{scheme['id']}"
            if id_ not in ignore:
                self.create_scheme(identity, scheme)

                filepath = self._dir / scheme.get("data-file")
                for record in create_iterator(filepath):
                    if delay:
                        create_vocabulary_record.delay(
                            self._service_str, record)
                    else:  # mostly for tests
                        create_vocabulary_record(self._service_str, record)

                loaded.append(id_)

        return loaded
