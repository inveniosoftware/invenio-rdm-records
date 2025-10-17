# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2025 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Crossref DOI Provider."""

import io
import warnings
from collections import ChainMap
from time import time

import requests
from commonmeta import dig, validate_prefix
from flask import current_app
from idutils import is_doi
from invenio_access.permissions import system_identity
from invenio_communities import current_communities
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PIDStatus
from requests_toolbelt.multipart.encoder import MultipartEncoder

from ....resources.serializers import CrossrefXMLSerializer
from .base import PIDProvider


class CrossrefClient:
    """Crossref Client."""

    def __init__(self, name, config_prefix=None, config_overrides=None, **kwargs):
        """Constructor."""
        self.name = name
        self._config_prefix = config_prefix or "CROSSREF"
        self._config_overrides = config_overrides or {}

        # Set reasonable defaults
        self.timeout = 30
        self.test_mode = False

        # Set API URL based on test mode
        if self.test_mode:
            self.api_url = "https://test.crossref.org/servlet/deposit"
        else:
            self.api_url = "https://doi.crossref.org/servlet/deposit"

    def cfgkey(self, key):
        """Generate a configuration key."""
        return f"{self._config_prefix}_{key.upper()}"

    def cfg(self, key, default=None):
        """Get a application config value."""
        config = ChainMap(self._config_overrides, current_app.config)
        return config.get(self.cfgkey(key), default)

    def check_credentials(self, **kwargs):
        """Check if the client has the credentials properly set up.

        :returns: True if credentials are properly configured, False otherwise.
        """
        if (
            not self.cfg("username")
            or not self.cfg("password")
            or not self.cfg("prefixes")
            or not len(self.cfg("prefixes")) > 0
            or not self.cfg("depositor")
            or not self.cfg("email")
            or not self.cfg("registrant")
        ):
            current_app.logger.error(
                f"CrossrefClient configuration incomplete: missing configuration settings. "
                f"Required: {self.cfgkey('username')}, <password>, {self.cfgkey('prefixes')}, "
                f"{self.cfgkey('depositor')}, {self.cfgkey('email')}, {self.cfgkey('registrant')}"
            )
            warnings.warn(
                f"The {self.__class__.__name__} is misconfigured. Please "
                f"set {self.cfgkey('username')}, <password> and {self.cfgkey('prefixes')}, "
                f"{self.cfgkey('depositor')}, {self.cfgkey('email')}, {self.cfgkey('registrant')} in your configuration.",
                UserWarning,
            )
            return False

        return True

    def generate_doi(self, record, **kwargs):
        """Generate a DOI. Uses the DOI prefix of the default community custom_field.

        :param record: The record for which to generate a DOI.
        :returns: Generated DOI string.
        :raises RuntimeError: If credentials or prefixes are not configured.
        """
        if not self.check_credentials():
            raise RuntimeError("Crossref client credentials not properly configured.")

        # Determine prefix to use
        prefixes = self.cfg("prefixes")
        default_community = dig(record, "communities.default")

        prefix = None
        if len(prefixes) > 1 and default_community:
            try:
                # Fetch default community and get DOI prefix custom field
                community = current_communities.service.read(
                    identity=system_identity, id_=default_community
                )
                community_prefix = dig(community.data, "custom_fields.rs:prefix")
                if community_prefix and community_prefix in [str(p) for p in prefixes]:
                    prefix = str(community_prefix)
                    current_app.logger.debug(
                        f"Using DOI prefix: {prefix} for community: {default_community}"
                    )

            except Exception as e:
                current_app.logger.warning(
                    f"Failed to fetch community metadata for {default_community}: {type(e).__name__}: {str(e)}"
                )

        if not prefix:
            # Fallback to first configured prefix
            prefix = str(prefixes[0])

        doi_format = self.cfg("format", "{prefix}/{id}")

        if callable(doi_format):
            return doi_format(prefix, record)
        else:
            # Ensure we have a valid record ID
            record_id = getattr(record, "pid", None)
            if record_id and hasattr(record_id, "pid_value"):
                return f"{prefix}/{record_id.pid_value}"
            elif hasattr(record, "id"):
                return f"{prefix}/{record.id}"
            else:
                raise RuntimeError("Cannot generate DOI: record has no valid ID.")

    def deposit(self, input_xml):
        """Upload metadata for a new or existing DOI.

        :param input_xml: XML metadata following the Crossref Metadata Schema (str or bytes).
        :return: Status string ('SUCCESS' or 'ERROR' on failure).
        :raises RuntimeError: If credentials are not configured.
        """
        if not self.check_credentials():
            raise RuntimeError("Crossref client credentials not properly configured.")

        try:
            # Convert string to bytes if necessary
            if isinstance(input_xml, str):
                input_xml = input_xml.encode("utf-8")

            # The filename displayed in the Crossref admin interface
            filename = f"{int(time())}"

            multipart_data = MultipartEncoder(
                fields={
                    "fname": (filename, io.BytesIO(input_xml), "application/xml"),
                    "operation": "doMDUpload",
                    "login_id": self.cfg("username"),
                    "login_passwd": self.cfg("password"),
                }
            )
            headers = {"Content-Type": multipart_data.content_type}

            # Make the request
            resp = requests.post(
                self.api_url, data=multipart_data, headers=headers, timeout=self.timeout
            )

            # Check for HTTP errors
            resp.raise_for_status()

            # Log response details
            current_app.logger.debug(
                f"CrossrefClient.deposit: HTTP response status: {resp.status_code}"
            )

            # Parse response to check for success/failure
            response_text = resp.text.strip()
            if "SUCCESS" in response_text:
                return "SUCCESS"
            else:
                current_app.logger.error(
                    f"CrossrefClient.deposit: Deposit may have failed - no SUCCESS in response: {response_text}"
                )
                return "ERROR"

        except requests.Timeout as e:
            current_app.logger.error(
                f"CrossrefClient.deposit: Timeout error after {self.timeout}s",
                exc_info=e,
            )
            return "ERROR"
        except requests.RequestException as e:
            current_app.logger.error(
                f"CrossrefClient.deposit: Request error - {type(e).__name__}: {str(e)}",
                exc_info=e,
            )
            return "ERROR"
        except ValueError as e:
            current_app.logger.error(
                f"CrossrefClient.deposit: Input validation error: {e}"
            )
            return "ERROR"
        except Exception as e:
            current_app.logger.error(
                f"CrossrefClient.deposit: Unexpected error - {type(e).__name__}: {str(e)}",
                exc_info=e,
            )
            return "ERROR"

    def validate_doi(self, doi):
        """Validate if a DOI is valid and uses an allowed prefix.

        :param doi: DOI string to validate.
        :returns: True if valid, False otherwise.
        """
        if not doi or not is_doi(doi):
            current_app.logger.error(
                f"CrossrefClient.validate_doi: DOI format invalid or empty: {doi}"
            )
            return False

        try:
            doi_prefix = validate_prefix(doi)
            prefixes = self.cfg("prefixes", [])
            return doi_prefix in [str(p) for p in prefixes]
        except Exception as e:
            current_app.logger.error(
                f"CrossrefClient.validate_doi: Exception during validation: {type(e).__name__}: {str(e)}"
            )
            return False


