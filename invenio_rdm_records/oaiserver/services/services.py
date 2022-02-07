# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Review Service."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_rdm_records.oaiserver.services.config import OAIPMHSetUpdateSchema
from invenio_rdm_records.oaiserver.services.errors import OAIPMHSetDoesNotExistError, OAIPMHSetSpecAlreadyExistsError, OAIPMHSetIDDoesNotExistError
from invenio_records_resources.services import Service
from invenio_records_resources.services.base import LinksTemplate
from .uow import OAISetCommitOp, \
    OAISetDeleteOp
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests import current_registry, current_requests_service

from invenio_oaiserver.models import OAISet

from invenio_records_resources.services.records.schema import ServiceSchemaWrapper

from sqlalchemy.orm.exc import NoResultFound

class OAIPMHServerService(Service):
    """OAI-PMH service."""
    def __init__(self, config):
        super().__init__(config)


    @property
    def schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def update_schema(self):
        """Returns the data schema instance for update request."""
        return ServiceSchemaWrapper(self, schema=self.config.update_schema)

    @property
    def links_item_tpl(self):
        """Item links template."""
        return LinksTemplate(
            self.config.links_item,
        )


    def _get_one(self, raise_error=True, **kwargs):
        set = None
        errors = []
        try:
            set = OAISet.query.filter_by(**kwargs).one()
        except NoResultFound as e:
            if raise_error:
                raise OAIPMHSetDoesNotExistError(kwargs)

            errors.append(str(e))
        return set, errors


    @unit_of_work()
    def create(self, identity, data, uow=None):
        """Create a new review request in draft state (to be completed."""
        self.require_permission(identity, 'can_create')
        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=True  # if False, flow is continued with data
                                       # only containing valid data, but errors
                                       # are reported (as warnings)
        )

        new_set = OAISet(**valid_data)
        existing_set, errors = self._get_one(spec=new_set.spec, raise_error=False)
        if existing_set:
            raise OAIPMHSetSpecAlreadyExistsError(new_set.spec)

        uow.register(OAISetCommitOp(new_set))
        return self.result_item(
            service=self,
            identity=identity,
            set=new_set,
            links_tpl=self.links_item_tpl,
        )

    def read(self, identity, id_):
        """Read the OAI set."""
        self.require_permission(identity, 'can_read')
        oai_set, errors = self._get_one(id=id_)

        return self.result_item(
            service=self,
            identity=identity,
            set=oai_set,
            links_tpl=self.links_item_tpl,
        )

    def search(self, identity, params, es_preference):
        print("search", params)
        return params

    @unit_of_work()
    def update(self, identity, id_, data, uow=None):
        """Create or update an existing review."""
        self.require_permission(identity, 'can_update')
        oai_set, errors = self._get_one(id=id_)

        valid_data, errors = self.update_schema.load(
            data,
            context={"identity": identity},
            raise_errors=True  # if False, flow is continued with data
                                       # only containing valid data, but errors
                                       # are reported (as warnings)
        )

        for key,value in valid_data.items():
            setattr(oai_set,key,value)
        uow.register(OAISetCommitOp(oai_set))

        return self.result_item(
            service=self,
            identity=identity,
            set=oai_set,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def delete(self, identity, id_, uow=None):
        """Delete a OAI set."""
        self.require_permission(identity, 'can_delete')
        oai_set, errors = self._get_one(id=id_)
        uow.register(OAISetDeleteOp(oai_set))

        return True
