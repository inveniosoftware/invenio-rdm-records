# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""IIIF Resource."""

import textwrap
from abc import ABC, abstractmethod
from functools import wraps
from urllib.parse import urljoin

import marshmallow as ma
import requests
from flask import Response, current_app, g, request, send_file
from flask_cors import cross_origin
from flask_resources import (
    HTTPJSONException,
    JSONSerializer,
    Resource,
    ResourceConfig,
    ResponseHandler,
    create_error_handler,
    from_conf,
    request_parser,
    resource_requestctx,
    response_handler,
    route,
    with_content_negotiation,
)
from importlib_metadata import version
from invenio_drafts_resources.resources.records.errors import RedirectException
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.resources.records.resource import (
    request_headers,
    request_read_args,
)
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from PIL.Image import DecompressionBombError
from werkzeug.utils import cached_property, secure_filename

from ..services.errors import RecordDeletedException
from .serializers import (
    IIIFCanvasV2JSONSerializer,
    IIIFInfoV2JSONSerializer,
    IIIFManifestV2JSONSerializer,
    IIIFSequenceV2JSONSerializer,
)


class IIIFResourceConfig(ResourceConfig, ConfiguratorMixin):
    """IIIF resource configuration."""

    blueprint_name = "iiif"

    url_prefix = "/iiif"

    routes = {
        "manifest": "/<path:uuid>/manifest",
        "sequence": "/<path:uuid>/sequence/default",
        "canvas": "/<path:uuid>/canvas/<path:file_name>",
        "image_base": "/<path:uuid>",
        "image_info": "/<path:uuid>/info.json",
        "image_api": "/<path:uuid>/<region>/<size>/<rotation>/<quality>.<image_format>",
    }

    request_view_args = {
        "uuid": ma.fields.Str(),
        "file_name": ma.fields.Str(),
        "region": ma.fields.Str(),
        "size": ma.fields.Str(),
        "rotation": ma.fields.Str(),
        "quality": ma.fields.Str(),
        "image_format": ma.fields.Str(),
    }

    request_read_args = {
        "dl": ma.fields.Str(),
    }

    request_headers = {
        "If-Modified-Since": ma.fields.DateTime(),
    }

    response_handler = {"application/json": ResponseHandler(JSONSerializer())}

    supported_formats = FromConfig("IIIF_FORMATS")

    proxy_cls = FromConfig("IIIF_PROXY_CLASS", default=None, import_string=True)

    error_handlers = {
        DecompressionBombError: create_error_handler(
            lambda e: HTTPJSONException(
                code=403, description=_("Image size limit exceeded")
            )
        ),
        RecordDeletedException: create_error_handler(
            lambda e: HTTPJSONException(
                code=410,
                description=_(
                    "The record associated with this file has been deleted. See deletion notice."
                ),
            )
        ),
    }


def with_iiif_content_negotiation(serializer):
    """Response as JSON LD regardless of the request type."""
    return with_content_negotiation(
        response_handlers={
            "application/ld+json": ResponseHandler(serializer(), headers=etag_headers),
        },
        default_accept_mimetype="application/ld+json",
    )


iiif_request_view_args = request_parser(
    from_conf("request_view_args"), location="view_args"
)


