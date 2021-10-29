# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite DOI Provider."""

import json

from datacite import DataCiteRESTClient
from datacite.errors import DataCiteError
from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus

from invenio_rdm_records.resources.serializers import DataCite43JSONSerializer

from .base import BaseClient, BasePIDProvider


class DOIDataCiteClient(BaseClient):
    """DataCite Client.

    It Loads the values from config.
    """

    def __init__(self, name="datacite", url=None, config_key=None, **kwargs):
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
        """Returns if the client has the credentials properly set up.

        If the client is running on test mode the credentials are not required.
        """
        return self.username and self.password and self.prefix


class DOIDataCitePIDProvider(BasePIDProvider):
    """DataCite Provider class.

    Note that DataCite is only contacted when a DOI is reserved or
    registered, or any action posterior to it. Its creation happens
    only at PIDStore level.
    """

    name = "datacite"

    def __init__(self, client_cls, pid_type="doi",
                 default_status=PIDStatus.NEW, generate_id_func=None,
                 generate_doi_func=None, **kwargs):
        """Constructor."""
        super().__init__(pid_type=pid_type, default_status=default_status)

        self.client = client_cls()
        self.api_client = DataCiteRESTClient(
            self.client.username, self.client.password,
            self.client.prefix, self.client.test_mode
        )

        self.generate_id = generate_id_func or \
            DOIDataCitePIDProvider._generate_id

        default_generate_doi = self._generate_doi
        format_func = current_app.config['RDM_RECORDS_DOI_DATACITE_FORMAT']
        if format_func and callable(format_func):
            default_generate_doi = format_func
        self.generate_doi = generate_doi_func or default_generate_doi

    @staticmethod
    def _log_errors(errors):
        """Log errors from DataCiteError class."""
        # DataCiteError is a tuple with the errors on the first
        errors = json.loads(errors.args[0])["errors"]
        for error in errors:
            field = error["source"]
            reason = error["title"]
            current_app.logger.warning(f"Error in {field}: {reason}")

    @staticmethod
    def _generate_id(record, **kwargs):
        """Generate a unique DOI suffix.

        The content after the slash.
        """
        recid = record.pid.pid_value
        return f"{recid}"

    def _generate_doi(self, record, **kwargs):
        """Generate a unique DOI."""
        prefix = self.client.prefix
        id = self.generate_id(record, **kwargs)
        format_string = current_app.config['RDM_RECORDS_DOI_DATACITE_FORMAT']
        if format_string:
            return format_string.format(prefix=prefix, id=id)
        else:
            return f"{prefix}/datacite.{id}"

    def create(self, record, **kwargs):
        """Create a new unique DOI PID based on the record ID."""
        # managed provider should not receive a value
        assert not kwargs.get("value")

        doi = self.generate_doi(record, **kwargs)
        return super().create(record, value=doi, **kwargs)

    def register(self, pid, record, **kwargs):
        """Register a DOI via the DataCite API.

        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is registered successfully.
        """
        local_success = super().register(pid)
        if not local_success:
            return False

        try:
            doc = DataCite43JSONSerializer().dump_one(record)
            url = kwargs["url"]
            self.api_client.public_doi(
                metadata=doc, url=url, doi=pid.pid_value)
            return True
        except DataCiteError as e:
            current_app.logger.warning("DataCite provider error when "
                                       f"updating DOI for {pid.pid_value}")
            self._log_errors(e)

            return False

    def update(self, pid, record, url=None, **kwargs):
        """Update metadata associated with a DOI.

        This can be called before/after a DOI is registered.
        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is updated successfully.
        """
        # PIDS-FIXME: Do we want to log when reactivate the DOI
        try:
            # Set metadata
            doc = DataCite43JSONSerializer().dump_one(record)
            self.api_client.update_doi(
                metadata=doc, doi=pid.pid_value, url=url)
        except DataCiteError as e:
            current_app.logger.warning("DataCite provider error when "
                                       f"updating DOI for {pid.pid_value}")
            self._log_errors(e)

            return False

        if pid.is_deleted():
            return pid.sync_status(PIDStatus.REGISTERED)

        return True

    def delete(self, pid, **kwargs):
        """Delete/unregister a registered DOI.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, also it's deleted also remotely.
        :returns: `True` if is deleted successfully.
        """
        try:
            if pid.is_reserved():  # Delete only works for draft DOIs
                self.api_client.delete_doi(pid.pid_value)
            elif pid.is_registered():
                self.api_client.hide_doi(pid.pid_value)
        except DataCiteError as e:
            current_app.logger.warning("DataCite provider error when deleting "
                                       f"DOI for {pid.pid_value}")
            self._log_errors(e)

            return False

        return super().delete(pid, **kwargs)

    def validate(
        self, record, identifier=None, provider=None, **kwargs
    ):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). The first specifies if the
                  validation was passed successfully. The second one is an
                  array of error messages.
        """
        success, errors = super().validate(
            record, identifier, provider, **kwargs)

        # format check
        try:
            self.api_client.check_doi(identifier)
        except ValueError as e:
            errors.append(str(e))

        return (True, []) if not errors else (False, errors)

    def can_modify(self, pid, **kwargs):
        """Checks if the PID can be modified."""
        return not pid.is_registered() and not pid.is_reserved()
