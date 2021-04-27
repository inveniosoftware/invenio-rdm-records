# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite DOI Provider."""

import logging

from datacite import DataCiteRESTClient
from flask import current_app
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus

from ..tasks import doi_datacite_delete, doi_datacite_register, \
    doi_datacite_update
from .base import BaseClient, BasePIDProvider


class DOIDataCiteClient(BaseClient):
    """DataCite Client.

    It Loads the values from config.
    """

    def __init__(self, name, url=None, config_key=None, **kwargs):
        """Constructor."""
        config_key = config_key or f"RDM_RECORDS_DOI_DATACITE"

        username = current_app.config.get(f"{config_key}_USERNAME")
        password = current_app.config.get(f"{config_key}_PASSWORD")
        prefix = current_app.config.get(f"{config_key}_PREFIX")
        test_mode = current_app.config.get(f"{config_key}_TEST_MODE", True)

        super().__init__(name, username, password, url=url, **kwargs)

        self.prefix = prefix
        self.test_mode = test_mode

    def has_credentials(self, **kwargs):
        """Returns if the client has the credentials properly set up."""
        return self.username and self.password and self.prefix


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
        self.api_client = None
        self.is_api_client_setup = False

        if client and client.has_credentials():
            self.api_client = DataCiteRESTClient(
                client.username, client.password,
                client.prefix, client.test_mode
            )
            self.is_api_client_setup = True

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

        try:
            pid = self.get(doi)
        except PIDDoesNotExistError:
            # not existing, create a new one
            return super().create(
                pid_value=doi,
                object_type="rec",
                object_uuid=record.id,
                **kwargs
            )

        # re-activate if previously deleted
        if pid.is_deleted():
            pid.sync_status(PIDStatus.NEW)
            return pid
        else:
            raise PIDAlreadyExists(self.pid_type, doi)

    def reserve(self, pid, record, **kwargs):
        """Constant True.

        It does not reserve locally, nor externally. This is to avoid storing
        many PIDs as cause of reserve/discard, which would then be soft
        deleted. Therefore we want to pass from status.NEW to status.RESERVED.
        :param pid: the PID to reserve.
        :param record: the record.
        :returns: `True`
        """
        return True

    def register(self, pid, record, url, **kwargs):
        """Register a DOI via the DataCite API.

        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is registered successfully.
        """
        local_success = super().register(pid, record)
        if not local_success:
            return False
        if self.is_api_client_setup:
            delay = \
                current_app.config["RDM_RECORDS_DOI_DATACITE_REGISTER_DELAY"]
            doi_datacite_register.apply_async(
                [record.pid.pid_value, self.client.name], countdown=delay)
        else:
            logging.warning("DataCite client not configured. " +
                            f"Cannot register DOI for {pid.pid_value}")

        return True

    def update(self, pid, record, url, **kwargs):
        """Update metadata associated with a DOI.

        This can be called before/after a DOI is registered.
        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is updated successfully.
        """
        # PIDS-FIXME: Do we want to log when reactivate the DOI
        # if pid.is_deleted():
        if self.is_api_client_setup:
            delay = \
                current_app.config["RDM_RECORDS_DOI_DATACITE_UPDATE_DELAY"]
            doi_datacite_update.apply_async(
                [record.pid.pid_value, self.client.name], countdown=delay)
        else:
            logging.warning("DataCite client not configured. " +
                            f"Cannot update DOI for {pid.pid_value}")

        if pid.is_deleted():
            return pid.sync_status(PIDStatus.REGISTERED)

        return True

    def delete(self, pid, record, **kwargs):
        """Delete/unregister a registered DOI.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, also it's deleted also remotely.
        :returns: `True` if is deleted successfully.
        """
        if self.is_api_client_setup:
            # this provider does not send NEW or RESERVED to datacite
            if pid.is_registered():
                delay = current_app.config[
                    "RDM_RECORDS_DOI_DATACITE_UPDATE_DELAY"]
                recid_value = record.pid.pid_value
                doi_value = pid.pid_value  # pid (func param) is a DOI

                doi_datacite_delete.apply_async(
                    [recid_value, doi_value, self.client.name],
                    countdown=delay
                )
        else:
            logging.warning("DataCite client not configured. " +
                            f"Cannot delete DOI for {pid.pid_value}")

        return super().delete(pid, record)

    def validate(self, identifier=None, provider=None, client=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). The first specifies if the
                  validation was passed successfully. The second one is an
                  array of error messages.
        """
        _, errors = super().validate(identifier, provider, client, **kwargs)

        if identifier and self.is_api_client_setup:
            try:
                self.api_client.check_doi(identifier)
            except ValueError as e:
                errors.append(str(e))

        return (True, []) if not errors else (False, errors)
