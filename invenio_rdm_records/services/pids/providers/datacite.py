# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite DOI Provider."""

import json
import warnings

from datacite import DataCiteRESTClient
from datacite.errors import DataCiteError
from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_pidstore.models import PIDStatus

from invenio_rdm_records.resources.serializers import DataCite43JSONSerializer

from .base import PIDProvider


class DataCiteClient:
    """DataCite Client."""

    def __init__(self, name, config_prefix=None, **kwargs):
        """Constructor."""
        self.name = name
        self._config_prefix = config_prefix or "DATACITE"
        self._api = None

    def cfgkey(self, key):
        """Generate a configuration key."""
        return f"{self._config_prefix}_{key.upper()}"

    def cfg(self, key, default=None):
        """Get a application config value."""
        return current_app.config.get(self.cfgkey(key), default)

    def generate_doi(self, record):
        """Generate a DOI."""
        self.check_credentials()
        prefix = self.cfg("prefix")
        if not prefix:
            raise RuntimeError("Invalid DOI prefix configured.")
        doi_format = self.cfg("format", "{prefix}/{id}")
        if callable(doi_format):
            return doi_format(prefix, record)
        else:
            return doi_format.format(prefix=prefix, id=record.pid.pid_value)

    def check_credentials(self, **kwargs):
        """Returns if the client has the credentials properly set up.

        If the client is running on test mode the credentials are not required.
        """
        if not (self.cfg("username") and self.cfg("password") and self.cfg("prefix")):
            warnings.warn(
                f"The {self.__class__.__name__} is misconfigured. Please "
                f"set {self.cfgkey('username')}, {self.cfgkey('password')}"
                f" and {self.cfgkey('prefix')} in your configuration.",
                UserWarning,
            )

    @property
    def api(self):
        """DataCite REST API client instance."""
        if self._api is None:
            self.check_credentials()
            self._api = DataCiteRESTClient(
                self.cfg("username"),
                self.cfg("password"),
                self.cfg("prefix"),
                self.cfg("test_mode", True),
            )
        return self._api


class DataCitePIDProvider(PIDProvider):
    """DataCite Provider class.

    Note that DataCite is only contacted when a DOI is reserved or
    registered, or any action posterior to it. Its creation happens
    only at PIDStore level.
    """

    def __init__(
        self,
        id_,
        client=None,
        serializer=None,
        pid_type="doi",
        default_status=PIDStatus.NEW,
        **kwargs,
    ):
        """Constructor."""
        super().__init__(
            id_,
            client=(client or DataCiteClient("datacite", config_prefix="DATACITE")),
            pid_type=pid_type,
            default_status=default_status,
        )
        self.serializer = serializer or DataCite43JSONSerializer()

    @staticmethod
    def _log_errors(errors):
        """Log errors from DataCiteError class."""
        # DataCiteError is a tuple with the errors on the first
        errors = json.loads(errors.args[0])["errors"]
        for error in errors:
            field = error["source"]
            reason = error["title"]
            current_app.logger.warning(f"Error in {field}: {reason}")

    def generate_id(self, record, **kwargs):
        """Generate a unique DOI."""
        # Delegate to client
        return self.client.generate_doi(record)

    def can_modify(self, pid, **kwargs):
        """Checks if the PID can be modified."""
        return not pid.is_registered() and not pid.is_reserved()

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
            doc = self.serializer.dump_one(record)
            url = kwargs["url"]
            self.client.api.public_doi(metadata=doc, url=url, doi=pid.pid_value)
            return True
        except DataCiteError as e:
            current_app.logger.warning(
                "DataCite provider error when " f"registering DOI for {pid.pid_value}"
            )
            self._log_errors(e)

            return False

    def update(self, pid, record, url=None, **kwargs):
        """Update metadata associated with a DOI.

        This can be called before/after a DOI is registered.
        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is updated successfully.
        """
        try:
            # Set metadata
            doc = self.serializer.dump_one(record)
            self.client.api.update_doi(metadata=doc, doi=pid.pid_value, url=url)
        except DataCiteError as e:
            current_app.logger.warning(
                "DataCite provider error when " f"updating DOI for {pid.pid_value}"
            )
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
                self.client.api.delete_doi(pid.pid_value)
            elif pid.is_registered():
                self.client.api.hide_doi(pid.pid_value)
        except DataCiteError as e:
            current_app.logger.warning(
                "DataCite provider error when deleting " f"DOI for {pid.pid_value}"
            )
            self._log_errors(e)

            return False

        return super().delete(pid, **kwargs)

    def validate(self, record, identifier=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). The first specifies if the
                  validation was passed successfully. The second one is an
                  array of error messages.
        """
        _, errors = super().validate(record, identifier, provider, **kwargs)

        # Format check
        try:
            self.client.api.check_doi(identifier)
        except ValueError as e:
            errors.append(str(e))

        return (True, []) if not errors else (False, errors)
