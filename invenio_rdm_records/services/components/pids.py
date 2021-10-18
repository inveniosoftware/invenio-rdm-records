# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for pids."""
from invenio_drafts_resources.services.records.components import \
    ServiceComponent
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from ...proxies import current_rdm_records
from ..pids.errors import PIDTypeNotSupportedError
from ..pids.tasks import register_or_update_pid


class PIDsComponent(ServiceComponent):
    """Service component for pids."""

    def _validate_pids_schemes(self, pids):
        """Validate the pid schemes are supported by the service.

        This would only fail on the REST API or a misconfigured web UI.
        The marshmallow schema validates that the structure of the data is
        correct. This function validates that the given pids are actually
        supported.
        """
        pids_providers = set(self.service.config.pids_providers.keys())
        all_pids = set(pids.keys())
        unknown_pids = all_pids - pids_providers
        if unknown_pids:
            raise PIDTypeNotSupportedError(unknown_pids)

    def _validate_pids(self, pids, record, errors):
        """Validate an iterator of PIDs.

        This function assumes all pid types are supported by the system.
        """
        for scheme, pid in pids.items():
            provider_name = pid.get("provider")
            provider = self.service.pids.get_provider(scheme, provider_name)
            success, val_errors = provider.validate(record=record, **pid)
            if not success:
                errors.append({
                    "field": f"pids.{scheme}",
                    "message": val_errors
                })

    # hook methods
    def create(self, identity, data=None, record=None,  errors=None):
        """This method is called on draft creation.

        It should validate and add the pids to the draft.
        """
        pids = data.get('pids', {})
        self._validate_pids_schemes(pids)
        self._validate_pids(pids, record, errors)
        # the record is a draft
        record.pids = pids

    def new_version(self, identity, draft=None, record=None):
        """A new draft should not have any pids from the previous record."""
        draft.pids = {}

    def _create_and_spawn_register(
        self, draft, scheme, value=None, provider_name=None
    ):
        """Creates (reserves) a PID and spawns a task to register it."""
        #
        #            |          value          |           no value          |
        # |----------|-------------------------|-----------------------------|
        # | managed  |     reserve+register*   |   create+reserve+register   |
        # |----------|-------------------------|-----------------------------|
        # | external | create+reserve+register |             fail            |
        # |----------|-------------------------|-----------------------------|
        #
        # * in case of a draft of published record (edit) this step is skipped

        provider = self.service.pids.get_provider(scheme, provider_name)
        # FIXME: validation should happen at marshmallow level
        if not provider.is_managed() and not value:
            raise ValidationError(
                message="External identifier value is required.",
                field_name=f"pids.{scheme}"
            )
        elif (not provider.is_managed() and value) or \
                (provider.is_managed() and not value):
            args = {"record": draft, "status": PIDStatus.RESERVED}
            if value:
                args["value"] = value
            pid = provider.create(**args)
            provider.reserve(pid, record=draft)
        else:  # managed and value, i.e. an already created pid, needs reserve
            # TODO: What should happen if via REST a non existing pid is sent
            pid = provider.get(pid_value=value, pid_type=scheme)
            if pid.is_deleted():  # in case of previous inactivation
                pid = provider.create(record=draft, value=pid.pid_value)
            if pid.is_new():  # not reserved and not registered
                provider.reserve(pid, record=draft)

        pid_attrs = {
            "identifier": pid.pid_value,
            "provider": provider.name,
        }
        if provider.client:
            pid_attrs["client"] = provider.client.name

        return pid_attrs

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        record_pids = {}
        draft_pids = draft.get('pids', {})

        # FIXME: this should be moved to marshmallow level
        # validation happens before to be able to fail before reserving pids
        # it means a double looping but validation should eventually be moved
        # to marshmallow see invenio-rdm-records/issues/796
        errors = []
        self._validate_pids_schemes(draft_pids)
        self._validate_pids(draft_pids, record, errors)
        if errors:
            raise ValidationError(message=errors)

        # loop through given pids
        for scheme, pid in draft_pids.items():
            provider_name = pid.get("provider")
            identifier_value = pid.get("identifier")
            record_pids[scheme] = self._create_and_spawn_register(
                draft, scheme, identifier_value, provider_name
            )

        # get mandatory pids, using default provider
        # if the pid was not in the pids field one will be created using the
        # default provider
        pids_required = self.service.config.pids_required
        for scheme in pids_required:
            if not draft_pids.get(scheme):
                # FIXME: Should fail if required and external but no value
                record_pids[scheme] = self._create_and_spawn_register(
                    draft, scheme
                )

        record.pids = record_pids

    # the delete hook is not implemented because record deletion is
    # forbidden by permissions. In addition, the flow to when/how delete a
    # reserved/registered pid is not trivial. It is dealt with by the
    # inactivate function at pids service level
    def delete_draft(self, identity, draft=None, record=None, force=False):
        """This method deletes PIDs of a draft.

        It should only delete pids with status `NEW`, other pids would
        belong to previous versions of the record.
        """
        pids = draft.get('pids', {})
        for scheme, pid_attrs in pids.items():
            provider_name = pid_attrs.get("provider")
            provider = self.service.pids.get_provider(scheme, provider_name)
            try:
                pid = provider.get(pid_value=pid_attrs["identifier"])
                # FIXME: should check returned value and log ig deletion failed
                # pids should be status NEW at this point
                if pid.is_new():
                    provider.delete(pid, record=draft)
            except PIDDoesNotExistError:
                pass  # pid was not saved to pidstore yet, no deletion needed

    def _remove_if_created(
        self, pid_value, pid_type, pid_provider, record=None
    ):
        """Deletes a PID if it has been created/reserved."""
        if pid_value:  # e.g. ask to remove an external and incomplete pid
            provider = self.service.pids.get_provider(pid_type, pid_provider)
            try:
                pid = provider.get(pid_value=pid_value)
                provider.delete(pid, record=record)
            except PIDDoesNotExistError:
                pass  # if it does not exist, it does not need to be deleted

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Update draft handler.

        The permission check is performed on pid updates, no new additions.
        In addition, they check only if it is allowed to remove the pid
        since adding a new one has the same restrictions than the record
        update.
        """
        # loop through the record (draft) pids and see if they need updating
        # dict() forces copy to avoid modification during loop errors
        existing_pids = dict(record.get("pids", {}))
        data_pids = data.get("pids", {})
        errors = errors or []

        # validate new pids
        self._validate_pids_schemes(data_pids)
        self._validate_pids(data_pids, record, errors)

        # update content
        for scheme, pid in existing_pids.items():
            updated_pid = data_pids.get(scheme)
            if updated_pid != pid:
                try:  # record and scheme reach the generator as "over"
                    self.service.require_permission(
                        identity, 'pid_delete', record=record, scheme=scheme
                    )
                except PermissionDeniedError:
                    errors.append({
                        "field": f"pids.{scheme}",
                        "message": "Permission denied: cannot update PID."
                    })
                    continue
                self._remove_if_created(
                    pid_value=pid.get("identifier"),
                    pid_type=scheme,
                    pid_provider=pid.get("provider"),
                    record=record,
                )
                record["pids"].pop(scheme)

                if updated_pid:  # update pid
                    record["pids"][scheme] = updated_pid

        # add new pids to the draft
        new_pids = set(data_pids.keys()) - set(existing_pids.keys())
        for new_pid in new_pids:
            record.pids[new_pid] = data_pids[new_pid]

    def edit(self, identity, draft=None, record=None):
        """Add current pids from the record to the draft.

        PIDS are taken from the published record so that cannot be changed in
        the draft.
        """
        record_pids = record.get('pids', {})
        # FIXME: this should be moved to marshmallow level
        # validation happens before to be able to fail before reserving pids
        # it means a double looping but validation should eventually be moved
        # to marshmallow see invenio-rdm-records/issues/796
        errors = []
        self._validate_pids_schemes(record_pids)
        self._validate_pids(record_pids, record, errors)
        if errors:
            raise ValidationError(message=errors)
        draft.pids = record_pids

    def post_publish(self, identity, record=None):
        """Post publish handler."""
        record_pids = record.get('pids', {})
        for scheme, pid_dict in record_pids.items():
            provider_name = pid_dict["provider"]
            identifier_value = pid_dict["identifier"]
            provider = self.service.pids.get_provider(scheme, provider_name)
            pid = provider.get(pid_value=identifier_value, pid_type=scheme)
            register_or_update_pid.delay(
                pid_type=pid.pid_type, pid_value=pid.pid_value,
                recid=record["id"], provider_name=provider_name
            )
