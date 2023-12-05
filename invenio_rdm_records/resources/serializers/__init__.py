# -*- coding: utf-8 -*-
#
# Copyright (C) 2020, 2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from .bibtex import BibtexSerializer
from .cff import CFFSerializer
from .codemeta import CodemetaSerializer
from .csl import CSLJSONSerializer, StringCitationSerializer
from .datacite import DataCite43JSONSerializer, DataCite43XMLSerializer
from .dcat import DCATSerializer
from .dublincore import DublinCoreJSONSerializer, DublinCoreXMLSerializer
from .geojson import GeoJSONSerializer
from .iiif import (
    IIIFCanvasV2JSONSerializer,
    IIIFInfoV2JSONSerializer,
    IIIFManifestV2JSONSerializer,
    IIIFSequenceV2JSONSerializer,
)
from .marcxml import MARCXMLSerializer
from .schemaorg import SchemaorgJSONLDSerializer
from .ui import UIJSONSerializer

__all__ = (
    "BibtexSerializer",
    "CFFSerializer",
    "CSLJSONSerializer",
    "DataCite43JSONSerializer",
    "DataCite43XMLSerializer",
    "DublinCoreJSONSerializer",
    "DublinCoreXMLSerializer",
    "GeoJSONSerializer",
    "IIIFCanvasV2JSONSerializer",
    "IIIFInfoV2JSONSerializer",
    "IIIFManifestV2JSONSerializer",
    "IIIFSequenceV2JSONSerializer",
    "MARCXMLSerializer",
    "SchemaorgJSONLDSerializer",
    "StringCitationSerializer",
    "UIJSONSerializer",
    "DCATSerializer",
    "CodemetaSerializer",
)
