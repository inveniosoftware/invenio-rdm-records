# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2023 Northwestern University.
# SPDX-FileCopyrightText: 2023-2024 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""PID Base Provider."""

from flask import current_app
from invenio_db import db
from invenio_i18n import lazy_gettext as _

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

        if errors and identifier and self._link_existing_record:
            self._name_existing_record(errors, record, identifier)

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

    def _existing_record_url(self, record, identifier):
        """Return the URL of the readable published record using the identifier."""
        return None

    def _name_existing_record(self, errors, record, identifier):
        """Replace the "already exists" message with one linking the record."""
        url = self._existing_record_url(record, identifier)
        if not url:
            return

        default_msg = str(
            _(
                "%(pid_type)s:%(identifier)s already exists.",
                pid_type=self.pid_type,
                identifier=identifier,
            )
        )
        new_msg = _(
            "%(scheme)s %(identifier)s is already used by the record %(url)s.",
            scheme=self.label,
            identifier=identifier,
            url=url,
        )
        for error in errors:
            error["messages"] = [
                new_msg if str(m) == default_msg else m for m in error["messages"]
            ]

    def delete(self, pid, **kwargs):
        """Delete a persistent identifier."""
        # PID is in REGISTERED status and we don't want to keep it around, so
        # force delete the PID (only supported for NEW status in the API so we
        # circumvent the API interface here).
        with db.session.begin_nested():
            db.session.delete(pid)
        return True
