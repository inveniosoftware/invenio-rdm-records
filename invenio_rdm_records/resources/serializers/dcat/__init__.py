# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Datacite to DCAT serializer."""

from datacite import schema43
from lxml import etree as ET
from pkg_resources import resource_stream
from werkzeug.utils import cached_property

from invenio_rdm_records.resources.serializers import DataCite43XMLSerializer


class DCATSerializer(DataCite43XMLSerializer):
    """DCAT serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(encoder=self._etree_tostring)

    def _etree_tostring(self, record, **kwargs):
        root = self.transform_with_xslt(record, **kwargs)
        return ET.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode("utf-8")

    @cached_property
    def xslt_transform_func(self):
        """Return the DCAT XSLT transformation function."""
        with resource_stream(
            "invenio_rdm_records.resources.serializers", "dcat/datacite-to-dcat-ap.xsl"
        ) as f:
            xsl = ET.XML(f.read())
        transform = ET.XSLT(xsl)
        return transform

    def transform_with_xslt(self, dc_record, **kwargs):
        """Transform record with XSLT."""
        dc_etree = schema43.dump_etree(dc_record)
        dc_namespace = schema43.ns[None]
        dc_etree.tag = "{{{0}}}resource".format(dc_namespace)
        dcat_etree = self.xslt_transform_func(dc_etree).getroot()

        return dcat_etree
