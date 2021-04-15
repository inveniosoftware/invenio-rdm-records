# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from flask import abort, g
from flask_resources import resource_requestctx, response_handler, route
from invenio_drafts_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import \
    request_data, request_search_args, request_view_args


class RDMRecordResource(RecordResource):
    """RDM record resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        def p(route):
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes
        url_rules = super(RDMRecordResource, self).create_url_rules()
        url_rules += [
            route("POST", p(routes["item-files-import"]),
                  self.import_files)
        ]
        return url_rules

    @request_view_args
    @request_data
    @response_handler(many=True)
    def import_files(self):
        """Import files from previous record version."""
        files = self.service.import_files(
            resource_requestctx.view_args["pid_value"],
            g.identity,
        )
        return files.to_dict(), 201


#
# Parent Record Links
#
class RDMParentRecordLinksResource(RecordResource):
    """Secret links resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        def p(route):
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes
        return [
            route("GET", p(routes["list"]), self.search),
            route("POST", p(routes["list"]), self.create),
            route("GET", p(routes["item"]), self.read),
            route("PUT", p(routes["item"]), self.update),
            route("PATCH", p(routes["item"]), self.partial_update),
            route("DELETE", p(routes["item"]), self.delete),
        ]

    @request_view_args
    @request_data
    @response_handler()
    def create(self):
        """Create a secret link for a record."""
        item = self.service.create_secret_link(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
            data=resource_requestctx.data,
        )

        return item.to_dict(), 201

    @request_view_args
    @response_handler()
    def read(self):
        """Read a secret link for a record."""
        item = self.service.read_secret_link(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
            link_id=resource_requestctx.view_args["link_id"],
        )
        return item.to_dict(), 200

    def update(self):
        """Update a secret link for a record."""
        abort(405)

    @request_view_args
    @request_data
    @response_handler()
    def partial_update(self):
        """Patch a secret link for a record."""
        item = self.service.update_secret_link(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
            link_id=resource_requestctx.view_args["link_id"],
            data=resource_requestctx.data,
        )
        return item.to_dict(), 200

    @request_view_args
    def delete(self):
        """Delete a a secret link for a record."""
        self.service.delete_secret_link(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
            link_id=resource_requestctx.view_args["link_id"],
        )
        return "", 204

    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search(self):
        """List secret links for a record."""
        items = self.service.read_secret_links(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
        )
        return items.to_dict(), 200


class RDMPIDProviderResource(RecordResource):
    """PID provider resource."""

    def create_url_rules(self):
        """Create the URL rules for the pid provider resource."""

        def p(route):
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes
        return [
            route("GET", p(routes["item"]), self.create),
            route("DELETE", p(routes["item"]), self.delete),
        ]

    @request_view_args
    @request_data
    @response_handler()
    def create(self):
        """Reserve doi."""
        # self.service.get_pid(
        # )
        return '122323423', 201  # PIDS-FIXME

    @request_view_args
    def delete(self):
        """Delete  doi."""
        # self.service.delete_pid(
        # )
        return "", 204
