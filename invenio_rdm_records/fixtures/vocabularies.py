# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2021-2022 Northwestern University.
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
from invenio_db import db
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.models import VocabularyScheme, \
    VocabularyType
from sqlalchemy.orm import load_only

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
            for id_, yaml_entry in data.items():
                # Some vocabularies are non-generic
                if id_ in ("subjects", "affiliations"):
                    entry = VocabularyEntryWithSchemes(
                        id_, dir_, id_, yaml_entry
                    )
                elif id_ in ("names", "funders", "awards"):
                    entry = VocabularyEntry(
                        id_, dir_, id_, yaml_entry
                    )
                else:
                    entry = GenericVocabularyEntry(dir_, id_, yaml_entry)

                yield id_, entry

    def get_records_by_vocabulary(self, vocabulary_id):
        """Get all records of a given vocabulary."""
        for id_, entry in self.read():
            if vocabulary_id != id_:
                continue
            for data in entry.iterate(set()):
                yield data

    def load(self, ignore=None):
        """Load the whole fixture.

        ignore: iterable of ids to ignore

        For subjects (or any vocabulary with a dict of data-file), the id
        that counts is ``<vocabulary id>.<dict key>``.

        Returns all vocabulary ids loaded so far.
        """
        ids = set(ignore) if ignore else set()

        for id_, entry in self.read():
            ids.update(
                entry.load(self._identity, ignore=ids, delay=self._delay)
            )

        return ids


class VocabularyEntry:
    """Loading vocabulary superclass."""

    def __init__(self, service_str, directory, id_, entry):
        """Constructor."""
        self._dir = directory
        self._id = id_
        self._entry = entry
        self.service_str = service_str

    # Interface properties
    @property
    def covered_ids(self):
        """Just the id of the vocabulary covered by this entry as a list."""
        return [self._id]

    # Template methods
    def pre_load(self, identity, ignore):
        """Actions taken before iteratively creating records."""
        if self._id not in ignore:
            pid_type = self._entry['pid-type']
            current_service.create_type(identity, self._id, pid_type)

    def iterate(self, ignore):
        """Iterate over dicts of file content."""
        if self._id not in ignore:
            filepath = self._dir / self._entry["data-file"]
            for data in create_iterator(filepath):
                yield data

    def loaded(self):
        """Vocabularies actually loaded."""
        return [self._id]

    def load(self, identity, ignore=None, delay=False):
        """Template method design pattern for loading entries."""
        ignore = ignore or set()
        self.pre_load(identity, ignore=ignore)
        for data in self.iterate(ignore=ignore):
            self.create_record(data, delay=delay)
        return self.loaded()

    def create_record(self, data, delay=False):
        """Create the record."""
        if delay:
            create_vocabulary_record.delay(self.service_str, data)
        else:  # mostly for tests
            create_vocabulary_record(self.service_str, data)


class GenericVocabularyEntry(VocabularyEntry):
    """Vocabulary fixture with single data-file."""

    def __init__(self, directory, id_, entry):
        """Constructor."""
        super().__init__("vocabularies", directory, id_, entry)

    # Template methods
    def iterate(self, ignore):
        """Iterate over dicts of file content."""
        if self._id not in ignore:
            filepath = self._dir / self._entry["data-file"]
            for data in create_iterator(filepath):
                data['type'] = self._id
                yield data


class VocabularyEntryWithSchemes(VocabularyEntry):
    """Vocabulary fixture for specific vocabulary with schemes."""

    def __init__(self, service_str, directory, id_, entry):
        """Constructor."""
        super().__init__(service_str, directory, id_, entry)
        self._loaded = []

    # Template methods
    def pre_load(self, identity, ignore):
        """Actions taken before iteratively creating records."""
        for scheme in self.schemes():
            id_ = f"{self._id}.{scheme['id']}"
            if id_ not in ignore:
                self.create_scheme(scheme)

    def iterate(self, ignore):
        """Iterate over dicts of file content."""
        self._loaded = []

        for scheme in self.schemes():
            id_ = f"{self._id}.{scheme['id']}"
            if id_ not in ignore:
                self._loaded.append(id_)
                filepath = self._dir / scheme.get("data-file")
                yield from create_iterator(filepath)

    def loaded(self):
        """Vocabularies actually loaded."""
        return self._loaded

    # Other interface methods
    @property
    def covered_ids(self):
        """List of ids of the subvocabularies covered by this entry."""
        return [f"{s['id']}" for s in self.schemes()]

    # Helpers
    def schemes(self):
        """Return schemes."""
        return self._entry.get("schemes", [])

    def create_scheme(self, metadata):
        """Create the vocabulary scheme row."""
        id_ = metadata["id"]
        name = metadata.get("name", "")
        uri = metadata.get("uri", "")
        VocabularyScheme.create(
            id=id_, parent_id=self._id, name=name, uri=uri)
        db.session.commit()
