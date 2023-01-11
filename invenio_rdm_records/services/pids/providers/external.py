# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2023 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Base Provider."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_db import db

from .base import PIDProvider


class BlockedPrefixes:
    """Blocked prefixes validator."""

    def __init__(self, prefixes=None, config_names=None):
        """Initialize the prefixes."""
        self._config_names = config_names
        self._prefixes = prefixes or []

    @property
    def prefixes(self):
        """Get list of blocked prefixes."""
        _prefixes = []
        for name in self._config_names:
            val = current_app.config[name]
            if isinstance(val, str):
                _prefixes += [val]
            else:
                _prefixes += val
        return _prefixes + self._prefixes

    def __call__(self, record, identifier, provider, errors):
        """Validator call."""
        for p in self.prefixes:
            if identifier.startswith(p):
                errors.append(
                    _("The prefix '{prefix}' is administrated locally.").format(
                        prefix=p
                    )
                )
                # Bail early
                return


class ExternalPIDProvider(PIDProvider):
    """This provider is validates PIDs to unmanaged constraints.

    It does not support any other type of operation. However, it helps
    generalize the service code by using polymorphism.
    """

    def __init__(self, name, pid_type, validators=None, **kwargs):
        """Constructor."""
        super().__init__(name, pid_type=pid_type, managed=False, **kwargs)
        self._validators = validators or []

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
            error = self._insert_pid_type_error_msg(
                errors,
                _("Missing {scheme} for required field.").format(scheme=self.label),
            )

        for v in self._validators:
            # Not very pretty but keeps original functionality without touching
            # BlockedPrefixes
            error_msgs = []
            v(record, identifier, provider, error_msgs)
            if error_msgs:
                self._insert_pid_type_error_msg(errors, error_msgs)

        return (True, []) if not errors else (False, errors)

    def delete(self, pid, **kwargs):
        """Delete a persistent identifier."""
        # PID is in REGISTERED status and we don't want to keep it around, so
        # force delete the PID (only supported for NEW status in the API so we
        # circumvent the API interface here).
        with db.session.begin_nested():
            db.session.delete(pid)
        return True