class CrossrefPIDProvider(PIDProvider):
    """Crossref Provider class.

    Note that Crossref is only contacted when a DOI is registered, or any action
    posterior to it. Its creation happens only at the PIDStore level.
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
        # Note: Cannot use current_app.logger here as Flask context may not be available during module import
        # Logging will occur in methods when Flask context is available

        super().__init__(
            id_,
            client=(client or CrossrefClient("crossref", config_prefix="CROSSREF")),
            pid_type=pid_type,
            default_status=default_status,
        )
        self.serializer = serializer or CrossrefXMLSerializer()

    def generate_id(self, record, **kwargs):
        """Generate a unique DOI, delegating to the client."""
        return self.client.generate_doi(record, **kwargs)

    @classmethod
    def is_enabled(cls, app):
        """Determine if crossref is enabled or not."""
        return app.config.get("CROSSREF_ENABLED", False)

    def can_modify(self, pid, **kwargs):
        """Checks if the PID can be modified."""
        return not pid.is_registered()

    def register(self, pid, record, **kwargs):
        """Register metadata with the Crossref XML API.

        :param pid: the PID to register.
        :param record: the record metadata for the DOI.
        :returns: `True` if is registered successfully.
        """
        local_success = super().register(pid)
        if not local_success:
            return False

        try:
            doc = self.serializer.dump_obj(record)
            self.client.deposit(doc)
            return True
        except Exception as e:
            current_app.logger.error(
                f"CrossrefPIDProvider.register: Error registering DOI {pid.pid_value}: {type(e).__name__}: {str(e)}",
                exc_info=e,
            )
            return False

    def update(self, pid, record, url=None, **kwargs):
        """Update metadata with the Crossref XML API.

        :param pid: the PID to update.
        :param record: the record metadata for the DOI.
        :returns: `True` if is updated successfully.
        """
        try:
            doc = self.serializer.dump_obj(record)
            self.client.deposit(doc)
            return True
        except Exception as e:
            current_app.logger.error(
                f"CrossrefPIDProvider.update: Error updating DOI {pid.pid_value}: {type(e).__name__}: {str(e)}",
                exc_info=e,
            )
            return False

    def delete(self, pid, **kwargs):
        """Delete/unregister a registered DOI.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, also it's deleted also remotely.
        :returns: `True` if is deleted successfully.
        """
        try:
            if pid.is_reserved():  # Delete only works for draft DOIs
                current_app.logger.error(
                    f"CrossrefPIDProvider.delete: Not implemented - deleting reserved DOI {pid.pid_value}"
                )
            elif pid.is_registered():
                current_app.logger.error(
                    f"CrossrefPIDProvider.delete: Not implemented - deleting registered DOI {pid.pid_value}"
                )
        except Exception as e:
            current_app.logger.error(
                f"CrossrefPIDProvider.delete: Unexpected error when deleting DOI {pid.pid_value}: {type(e).__name__}: {str(e)}",
                exc_info=e,
            )
            return False

        result = super().delete(pid, **kwargs)
        current_app.logger.debug(
            f"CrossrefPIDProvider.delete: Local deletion result for {pid.pid_value}: {result}"
        )
        return result

    def validate(self, record, identifier=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). `success` is a bool that specifies
                  if the validation was successful. `errors` is a list of
                  error dicts of the form:
                  `{"field": <field>, "messages: ["<msgA1>", ...]}`.
        """
        errors = []

        try:
            # Validate DOI. Should be a valid DOI with an enabled prefix.
            if (
                not identifier
                or not is_doi(identifier)
                or validate_prefix(identifier) not in self.client.cfg("prefixes")
            ):
                errors.append(
                    {
                        "field": "pids.identifier.doi",
                        "messages": [_("Missing or invalid DOI for registration.")],
                    }
                )

            success = errors == []

            return success, errors

        except Exception as e:
            current_app.logger.error(
                f"CrossrefPIDProvider.validate: Unexpected error during validation: {type(e).__name__}: {str(e)}",
                exc_info=e,
            )
            return False, [
                {"field": "general", "messages": ["Validation error occurred"]}
            ]

    def create_and_reserve(self, record, **kwargs):
        """Create and reserve a DOI for the given record, and update the record with the reserved DOI."""
        if "doi" not in record.pids:
            pid = self.create(record)
            self.reserve(pid, record=record)
            pid_attrs = {"identifier": pid.pid_value, "provider": self.name}
            if self.client:
                pid_attrs["client"] = self.client.name
            record.pids["doi"] = pid_attrs