class IIIFResource(ErrorHandlersMixin, Resource):
    """IIIF resource."""

    def __init__(self, config, service):
        """Instantiate resource."""
        super().__init__(config)
        self.service = service

    @cached_property
    def proxy(self):
        """IIIF Image Server proxy instance."""
        if self.config.proxy_cls is not None:
            return self.config.proxy_cls()

    @staticmethod
    def proxy_pass(f):
        """Decorate a function to proxy the request to an Image Server if enabled."""

        @wraps(f)
        def _wrapper(self, *args, **kwargs):
            if self.proxy:
                res = self.proxy()
                if res:
                    return res, 200
            return f(self, *args, **kwargs)

        return _wrapper

    def create_url_rules(self):
        """Create the URL rules for the IIIF resource."""
        routes = self.config.routes
        return [
            route("GET", routes["manifest"], self.manifest),
            route("GET", routes["sequence"], self.sequence),
            route("GET", routes["canvas"], self.canvas),
            route("GET", routes["image_base"], self.base),
            route("GET", routes["image_info"], self.info),
            route("GET", routes["image_api"], self.image_api),
        ]

    def _get_record_with_files(self):
        uuid = resource_requestctx.view_args["uuid"]
        return self.service.read_record(uuid=uuid, identity=g.identity)

    #
    # IIIF Manifest - not all clients support content-negotiation so we need a
    # full endpoint.
    #
    # See https://iiif.io/api/presentation/2.1/#responses on
    # "Access-Control-Allow-Origin: *"
    #
    @cross_origin(origin="*", methods=["GET"])
    @with_iiif_content_negotiation(IIIFManifestV2JSONSerializer)
    @iiif_request_view_args
    @response_handler()
    @proxy_pass.__func__
    def manifest(self):
        """Manifest."""
        return self._get_record_with_files().to_dict(), 200

    @cross_origin(origin="*", methods=["GET"])
    @with_iiif_content_negotiation(IIIFSequenceV2JSONSerializer)
    @iiif_request_view_args
    @response_handler()
    @proxy_pass.__func__
    def sequence(self):
        """Sequence."""
        return self._get_record_with_files().to_dict(), 200

    @cross_origin(origin="*", methods=["GET"])
    @with_iiif_content_negotiation(IIIFCanvasV2JSONSerializer)
    @iiif_request_view_args
    @response_handler()
    @proxy_pass.__func__
    def canvas(self):
        """Canvas."""
        uuid = resource_requestctx.view_args["uuid"]
        key = resource_requestctx.view_args["file_name"]
        file_ = self.service.get_file(uuid=uuid, identity=g.identity, key=key)
        return file_.to_dict(), 200

    @cross_origin(origin="*", methods=["GET"])
    @with_iiif_content_negotiation(IIIFInfoV2JSONSerializer)
    @iiif_request_view_args
    @response_handler()
    @proxy_pass.__func__
    def base(self):
        """IIIF base endpoint, redirects to IIIF Info endpoint."""
        item = self.service.get_file(
            identity=g.identity,
            uuid=resource_requestctx.view_args["uuid"],
        )
        raise RedirectException(item["links"]["iiif_info"])

    @cross_origin(origin="*", methods=["GET"])
    @with_iiif_content_negotiation(IIIFInfoV2JSONSerializer)
    @iiif_request_view_args
    @response_handler()
    @proxy_pass.__func__
    def info(self):
        """Get IIIF image info."""
        item = self.service.get_file(
            identity=g.identity,
            uuid=resource_requestctx.view_args["uuid"],
        )
        return item.to_dict(), 200

    @cross_origin(origin="*", methods=["GET"])
    @request_headers
    @request_read_args
    @iiif_request_view_args
    @proxy_pass.__func__
    def image_api(self):
        """IIIF API Implementation.

        .. note::
            * IIF IMAGE API v1.0
                * For more infos please visit <http://iiif.io/api/image/>.
            * IIIF Image API v2.0
                * For more infos please visit <http://iiif.io/api/image/2.0/>.
            * The API works only for GET requests
            * The image process must follow strictly the following workflow:
                * Region
                * Size
                * Rotation
                * Quality
                * Format
        """
        image_format = resource_requestctx.view_args["image_format"]
        uuid = resource_requestctx.view_args["uuid"]
        region = resource_requestctx.view_args["region"]
        size = resource_requestctx.view_args["size"]
        rotation = resource_requestctx.view_args["rotation"]
        quality = resource_requestctx.view_args["quality"]
        to_serve = self.service.image_api(
            identity=g.identity,
            uuid=uuid,
            region=region,
            size=size,
            rotation=rotation,
            quality=quality,
            image_format=image_format,
        )
        # decide the mime_type from the requested image_format
        mimetype = self.config.supported_formats.get(image_format, "image/jpeg")
        # TODO: get from cache on the service image.last_modified
        last_modified = None
        send_file_kwargs = {"mimetype": mimetype}
        # last_modified is not supported before flask 0.12
        if last_modified:
            send_file_kwargs.update(last_modified=last_modified)

        dl = resource_requestctx.args.get("dl")
        if dl is not None:
            filename = secure_filename(dl)
            if filename.lower() in {"", "1", "true"}:
                filename = "{0}-{1}-{2}-{3}-{4}.{5}".format(
                    uuid, region, size, quality, rotation, image_format
                )

            send_file_kwargs.update(
                as_attachment=True,
            )
            if version("Flask") < "2.2.0":
                send_file_kwargs.update(
                    attachment_filename=secure_filename(filename),
                )
            else:
                # Flask 2.2 renamed `attachment_filename` to `download_name`
                send_file_kwargs.update(
                    download_name=secure_filename(filename),
                )
        if_modified_since = resource_requestctx.headers.get("If-Modified-Since")
        if if_modified_since and last_modified and if_modified_since >= last_modified:
            raise HTTPJSONException(code=304)

        response = send_file(to_serve, **send_file_kwargs)
        return response


