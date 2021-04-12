# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Base Provider."""

from invenio_pidstore.models import PersistentIdentifier, PIDStatus


class BaseClient:
    """PID Client base class."""

    def __init__(self, username, password, url=None, **kwards):
        """Constructor."""
        self.username = username
        self.password = password
        self.url = url


class BaseProvider:
    """Base Provider class."""

    def _generate_id(self, **kwargs):
        """Generates an identifier value."""
        raise NotImplementedError

    def __init__(self, name, client=None, pid_type=None,
                 default_status=PIDStatus.NEW, system_managed=True, **kwargs):
        """Constructor."""
        self.name = name
        self.client = client
        self.pid_type = pid_type
        self.default_status = default_status
        self.system_managed = system_managed

    def is_managed(self):
        """Returns if the PIDs from the provider are managed by the system.

        This helps differentiate external providers.
        """
        return self.system_managed

    def get(self, pid_value, pid_type=None, **kwargs):
        """Get a persistent identifier for this provider.

        :param pid_type: Persistent identifier type. (Default: configured
            :attr:`invenio_pidstore.providers.base.BaseProvider.pid_type`)
        :param pid_value: Persistent identifier value.
        :param kwargs: See
            :meth:`invenio_pidstore.providers.base.BaseProvider` required
            initialization properties.
        :returns: A :class:`invenio_pidstore.models.base.PersistentIdentifier`
            instance.
        """
        return PersistentIdentifier.get(pid_type or self.pid_type, pid_value,
                                        pid_provider=self.name, **kwargs)

    def create(self, pid_value=None, pid_type=None, object_type=None,
               object_uuid=None, **kwargs):
        """Create a new instance for the given type and pid.

        :param pid_value: Persistent identifier value. (Default: None).
        :param pid_type: Persistent identifier type. (Default: None).
        :param status: Status for the created PID (Default:
            :attr:`invenio_pidstore.models.PIDStatus.NEW`).
        :param object_type: The object type is a string that identify its type.
            (Default: None).
        :param object_uuid: The object UUID. (Default: None).
        :returns: A :class:`invenio_pidstore.models.PersistentIdentifier`
            instance.
        """
        pid_type = pid_type or self.pid_type
        assert pid_type

        pid_value = pid_value or self._generate_id(**kwargs)
        assert pid_value

        status = status or self.default_status
        assert status

        return PersistentIdentifier.create(
            pid_type,
            pid_value,
            pid_provider=self.name,
            object_type=object_type,
            object_uuid=object_uuid,
            status=status,
        )

    def reserve(self, pid, **kwargs):
        """Reserve a persistent identifier.

        This might or might not be useful depending on the service of the
        provider.
        See: :meth:`invenio_pidstore.models.PersistentIdentifier.reserve`.
        """
        return pid.reserve()

    def register(self, pid, **kwargs):
        """Register a persistent identifier.

        See: :meth:`invenio_pidstore.models.PersistentIdentifier.register`.
        """
        return pid.register()

    def update(self, record, pid, **kwargs):
        """Update information about the persistent identifier."""
        pass

    def delete(self, pid, **kwargs):
        """Delete a persistent identifier.

        See: :meth:`invenio_pidstore.models.PersistentIdentifier.delete`.
        """
        return pid.delete()

    def get_status(self, identifier, **kwargs):
        """Get the status of the identifier."""
        return self.get(identifier).status

    def validate(self, pid_attrs, **kwargs):
        """Validate the attributes of the identifier."""
        return True
