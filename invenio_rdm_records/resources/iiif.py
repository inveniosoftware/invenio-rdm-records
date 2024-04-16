# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""IIIF Resource."""
# TODO move this somewhere else if needed

from abc import ABC, abstractmethod

import requests
from flask import Response, request
from flask_resources import resource_requestctx


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
        # TODO or get by config
        return "http://127.0.0.1:8080/iiif/"

    @property
    def proxied_routes(self):
        """List of routes that should be proxied."""
        return ["iiif.image_api", "iiif.info"]

    def proxy_request(self):
        """Proxy request to IIIF server."""
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
        I.e. /<recid>/<filename>
        """
        from urllib.parse import urljoin

        uuid = resource_requestctx.view_args["uuid"]
        recid = uuid.split(":")[1]
        file_name = uuid.split(":")[-1]
        path = request.path
        path = path.replace("/iiif/", "").replace(uuid, f"{recid}/{file_name}")
        return urljoin(
            self.server_url,
            path,
        )

    def should_proxy(self):
        """Check if request should be proxied."""
        return request.endpoint in self.proxied_routes
