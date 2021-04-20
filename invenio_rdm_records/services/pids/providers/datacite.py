# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite DOI Provider."""

from datacite import DataCiteRESTClient
from datacite.errors import DataCiteError, HttpError
from flask import current_app
from invenio_pidstore.models import PIDStatus

from ....resources.serializers import DataCite43JSONSerializer
from .base import BaseClient, BasePIDProvider


class DataCiteClient(BaseClient):
    """DataCite Client.

    It Loads the values from config.
    """

    def __init__(self, name, username, password, prefix, test_mode, **kwards):
        """Constructor."""
        self.name = name
        name = self.name.upper()
        self.prefix = current_app.config[f"{name}_DATACITE_CLIENT_PREFIX"],
        self.test_mode = \
            current_app.config.getf("{name}_DATACITE_CLIENT_TEST_MODE", True),

        super(DataCiteClient, self).__init__(
            username=current_app.config[f"{name}_DATACITE_CLIENT_USERNAME"],
            password=current_app.config[f"{name}_DATACITE_CLIENT_PASSWORD"],
        )


class DataCitePIDProvider(BasePIDProvider):
    """DataCite Provider class.

    Note that DataCite is only contacted when a DOI is reserved or
    registered, or any action posterior to it. Its creation happens
    only at PIDStore level.
    """

    name = "datacite"

    def __init__(self, client, pid_type="doi",
                 default_status=PIDStatus.NEW, generate_suffix_func=None,
                 generate_id_func=None, **kwargs):
        """Constructor."""
        self._client_credentials = client
        self.client = DataCiteRESTClient(
            client.username, client.password, client.prefix, client.test_mode
        )

        super(DataCitePIDProvider, self).__init__(
            self.client, pid_type, default_status)

        self.generate_suffix = generate_suffix_func or self._generate_suffix
        self.generate_id = generate_id_func or self._generate_id

    def _generate_suffix(self, recid, **kwargs):
        """Generate DOI suffix.

        The content after the slash.
        """
        return f"{self._client_credentials.name}.{recid}"

    def _generate_id(self, recid, **kwargs):
        """Generate a DOI."""
        prefix = self.client.prefix
        # subs by name attr of self
        return f"{prefix}/{self.generate_suffix(recid, **kwargs)}"

    def create(self, recid, **kwargs):
        """Create a new DOI PID based on the record ID."""
        pid_value = self.generate_id(recid, **kwargs)
        return super().create(pid_value=pid_value, **kwargs)

    def reserve(self, record, pid):
        """Reserve a DOI (amounts to upload metadata, but not to mint).

        :param doc: Set metadata for DOI.
        :returns: `True` if is reserved successfully.
        """
        # Only registered PIDs can be updated.
        try:
            pid.reserve()
            doc = DataCite43JSONSerializer.serialize_object(record)
            self.client.draft_doi(metadata=doc, doi=pid.pid_value)
        except (DataCiteError, HttpError):
            raise

        return True

    def register(self, record, pid, **kwargs):
        """Register a DOI via the DataCite API.

        :param record: Record with the metadata for the DOI.
        :returns: `True` if is registered successfully.
        """
        try:
            pid.register()
            # Set metadata for DOI
            doc = DataCite43JSONSerializer.serialize_object(record)
            self.client.public_doi(
                metadata=doc, url="PIDS-FIXME.com", doi=pid.pid_value)
        except (DataCiteError, HttpError):
            # PIDS-FIXME: PIDSTore logs, but invenio has almost no logs
            # A custom exception maybe better?
            raise

        return True

    def update(self, record, pid, **kwargs):
        """Update metadata associated with a DOI.

        This can be called before/after a DOI is registered.
        :param doc: Set metadata for DOI.
        :returns: `True` if is updated successfully.
        """
        # PIDS-FIXME: Do we want to log when reactivate the DOI
        # if pid.is_deleted():
        try:
            # Set metadata
            doc = DataCite43JSONSerializer.serialize_object(record)
            self.client.update_doi(
                metadata=doc, doi=pid.pid_value, url=None)
        except (DataCiteError, HttpError):
            raise

        if pid.is_deleted():
            # PIDS-FIXME: Is this correct?
            pid.sync_status(PIDStatus.REGISTERED)

        return True

    def delete(self, pid, **kwargs):
        """Delete/unregister a registered DOI.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, also it's deleted also remotely.
        :returns: `True` if is deleted successfully.
        """
        try:
            if pid.is_reserved():  # Delete only works for draft DOIs
                self.client.delete_doi(pid.pid_value)
            elif pid.is_registered():
                self.client.hide_doi(pid.pid_value)
            # In any case gets deleted locally (New, Reserved or Registered)
            pid.delete()
        except (DataCiteError, HttpError):
            raise

        return True

    def validate(self, pid_attrs, **kwargs):
        """Validate the attributes of the identifier."""
        # PIDS-FIXME: Anything needed here
        pass
