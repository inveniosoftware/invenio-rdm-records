# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2023 Northwestern University.
# SPDX-FileCopyrightText: 2023-2024 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""PID Base Provider."""

from flask import current_app, g
from invenio_db import db
from invenio_i18n import lazy_gettext as _
from sqlalchemy.orm.exc import NoResultFound

from .base import PIDProvider


class BlockedPrefixes:
    """Blocked prefixes validator."""

    def __init__(self, prefixes=None, config_names=None):
        """Initialize the prefixes."""
        self._config_names = config_names
        self._prefixes = prefixes or []

    @property
    def prefixes(self):
        """Get list of blocked prefixes. Can be string, list or dict in config.

        Do not include empty strings.
        """
        _prefixes = []
        for name in self._config_names:
            val = current_app.config[name]
            if isinstance(val, str):
                _prefixes += [val]
            elif isinstance(val, dict):
                _prefixes += list(val.values())
            else:
                _prefixes += val
        return [prefix for prefix in _prefixes + self._prefixes if prefix]

    def __call__(self, record, identifier, provider, errors):
        """Validator call. Validate the identifier as non-empty and against the blocked prefixes."""
        for p in self.prefixes:
            if p and identifier.startswith(p):
                errors.append(
                    _(
                        "The prefix '%(prefix)s' is managed by %(sitename)s. Please supply an external DOI or select 'No' to have a DOI generated for you.",
                        prefix=p,
                        sitename=current_app.config["THEME_SITENAME"],
                    )
                )
                # Bail early
                return


class ExternalPIDProvider(PIDProvider):
    """This provider is validates PIDs to unmanaged constraints.

    It does not support any other type of operation. However, it helps
    generalize the service code by using polymorphism.

    :param link_existing_record: if ``True``, a duplicate identifier error
        names (with its URL) the published record already using the
        identifier, provided the current identity is allowed to read it.
        Disabled by default so that the existence of restricted records is
        not disclosed.
    """

    def __init__(
        self,
        name,
        pid_type,
        validators=None,
        link_existing_record=False,
        **kwargs,
    ):
        """Constructor."""
        super().__init__(name, pid_type=pid_type, managed=False, **kwargs)
        self._validators = validators or []
        self._link_existing_record = link_existing_record

    @classmethod
    def is_enabled(cls, app):
        """Determine if datacite is enabled or not."""
        # TODO: not used at the moment, but this should be implemented when the
        # ui distinguish between datacite and external doi's
        return NotImplementedError

    def validate(self, record, identifier=None, provider=None, client=None, **kwargs):
        """Validate the pid attributes and record.

        :returns: A tuple (success, errors). `success` is a bool that specifies
                  if the validation was successful. `errors` is a list of
                  error dicts of the form:
                  `{"field": <field>, "messages: ["<msgA1>", ...]}`.
        """
        if client:
            current_app.logger.error(
                "Configuration error: client attribute not supported for "
                f"provider {self.name}"
            )
            raise  # configuration error

        success, errors = super().validate(record, identifier, provider, **kwargs)

        if not identifier:
            self._insert_pid_type_error_msg(
                errors,
                _("Missing %(scheme)s for required field.", scheme=self.label),
            )

        for v in self._validators:
            # Not very pretty but keeps original functionality without touching
            # BlockedPrefixes
            error_msgs = []
            v(record, identifier, provider, error_msgs)
            if error_msgs:
                self._insert_pid_type_error_msg(errors, error_msgs)

        return (True, []) if not errors else (False, errors)

    def _existing_record_url(self, pid):
        """Return the URL of the readable published record holding the PID."""
        # There is no identity outside a request (e.g. in scripts or tasks).
        identity = getattr(g, "identity", None)
        if identity is None or not pid.object_uuid:
            return None

        # Imported here to avoid a circular import.
        from invenio_rdm_records.proxies import current_rdm_records_service

        service = current_rdm_records_service
        try:
            with db.session.no_autoflush:
                # Drafts live in a different table, so they are not found here.
                existing = service.record_cls.get_record(pid.object_uuid)
            if not service.check_permission(identity, "read", record=existing):
                return None
            links = service.links_item_tpl.expand(identity, existing)
            return links.get("self_html")
        except NoResultFound:
            return None

    def _duplicate_error_message(self, pid, identifier):
        """Return the duplicate error, naming the existing record if allowed."""
        message = super()._duplicate_error_message(pid, identifier)
        if not self._link_existing_record:
            return message

        url = self._existing_record_url(pid)
        if not url:
            return message

        return _(
            "%(scheme)s %(identifier)s is already used by the record %(url)s",
            scheme=self.label,
            identifier=identifier,
            url=url,
        )

    def delete(self, pid, **kwargs):
        """Delete a persistent identifier."""
        # PID is in REGISTERED status and we don't want to keep it around, so
        # force delete the PID (only supported for NEW status in the API so we
        # circumvent the API interface here).
        with db.session.begin_nested():
            db.session.delete(pid)
        return True
