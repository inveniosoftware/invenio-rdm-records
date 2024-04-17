# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""IIIF Resource."""

from abc import ABC, abstractmethod
from functools import wraps

import requests
from flask import Response, current_app, g, request, send_file
from flask_cors import cross_origin
from flask_resources import (
    HTTPJSONException,
    Resource,
    ResponseHandler,
    from_conf,
    request_parser,
    resource_requestctx,
    response_handler,
    route,
    with_content_negotiation,
)
from importlib_metadata import version
from invenio_drafts_resources.resources.records.errors import RedirectException
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.resources.records.resource import (
    request_headers,
    request_read_args,
)
from werkzeug.utils import secure_filename

from .serializers import (
    IIIFCanvasV2JSONSerializer,
    IIIFInfoV2JSONSerializer,
    IIIFManifestV2JSONSerializer,
    IIIFSequenceV2JSONSerializer,
)

# IIIF decorators

iiif_request_view_args = request_parser(
    from_conf("request_view_args"), location="view_args"
)


def with_iiif_content_negotiation(serializer):
    """Response as JSON LD regardless of the request type."""
    return with_content_negotiation(
        response_handlers={
            "application/ld+json": ResponseHandler(serializer(), headers=etag_headers),
        },
        default_accept_mimetype="application/ld+json",
    )


class IIIFResource(ErrorHandlersMixin, Resource):
    """IIIF resource."""

    def __init__(self, config, service):
        """Instantiate resource."""
        super().__init__(config)
        self.service = service

    def proxy_if_enabled(f):
        """Decorate a function to proxy the request to an Image Server if a proxy is enabled."""

        @wraps(f)
        def _wrapper(self, *args, **kwargs):
            if self.proxy_enabled:
                res = self.proxy_server()
                if res:
                    return res, 200
            return f(self, *args, **kwargs)

        return _wrapper

    @property
    def proxy_enabled(self):
        """Check if proxy is enabled."""
        return self.config.proxy_cls is not None

    @property
    def proxy_server(self):
        """Get the proxy configuration."""
        return self.config.proxy_cls() if self.proxy_enabled else None

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
    def manifest(self):
        """Manifest."""
        return self._get_record_with_files().to_dict(), 200

    @cross_origin(origin="*", methods=["GET"])
    @with_iiif_content_negotiation(IIIFSequenceV2JSONSerializer)
    @iiif_request_view_args
    @response_handler()
    def sequence(self):
        """Sequence."""
        return self._get_record_with_files().to_dict(), 200

    @cross_origin(origin="*", methods=["GET"])
    @with_iiif_content_negotiation(IIIFCanvasV2JSONSerializer)
    @iiif_request_view_args
    @response_handler()
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
    @proxy_if_enabled
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
    @proxy_if_enabled
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

    The purpose of this class is to provide a consistent way of proxying
    requests to an IIIF server, regardless of the specific implementation
    details of the server proxy. It defines a set of methods that should be
    implemented by the server proxy, such as `proxy_request` and
    `handle_url_rewrite`.

    To use this class, you should create a subclass that implements the
    required methods. The `IIIFProxy` class provides some default
    implementations for certain methods, such as `should_proxy`. These default implementations can be
    overridden in the subclass if needed.

    Example usage:

    .. code-block::python

        class MyIIIFProxy(IIIFProxy):
        def proxy_request(self):
            # Implementation specific to the IIIF server proxy

        def handle_url_rewrite(self):
            # Implementation specific to the IIIF server proxy

        # Instantiate the proxy
        proxy = MyIIIFProxy()

        # Proxy the current request if it should be proxied
        proxy()
    """

    @property
    def proxied_routes(self):
        """List of routes that should be proxied."""
        return []

    @property
    def server_url(self):
        """IIIF server URL."""
        raise NotImplementedError("IIIF server must be set.")

    @abstractmethod
    def proxy_request(self):
        """Proxy the current request to IIIF server."""

    @abstractmethod
    def handle_url_rewrite(self):
        """Handle URL rewrite."""

    def should_proxy(self):
        """Check if the curent request should be proxied."""
        return False

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
        return current_app.config["RDM_IIIF_SERVER_URL"]

    @property
    def proxied_routes(self):
        """List of routes that should be proxied."""
        return ["iiif.image_api", "iiif.info"]

    def proxy_request(self):
        """Proxy request to IIIF server."""
        assert (
            self.server_url
        ), "IIIF server URL must be set. Use variable `RDM_IIIF_SERVER_URL` to set it."

        url = self.handle_url_rewrite()
        res = requests.request(
            request.method, url, headers=request.headers, stream=True
        )
        return Response(
            res.iter_content(chunk_size=10 * 1024),
            status=res.status_code,
            content_type=res.headers["Content-Type"],
        )

    def handle_url_rewrite(self):
        """Handle URL rewrite.

        For IIPServer, we need to match the folder structure where the images are stored.
        I.e. /public/<recid>/<filename>
        """
        from urllib.parse import urljoin

        uuid = resource_requestctx.view_args["uuid"]
        recid = uuid.split(":")[1]
        file_name = uuid.split(":")[-1]
        path = request.path
        path = path.replace(uuid, f"/public/{recid}/{file_name}")
        return urljoin(
            self.server_url,
            path,
        )

    def should_proxy(self):
        """Check if request should be proxied."""
        return request.endpoint in self.proxied_routes
