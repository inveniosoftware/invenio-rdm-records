# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers.

ATTENTION: Serializers MUST NOT query for data (e.g. use a service)!

The only allowed data querying is "get_vocabulary_props()" which is cached.
Querying for data in a serializer will most likely result in very bad
performance for the OAI-PMH server and search results serialzations.
"""

from .bibtex import BibtexSerializer
from .cff import CFFSerializer
from .codemeta import CodemetaSerializer
from .csl import CSLJSONSerializer, StringCitationSerializer
from .csv import CSVRecordSerializer
from .datacite import DataCite43JSONSerializer, DataCite43XMLSerializer
from .datapackage import DataPackageSerializer
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
from .signposting import (
    FAIRSignpostingProfileLvl1Serializer,
    FAIRSignpostingProfileLvl2Serializer,
)
from .ui import UIJSONSerializer

__all__ = (
    "BibtexSerializer",
    "CFFSerializer",
    "CSLJSONSerializer",
    "CSVRecordSerializer",
    "DataCite43JSONSerializer",
    "DataCite43XMLSerializer",
    "DataPackageSerializer",
    "DublinCoreJSONSerializer",
    "DublinCoreXMLSerializer",
    "FAIRSignpostingProfileLvl1Serializer",
    "FAIRSignpostingProfileLvl2Serializer",
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