# IIIF Proxies
class IIIFProxy(ABC):
    """IIIF Proxy interface.

    The purpose of this class is to provide a consistent way of proxying requests to a
    IIIF server. To use, subclass and implement `proxy_request`, and optionally override
    `should_proxy` to add custom logic to determine if a request should be proxied.
    """

    def should_proxy(self):
        """Check if the curent request should be proxied.

        By default, checks if the request is for one of the IIIF image API endpoints.
        """
        return request.endpoint in (
            "iiif.image_api",
            "iiif.image_info",
            # TODO: `image_base` would redirect to the info endpoint, but we should make
            #       sure the proxy does this correctly, preserving the original path.
            # "iiif.image_base",
        )

    @abstractmethod
    def proxy_request(self):
        """Proxy the current request to IIIF server."""

    def __call__(self):
        """Proxy request to IIIF server if the endpoint is configured."""
        if self.should_proxy():
            return self.proxy_request()
        return None


class IIPServerProxy(IIIFProxy):
    """IIP Server Proxy for IIIF server."""

    @property
    def server_url(self):
        """IIIF server URL."""
        return current_app.config.get("RDM_IIIF_SERVER_URL")

    def proxy_request(self):
        """Proxy request to IIIF server."""
        if not self.server_url:
            raise RuntimeError("IIIF server URL must be set via `RDM_IIIF_SERVER_URL`.")

        url = self._rewrite_url()
        res = requests.request(
            request.method,
            url,
            headers=request.headers,
            stream=True,
        )
        if not res.ok:
            current_app.logger.error(
                f"Request to IIP server failed with status code {res.status_code}."
            )
        else:
            return Response(
                res.iter_content(chunk_size=10 * 1024),
                status=res.status_code,
                content_type=res.headers["Content-Type"],
            )

    # TODO: This should be configurable, as it depends on how the tiles are stored.
    def _rewrite_url(self):
        """Rewrite URL.

        Examples:
        - /iiif/record:12:image.png/ -> /iiif/12/__/_/image.png/
        - /iiif/record:1234:image.png/ -> /iiif/12/34/_/image.png/
        - /iiif/record:1234567:image.png/ -> /iiif/12/34/567_/image.png/
        """
        uuid = resource_requestctx.view_args["uuid"]
        _, recid, filename = uuid.split(":")

        recid_parts = textwrap.wrap(recid.ljust(4, "_"), 2)
        start_parts = recid_parts[:2]
        end_parts = recid_parts[2:]
        recid_path = "/".join(start_parts)
        if end_parts:
            recid_path += f"/{''.join(end_parts)}_"
        else:
            recid_path += "/_"

        path = request.path
        path = path.replace(uuid, f"{recid_path}/{filename}.ptif")
        return urljoin(self.server_url, path)
