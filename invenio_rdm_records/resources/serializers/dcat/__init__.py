# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Datacite to DCAT serializer."""

import mimetypes
from importlib.resources import files

from datacite import schema45
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer
from idutils import detect_identifier_schemes, to_url
from lxml import etree as ET
from werkzeug.utils import cached_property

from ....contrib.journal.processors import JournalDataciteDumper
from ....resources.serializers.dcat.schema import DcatSchema


class DCATSerializer(MarshmallowSerializer):
    """DCAT serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=DcatSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={"dumpers": [JournalDataciteDumper()]},  # Order matters
            encoder=self._etree_tostring,
            **options,
        )

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
        file_ = (
            files("invenio_rdm_records.resources.serializers")
            / "dcat/datacite-to-dcat-ap.xsl"
        )
        with file_.open("rb") as f:
            xsl = ET.XML(f.read())
        transform = ET.XSLT(xsl)
        return transform

    def _add_files(self, root, files):
        """Add files information via distribution elements."""
        ns = root.nsmap

        def download_url(file):
            url = file.get("download_url")
            return {"{{{rdf}}}resource".format(**ns): url} if url else None

        def media_type(file):
            return mimetypes.guess_type(file["key"])[0]

        def byte_size(file):
            return str(file["size"]) if file.get("size") else None

        def access_url(file):
            url = file.get("access_url")
            return {"{{{rdf}}}resource".format(**ns): url} if url else None

        files_fields = {
            "{{{dcat}}}downloadURL": download_url,
            "{{{dcat}}}mediaType": media_type,
            "{{{dcat}}}byteSize": byte_size,
            "{{{dcat}}}accessURL": access_url,
            # TODO: there's also "spdx:checksum", but it's not in the W3C spec yet
        }

        for f in files:
            dist_wrapper = ET.SubElement(root[0], "{{{dcat}}}distribution".format(**ns))
            dist = ET.SubElement(dist_wrapper, "{{{dcat}}}Distribution".format(**ns))

            for tag, func in files_fields.items():
                tag_value = func(f)

                if tag_value:
                    el = ET.SubElement(dist, tag.format(**ns))
                    if isinstance(tag_value, str):
                        el.text = tag_value
                    if isinstance(tag_value, dict):
                        el.attrib.update(tag_value)

    def add_missing_creatibutor_links(self, rdf_tree):
        """Add missing `rdf:about` attributes to <rdf:Description> within <dct:creator> and <dct:contributor> and <foaf:Organization> within <org:memberOf>."""
        namespaces = rdf_tree.nsmap

        # Helper function to add rdf:about based on identifier
        def add_rdf_about(element, identifier_elem):
            identifier = identifier_elem.text.strip()
            schemes = detect_identifier_schemes(identifier)
            rdf_about_url = next(
                (
                    to_url(identifier, scheme=scheme)
                    for scheme in schemes
                    if to_url(identifier, scheme)
                ),
                None,
            )
            if rdf_about_url:
                element.set(
                    "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", rdf_about_url
                )

        # Process <dct:creator> and <dct:contributor>
        contributors_and_creators = rdf_tree.xpath(
            "//dct:creator/rdf:Description | //dct:contributor/rdf:Description",
            namespaces=namespaces,
        )

        for description in contributors_and_creators:
            # Add rdf:about for creator/contributor if missing
            if not description.get(
                "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
            ):
                identifier_elem = description.find("dct:identifier", namespaces)
                if identifier_elem is not None:
                    add_rdf_about(description, identifier_elem)

        # Process <foaf:Organization> within <org:memberOf> at any level
        organizations = rdf_tree.xpath(
            "//org:memberOf//foaf:Organization[not(@rdf:about)]",
            namespaces=namespaces,
        )

        for org in organizations:
            org_identifier_elem = org.find("dct:identifier", namespaces)
            if org_identifier_elem is not None:
                add_rdf_about(org, org_identifier_elem)

        return rdf_tree

    def _xpath_string_escape(self, input_str):
        """Create a concatenation of alternately-quoted strings that is always a valid XPath expression."""
        parts = input_str.split("'")
        if len(parts) > 1:
            return "concat('" + "',\"'\",'".join(parts) + "')"
        else:
            return f"'{input_str}'"

    def add_subjects_uri(self, rdf_tree, subjects):
        """Add valueURI of subjects to the corresponding dct:subject elements in the RDF tree."""
        namespaces = rdf_tree.nsmap
        for subject in subjects:
            value_uri = subject.get("valueURI")
            subject_label = subject.get("subject")
            subject_scheme = subject.get("subjectScheme")
            subject_props = subject.get("subjectProps", {})

            if value_uri and subject_label and subject_scheme:
                # Find the corresponding dct:subject element by prefLabel and subjectScheme
                subject_label_escaped = self._xpath_string_escape(subject_label)
                subject_element = rdf_tree.xpath(
                    f"""
                    //dct:subject[
                        skos:Concept[
                            skos:prefLabel[text()={subject_label_escaped}]
                            and skos:inScheme/skos:ConceptScheme/dct:title[text()='{subject_scheme}']
                        ]
                    ]
                    """,
                    namespaces=namespaces,
                )[0]

                if subject_element is not None:
                    # Add the valueURI to the dct:subject element as rdf:about
                    subject_element.set(
                        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", value_uri
                    )

                # Check if
                #  subject has a definition in its props
                definition = subject_props.get("definition")
                if definition:
                    concept_elem = subject_element.find(
                        ".//skos:Concept", namespaces=namespaces
                    )
                    if concept_elem is not None:
                        skos_definition = ET.Element(
                            "{http://www.w3.org/2004/02/skos/core#}definition"
                        )
                        skos_definition.text = definition
                        concept_elem.append(skos_definition)

        return rdf_tree

    def transform_with_xslt(self, dc_record, **kwargs):
        """Transform record with XSLT."""
        dc_etree = schema45.dump_etree(dc_record)
        dc_namespace = schema45.ns[None]
        dc_etree.tag = "{{{0}}}resource".format(dc_namespace)
        dcat_etree = self.xslt_transform_func(dc_etree).getroot()

        # Add valueURI to subjects
        subjects = dc_record.get("subjects", [])
        if subjects:
            dcat_etree = self.add_subjects_uri(dcat_etree, subjects)

        # Add the identifier links for creators & contributors if missing
        dcat_etree = self.add_missing_creatibutor_links(dcat_etree)

        # Inject files in results (since the XSLT can't do that by default)
        files_data = dc_record.get("_files", [])
        if files_data:
            self._add_files(
                root=dcat_etree,
                files=files_data,
            )
        return dcat_etree
