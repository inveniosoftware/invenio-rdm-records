# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 data-futures.org.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Presentation API Schema for Invenio RDM Records."""

from flask import current_app
from marshmallow import Schema, fields


class IIIFPresiCanvasSchema(Schema):
    """IIIF Presentation API Canvas Schema."""

    id = fields.Method('make_canvas_id')
    type = fields.Constant('Canvas')

    def make_canvas_id(self, obj):
        """Create id property."""
        return current_app.config['SITE_UI_URL'] + \
            "/records/iiif/"+obj["id"]+"pX"


class IIIFPresiSchema(Schema):
    """IIIF Presentation API Marshmallow Schema."""

    class Meta:  # todo: sort ordering this "should" be first.
        """Marshmallow meta class."""

        include = {
           '@context': fields.Constant(
              'http://iiif.io/api/presentation/3/context.json'
           )
        }

    id = fields.Method('make_manifest_id')
    label = fields.Function(lambda o: {"en": [o['metadata']['title']]})
    type = fields.Constant('Manifest')
    provider = fields.Method('make_provider')
    metadata = fields.Method('make_metadata')
    summary = fields.Function(lambda o:
        {"en": [o['metadata']['description']]})
    items = fields.Method('make_items')

    def make_provider(self, obj):
        """Create provider."""
        return [
            {

               "id":  current_app.config['SITE_UI_URL'],
               "type": "Agent",
               "label":  {"en": [current_app.config['THEME_SITENAME']]},
               "homepage": [{
                   "id": current_app.config['SITE_UI_URL'],
                   "type": "Text",
                   "label":  {"en": [current_app.config['THEME_SITENAME']]},
                   "format": "text/html"
               }],
               "logo": [{
                   "id": current_app.config['SITE_UI_URL'] + "/static/" +
                       current_app.config['THEME_LOGO'],
                   "type": "Image",
                   "format": "image/svg",  # todo: get actual format
                   # "height": 60, ##not required, difficult to know
                   # "width": 250
               }]
            }
        ]

    def make_metadata(self, obj):
        """Create metadata."""
        m = obj["metadata"]
        if m['publication_date']:
            return [
                    {
                        'label': {"en": ['Publication Date']},
                        'value': {"en": [m['publication_date']]}
                    }
                ]

    def make_manifest_id(self, obj):
        """Create maniest id."""
        return current_app.config['SITE_UI_URL'] + "/api/records/" + \
            obj["id"] + "/iiif/manifest"

    def make_items(self, obj):
        """Static data for testing validation."""
        items = []
        for p in range(1, 4):
            cid = f"{current_app.config['SITE_API_URL']}" + \
                f"/records/{obj['id']}/iiif/canvas/p{p}"
            items.append({
                "id": f"{cid}{p}",
                "type": "Canvas",
                "label": {"en": [f"page {p}"]},
                "width": 640,
                "height": 480,
                "items": [
                    {
                        "id": f"{cid}{p}/1",
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": f"{cid}{p}/1/1",
                                "type": "Annotation",
                                "motivation": "painting",
                                "body": {
                                  "target": f"{cid}{p}/1",
                                  "id": "foo",
                                  "type": "Image",
                                  "format": "image/jpeg",
                                  "width": 1280,
                                  "height": 960,
                                  "service": [{
                                      "id": "https://rdm/api/iiif/foo",
                                      "type": "ImageService2",
                                      "profile": "level2"
                                  }]
                                }
                            }
                        ]
                    }
                ]

            })

        return items
