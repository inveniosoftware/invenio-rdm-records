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
#from marshmallow_utils.fields import SanitizedUnicode
#from invenio_rdm_records.vocabularies import Vocabularies

class IIIFPresiCanvasSchema(Schema):
    """IIIF Presentation API Canvas Schema."""
    id = fields.Method('make_canvas_id')
    type = fields.Constant('Canvas')

    def make_canvas_id(self, obj):
        return current_app.config['SITE_UI_URL']+"/records/iiif/"+obj["id"]+"pX"


class IIIFPresiSchema(Schema):
    """IIIF Presentation API Marshmallow Schema."""

    class Meta: #todo: sort ordering this "should" be first.
        include = {
          '@context': fields.Constant('http://iiif.io/api/presentation/3/context.json')
        }
    id = fields.Method('make_manifest_id')
    label = fields.Str(attribute="metadata.title")
    type = fields.Constant('Manifest')

    def make_manifest_id(self,obj):
        return current_app.config['SITE_UI_URL']+"/records/iiif/"+ obj["id"] # todo: get records prefix from vars (will it ever change in RDM?)
