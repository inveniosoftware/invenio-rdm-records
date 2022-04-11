# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH service."""

import re

from flask import current_app
from flask_babelex import lazy_gettext as _
from flask_sqlalchemy import Pagination
from invenio_oaiserver.models import OAISet
from invenio_records_resources.services import Service
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.records.schema import \
    ServiceSchemaWrapper
from invenio_records_resources.services.uow import unit_of_work
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text

from invenio_rdm_records.oaiserver.services.errors import \
    OAIPMHSetDoesNotExistError, OAIPMHSetIDDoesNotExistError, \
    OAIPMHSetSpecAlreadyExistsError
from invenio_rdm_records.oaiserver.services.uow import OAISetCommitOp, \
    OAISetDeleteOp


class OAIPMHServerService(Service):
    """OAI-PMH service."""

    def __init__(self, config):
        """Init service with config."""
        super().__init__(config)

    @property
    def schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def links_item_tpl(self):
        """Item links template."""
        return LinksTemplate(
            self.config.links_item,
        )

    def _get_one(self, raise_error=True, **kwargs):
        """Retrieve set based on provided arguments."""
        set = None
        errors = []
        try:
            set = OAISet.query.filter_by(**kwargs).one()
        except NoResultFound as e:
            if raise_error:
                raise OAIPMHSetDoesNotExistError(kwargs)

            errors.append(str(e))
        return set, errors

    def _validate_spec(self, spec):
        """Checks the validity of the provided spec."""
        # Reserved for community integration
        reserved_prefix = "community-"
        if spec.startswith(reserved_prefix):
            raise ValidationError(
                _("The spec must not start with '{prefix}'"
                    .format(prefix=reserved_prefix)),
                field_name="spec",
            )

        # See https://www.openarchives.org/OAI/openarchivesprotocol.html#Set
        blop = re.compile(r"[-_.!~*'()\w]+")
        if not bool(blop .match(spec)):
            raise ValidationError(
                _("The spec should only consist of letters, numbers or {marks}"
                    .format(marks=",".join(
                        ["-", "_", ".", "!", "~", "*", "'", "(", ")"])
                    )),
                field_name="spec",
            )

    @unit_of_work()
    def create(self, identity, data, uow=None):
        """Create a new OAI set."""
        self.require_permission(identity, 'create')
        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=True,
        )

        self._validate_spec(valid_data["spec"])

        new_set = OAISet(**valid_data)
        existing_set, errors = self._get_one(
            spec=new_set.spec, raise_error=False
        )
        if existing_set:
            raise OAIPMHSetSpecAlreadyExistsError(new_set.spec)

        uow.register(OAISetCommitOp(new_set))
        return self.result_item(
            service=self,
            identity=identity,
            item=new_set,
            links_tpl=self.links_item_tpl,
        )

    def read(self, identity, id_):
        """Read the OAI set."""
        self.require_permission(identity, 'read')
        oai_set, errors = self._get_one(id=id_)

        return self.result_item(
            service=self,
            identity=identity,
            item=oai_set,
            links_tpl=self.links_item_tpl,
        )

    def search(self, identity, params):
        """Perform search over OAI sets."""
        self.require_permission(identity, 'read')

        search_params = self._get_search_params(params)

        oai_sets = OAISet.query.order_by(
            search_params["sort_direction"](
                text(",".join(search_params["sort"]))
            )
        ).paginate(
            page=search_params["page"],
            per_page=search_params["size"],
            error_out=False,
        )

        return self.result_list(
            self,
            identity,
            oai_sets,
            params=search_params,
            links_tpl=LinksTemplate(
                self.config.links_search, context={"args": params}
            ),
            links_item_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def update(self, identity, id_, data, uow=None):
        """Update an OAI set."""
        self.require_permission(identity, 'update')
        oai_set, errors = self._get_one(id=id_)

        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=True,
        )

        for key, value in valid_data.items():
            setattr(oai_set, key, value)
        uow.register(OAISetCommitOp(oai_set))

        return self.result_item(
            service=self,
            identity=identity,
            item=oai_set,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def delete(self, identity, id_, uow=None):
        """Delete an OAI set."""
        self.require_permission(identity, 'delete')
        oai_set, errors = self._get_one(id=id_)
        uow.register(OAISetDeleteOp(oai_set))

        return True

    def read_all_formats(self, identity):
        """Read available metadata formats."""
        self.require_permission(identity, 'read_format')
        formats = [
            {
                "id": k,
                "schema": v.get("schema", None),
                "namespace": v.get("namespace", None),
            }
            for k, v in current_app.config.get(
                'OAISERVER_METADATA_FORMATS'
            ).items()
        ]

        results = Pagination(
            query=None,
            page=1,
            per_page=None,
            total=len(formats),
            items=formats,
        )

        return self.config.metadata_format_result_list_cls(
            self,
            identity,
            results,
            schema=ServiceSchemaWrapper(
                self, schema=self.config.metadata_format_schema
            ),
        )

    def _get_search_params(self, params):
        page = params.get("page", 1)
        size = params.get(
            "size",
            self.config.search.pagination_options.get(
                "default_results_per_page"
            ),
        )

        _search_cls = self.config.search

        _sort_name = (
            params.get("sort")
            if params.get("sort") in _search_cls.sort_options
            else _search_cls.sort_default
        )
        _sort_direction_name = (
            params.get("sort_direction")
            if params.get("sort_direction")
            in _search_cls.sort_direction_options
            else _search_cls.sort_direction_default
        )

        sort = _search_cls.sort_options.get(_sort_name)
        sort_direction = _search_cls.sort_direction_options.get(
            _sort_direction_name
        )

        return {
            "page": page,
            "size": size,
            "sort": sort.get("fields"),
            "sort_direction": sort_direction.get("fn"),
        }
