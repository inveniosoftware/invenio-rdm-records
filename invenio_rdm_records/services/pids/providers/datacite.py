# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite DOI Provider."""

from datacite import DataCiteRESTClient
from datacite.errors import DataCiteError, HttpError
from invenio_pidstore.models import PIDStatus

from .base import BaseClient, BaseProvider


class DataCiteClient(BaseClient):
    """DataCite client."""

    def __init__(self, username, password, prefix, test_mode, **kwards):
        """Constructor."""
        super(DataCiteClient, self).__init__(username, password)
        self.prefix = prefix
        self.test_mode = test_mode


class DataCiteProvider(BaseProvider):
    """DataCite Provider class.

    Note that DataCite is only contacted when a DOI is reserved or
    registered, or any action posterior to it. Its creation happens
    only at PIDStore level.
    """

    def __init__(self, name, client, pid_type="doi",
                 default_status=PIDStatus.NEW, **kwargs):
        """Constructor."""
        self._client_credentials = client
        self.client = DataCiteRESTClient(
            client.username, client.password, client.prefix, client.test_mode
        )

        super(DataCiteProvider, self).__init__(
            name, client, pid_type, default_status)

    def reserve(self, record, pid):
        """Reserve a DOI (amounts to upload metadata, but not to mint).

        :param doc: Set metadata for DOI.
        :returns: `True` if is reserved successfully.
        """
        # Only registered PIDs can be updated.
        try:
            pid.reserve()
            self.client.draft_doi(metadata=record, doi=pid.pid_value)
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
            self.client.public_doi(metadata=record, doi=pid.pid_value)
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
            self.client.update_doi(metadata=record, doi=pid.pid_value)
        except (DataCiteError, HttpError):
            raise

        if pid.is_deleted():
            # PIDS-FIXME: Is this correct?
            pid.sync_status(PIDStatus.REGISTERED)

        return True

    def unregister(self, pid, **kwargs):
        """Delete/unregister a registered DOI.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, also it's deleted also remotely.
        :returns: `True` if is deleted successfully.
        """
        try:
            if pid.is_reserved():  # Delete only works for draft DOIs
                self.client.delete_doi(pid.pid_value)
            elif pid.is_registered():
                # First try external in case of errors
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
