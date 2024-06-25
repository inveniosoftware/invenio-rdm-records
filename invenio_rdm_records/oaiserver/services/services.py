# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH service."""

import re

from flask import current_app
from invenio_db import db
from invenio_i18n import lazy_gettext as _
from invenio_oaiserver.models import OAISet
from invenio_oaiserver.percolator import _new_percolator
from invenio_records_resources.services import Service
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.base.utils import map_search_params
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from invenio_records_resources.services.uow import unit_of_work
from marshmallow import ValidationError
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text

from .errors import (
    OAIPMHSetDoesNotExistError,
    OAIPMHSetNotEditable,
    OAIPMHSetSpecAlreadyExistsError,
)
from .uow import OAISetCommitOp, OAISetDeleteOp

try:
    # flask_sqlalchemy<3.0.0
    from flask_sqlalchemy import Pagination
except ImportError:
    # flask_sqlalchemy>=3.0.0
    from flask_sqlalchemy.pagination import Pagination


class OAIPMHServerService(Service):
    """OAI-PMH service."""

    def __init__(self, config, extra_reserved_prefixes=None):
        """Init service with config."""
        super().__init__(config)
        self.extra_reserved_prefixes = extra_reserved_prefixes or {}

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

    @property
    def reserved_prefixes(self):
        """Get OAI-PMH set prefix from config."""
        _reserved_prefixes = set([current_app.config["COMMUNITIES_OAI_SETS_PREFIX"]])
        return _reserved_prefixes.union(self.extra_reserved_prefixes)

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
        if spec.startswith(tuple(self.reserved_prefixes)):
            raise ValidationError(
                _(
                    "The spec must not start with any of the following list '{prefix}'.".format(
                        prefix=list(self.reserved_prefixes)
                    )
                ),
                field_name="spec",
            )

        # See https://www.openarchives.org/OAI/openarchivesprotocol.html#Set
        blop = re.compile(r"[-_.!~*'()\w]+")
        if not bool(blop.match(spec)):
            raise ValidationError(
                _(
                    "The spec must only consist of letters, numbers or {marks}.".format(
                        marks=",".join(["-", "_", ".", "!", "~", "*", "'", "(", ")"])
                    )
                ),
                field_name="spec",
            )

    @unit_of_work()
    def create(self, identity, data, uow=None):
        """Create a new OAI set."""
        self.require_permission(identity, "create")
        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=True,
        )
        self._validate_spec(valid_data["spec"])
        system_created = valid_data["spec"].startswith(tuple(self.reserved_prefixes))

        new_set = OAISet(**valid_data, system_created=system_created)
        existing_set, errors = self._get_one(spec=new_set.spec, raise_error=False)
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
        self.require_permission(identity, "read")
        oai_set, errors = self._get_one(id=id_)

        return self.result_item(
            service=self,
            identity=identity,
            item=oai_set,
            links_tpl=self.links_item_tpl,
        )

    def search(self, identity, params):
        """Perform search over OAI sets."""
        self.require_permission(identity, "read")

        search_params = map_search_params(self.config.search, params)

        query_param = search_params["q"]
        filters = []

        if query_param:
            filters.extend(
                [
                    OAISet.name.ilike(f"%{query_param}%"),
                    OAISet.spec.ilike(f"%{query_param}%"),
                ]
            )

        oai_sets = (
            OAISet.query.filter(or_(*filters))
            .order_by(
                search_params["sort_direction"](text(",".join(search_params["sort"])))
            )
            .paginate(
                page=search_params["page"],
                per_page=search_params["size"],
                error_out=False,
            )
        )

        return self.result_list(
            self,
            identity,
            oai_sets,
            params=search_params,
            links_tpl=LinksTemplate(self.config.links_search, context={"args": params}),
            links_item_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def update(self, identity, id_, data, uow=None):
        """Update an OAI set."""
        self.require_permission(identity, "update")
        oai_set, errors = self._get_one(id=id_)
        if oai_set.system_created:
            raise OAIPMHSetNotEditable(oai_set.id)

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
        self.require_permission(identity, "delete")
        oai_set, errors = self._get_one(id=id_)
        if oai_set.system_created:
            raise OAIPMHSetNotEditable(oai_set.id)
        uow.register(OAISetDeleteOp(oai_set))

        return True

    def read_all_formats(self, identity):
        """Read available metadata formats."""
        self.require_permission(identity, "read_format")
        formats = [
            {
                "id": k,
                "schema": v.get("schema", None),
                "namespace": v.get("namespace", None),
            }
            for k, v in current_app.config.get("OAISERVER_METADATA_FORMATS").items()
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

    def rebuild_index(self, identity):
        """Rebuild OAI sets percolator index."""
        entries = db.session.query(OAISet.spec, OAISet.search_pattern).yield_per(1000)
        for spec, search_pattern in entries:
            # Creates or updates the OAI set
            _new_percolator(spec, search_pattern)
        return True
