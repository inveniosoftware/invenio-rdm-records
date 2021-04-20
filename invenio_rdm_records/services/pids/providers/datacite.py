# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite DOI Provider."""

from datacite import DataCiteRESTClient
from datacite.errors import DataCiteError
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from ....resources.serializers import DataCite43JSONSerializer
from .base import BaseClient, BasePIDProvider


class DOIDataCiteClient(BaseClient):
    """DataCite Client.

    It Loads the values from config.
    """

    def __init__(self, name, url=None, **kwargs):
        """Constructor."""
        # PIDS-FIXME: Rethink config loading
        config_key = f"{name.upper()}_DATACITE_CLIENT"

        super().__init__(
            name=name,
            username=current_app.config[f"{config_key}_USERNAME"],
            password=current_app.config[f"{config_key}_PASSWORD"],
            url=url,
            **kwargs
        )

        self.prefix = current_app.config[f"{config_key}_PREFIX"]
        self.test_mode = \
            current_app.config.get(f"{config_key}_TEST_MODE", True)


class DOIDataCitePIDProvider(BasePIDProvider):
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
        self.client = client
        self.api_client = DataCiteRESTClient(
            client.username, client.password, client.prefix, client.test_mode
        )

        super().__init__(self.api_client, pid_type, default_status)

        self.generate_suffix = generate_suffix_func or \
            DOIDataCitePIDProvider._generate_suffix
        self.generate_id = generate_id_func or self._generate_id

    @staticmethod
    def _generate_suffix(record, client, **kwargs):
        """Generate a unique DOI suffix.

        The content after the slash.
        """
        recid = record.pid.pid_value
        return f"{client.name}.{recid}"

    def _generate_id(self, record, **kwargs):
        """Generate a unique DOI."""
        prefix = self.client.prefix
        suffix = self.generate_suffix(record, self.client, **kwargs)
        return f"{prefix}/{suffix}"

    def create(self, record, **kwargs):
        """Create a new unique DOI PID based on the record ID."""
        doi = self.generate_id(record, **kwargs)
        return super().create(
            pid_value=doi,
            object_type="rec",
            object_uuid=record.id,
            **kwargs
        )

    def reserve(self, pid, record, **kwargs):
        """Reserve a DOI only in the local system.

        It does not reserve the DOI in DataCite.
        :param pid: the PID to reserve.
        :param record: the record.
        :returns: `True` if is reserved successfully.
        """
        super().reserve(pid, record)

        return True

    def register(self, pid, record, **kwargs):
        """Register a DOI via the DataCite API.

        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is registered successfully.
        """
        super().register(pid, record)
        # PIDS-FIXME: move to async task, exception handling included
        try:
            doc = DataCite43JSONSerializer().dump_one(record)
            self.api_client.public_doi(
                metadata=doc, url="PIDS-FIXME.com", doi=pid.pid_value)
        except DataCiteError:
            pass

        return True

    def update(self, pid, record, **kwargs):
        """Update metadata associated with a DOI.

        This can be called before/after a DOI is registered.
        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is updated successfully.
        """
        # PIDS-FIXME: Do we want to log when reactivate the DOI
        # if pid.is_deleted():
        try:
            # PIDS-FIXME: move to async task, exception handling included
            # Set metadata
            doc = DataCite43JSONSerializer().dump_one(record)
            self.api_client.update_doi(
                metadata=doc, doi=pid.pid_value, url=None)
        except DataCiteError:
            pass

        if pid.is_deleted():
            # PIDS-FIXME: Is this correct?
            pid.sync_status(PIDStatus.REGISTERED)

        return True

    def delete(self, pid, record, **kwargs):
        """Delete/unregister a registered DOI.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, also it's deleted also remotely.
        :returns: `True` if is deleted successfully.
        """
        # PIDS-FIXME: move to async task, exception handling included
        try:
            if pid.is_reserved():  # Delete only works for draft DOIs
                self.api_client.delete_doi(pid.pid_value)
            elif pid.is_registered():
                self.api_client.hide_doi(pid.pid_value)
        except DataCiteError:
            pass

        return super().delete(pid, record)

    def validate(self, identifier=None, provider=None, client=None, **kwargs):
        """Validate the attributes of the identifier."""
        super().validate(identifier, provider, client, **kwargs)
        if identifier:
            self.api_client.check_doi(identifier)
