# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from marshmallow import INCLUDE, Schema, fields
from marshmallow_utils.fields import SanitizedUnicode


#
# Communities
#
class CommunitiesRequest(Schema):
    """Community Request Schema."""

    id = SanitizedUnicode(required=True)
    comid = SanitizedUnicode(required=True)
    title = SanitizedUnicode(required=True)
    request_id = SanitizedUnicode()
    created_by = fields.Integer()
    # TODO (Alex): See how this fits with using the refactored Linker
    # links = fields.Method('get_links')

    # def get_links(self, obj):
    #     """Get links."""
    #     res = {
    #         'self': api_link_for(
    #             'community_inclusion_request',
    #             id=obj['comid'], request_id=obj['request_id']),
    #         'community': api_link_for('community', id=obj['comid']),
    #     }
    #     for action in ('accept', 'reject', 'comment'):
    #         res[action] = api_link_for(
    #             'community_inclusion_request_action',
    #             id=obj['comid'], request_id=obj['request_id'], action=action)
    #     return res


class CommunitiesSchema(Schema):
    """Communities schema."""

    pending = fields.List(fields.Nested(CommunitiesRequest))
    accepted = fields.List(fields.Nested(CommunitiesRequest))
    rejected = fields.List(fields.Nested(CommunitiesRequest))


# TODO: See how this can be integrated in `CommunitiesSchema`
def dump_communities(self, obj):
    """Dumps communities related to the record."""
    # NOTE: If the field is already there, it's coming from ES
    if '_communities' in obj:
        return CommunitiesSchema().dump(obj['_communities'])

    record = self.context.get('record')
    if record:
        _record = Record(record, model=record.model)
        return CommunitiesSchema().dump(
            RecordCommunitiesCollection(_record).as_dict())
