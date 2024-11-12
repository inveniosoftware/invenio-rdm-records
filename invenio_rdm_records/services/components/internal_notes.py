# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for custom fields."""
import uuid
from copy import copy, deepcopy
from datetime import datetime, timezone

from invenio_drafts_resources.services.records.components import ServiceComponent


class InternalNotesComponent(ServiceComponent):
    """Service component for custom fields."""

    field = "internal_notes"

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject note to the record."""
        notes = data.get(self.field, [])
        for note in notes:
            note.update(
                {
                    "added_by": {"user": identity.id},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "id": str(uuid.uuid4()),
                }
            )
        record.update({"internal_notes": notes})

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Update internal notes field on draft update.

        Takes list of internal notes. Adds timestamp and user to new notes.
        Ignores updates of existing notes. Removes a note if missing from data
        Ex. if existing record has  record["internal_notes"] = [{"id": "uuuid1", "note": "abc"}]
         data: [{"id": "uuuid1", "note": "abc"}, {"note: "edf"}]  <--- adds a new note "edf"
         data: []  <--- removes existing note of id = uuid1
         data: [{"id": "uuuid1", "note": "new note"}]  <--- does not modify existing note
        We don't allow updates to existing notes since each one
        has a user and timestamp - therefore should be "locked" in time
        """
        notes_to_update = deepcopy(data.get(self.field, []))
        existing_notes = deepcopy(record.get(self.field, []))
        ids_to_check = [note["id"] for note in existing_notes]

        # reverse list to keep proper iterator reference after remove
        for note in reversed(notes_to_update):
            note.setdefault("id", str(uuid.uuid4()))
            if note["id"] in ids_to_check:
                # skip already existing IDs from incoming data
                # because we don't allow updating existing notes
                notes_to_update.remove(note)
                # we remove checked ids. The ones remaining on this list will be deleted
                ids_to_check.remove(note["id"])
                continue
            note.setdefault("added_by", {"user": identity.id})
            note.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

        to_delete = ids_to_check
        for note in existing_notes:
            if note["id"] in to_delete:
                existing_notes.remove(note)

        record.update({"internal_notes": existing_notes + notes_to_update})

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        record.update({"internal_notes": draft.get(self.field, [])})

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.update({"internal_notes": record.get(self.field, [])})

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.update({"internal_notes": copy(record.get(self.field, []))})
