# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from invenio_rdm_records.resources.serializers import DCATSerializer


def test_dcat_serializer(running_app, full_record_to_dict):
    full_record_to_dict["links"] = dict(self_html="https://self-link.com")
    full_record_to_dict["metadata"]["related_identifiers"].append(
        {
            "identifier": "10.1234/baz.qux",
            "relation_type": {
                "id": "hasmetadata",
                "title": {
                    "en": "Has metadata",
                },
            },
            "resource_type": {
                "id": "image",
                "title": {
                    "en": "Image",
                },
            },
            "scheme": "doi",
        }
    )
    full_record_to_dict["metadata"]["subjects"][0]["subject"] = "Women's studies"
    expected_data = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        'xmlns:adms="http://www.w3.org/ns/adms#" '
        'xmlns:bibo="http://purl.org/ontology/bibo/" '
        'xmlns:citedcat="https://w3id.org/citedcat-ap/" '
        'xmlns:dct="http://purl.org/dc/terms/" '
        'xmlns:dctype="http://purl.org/dc/dcmitype/" '
        'xmlns:dcat="http://www.w3.org/ns/dcat#" '
        'xmlns:foaf="http://xmlns.com/foaf/0.1/" '
        'xmlns:gsp="http://www.opengis.net/ont/geosparql#" '
        'xmlns:locn="http://www.w3.org/ns/locn#" '
        'xmlns:org="http://www.w3.org/ns/org#" '
        'xmlns:owl="http://www.w3.org/2002/07/owl#" '
        'xmlns:prov="http://www.w3.org/ns/prov#" '
        'xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" '
        'xmlns:skos="http://www.w3.org/2004/02/skos/core#" '
        'xmlns:vcard="http://www.w3.org/2006/vcard/ns#" '
        'xmlns:wdrs="http://www.w3.org/2007/05/powder-s#">\n'
        '  <rdf:Description rdf:about="https://doi.org/10.1234/12345-abcde">\n'
        '    <rdf:type rdf:resource="http://www.w3.org/ns/dcat#Dataset"/>\n'
        '    <dct:type rdf:resource="http://purl.org/dc/dcmitype/Image"/>\n'
        "    <dct:identifier "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">https://doi.org/10.1234/12345-abcde</dct:identifier>\n'
        '    <foaf:page rdf:resource="https://doi.org/10.1234/12345-abcde"/>\n'
        "    <dct:creator>\n"
        '      <rdf:Description rdf:about="https://orcid.org/0000-0001-8135-3489">\n'
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>\n'
        "        <foaf:name>Nielsen, Lars Holm</foaf:name>\n"
        "        <foaf:givenName>Lars Holm</foaf:givenName>\n"
        "        <foaf:familyName>Nielsen</foaf:familyName>\n"
        "        <org:memberOf>\n"
        "          <foaf:Organization>\n"
        "            <foaf:name>CERN</foaf:name>\n"
        "          </foaf:Organization>\n"
        "        </org:memberOf>\n"
        "        <org:memberOf>\n"
        "          <foaf:Organization>\n"
        "            <foaf:name>free-text</foaf:name>\n"
        "          </foaf:Organization>\n"
        "        </org:memberOf>\n"
        "      </rdf:Description>\n"
        "    </dct:creator>\n"
        "    <dct:creator>\n"
        "      <rdf:Description>\n"
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>\n'
        "        <foaf:name>Tom, Blabin</foaf:name>\n"
        "        <foaf:givenName>Blabin</foaf:givenName>\n"
        "        <foaf:familyName>Tom</foaf:familyName>\n"
        "      </rdf:Description>\n"
        "    </dct:creator>\n"
        "    <dct:title>InvenioRDM</dct:title>\n"
        "    <dct:publisher>\n"
        "      <foaf:Agent>\n"
        "        <foaf:name>InvenioRDM</foaf:name>\n"
        "      </foaf:Agent>\n"
        "    </dct:publisher>\n"
        "    <dct:issued "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#gYear">2018</dct:issued>\n'
        '    <dct:subject rdf:about="http://id.nlm.nih.gov/mesh/A-D000007">\n'
        "      <skos:Concept>\n"
        "        <skos:prefLabel>Women's studies</skos:prefLabel>\n"
        "        <skos:inScheme>\n"
        "          <skos:ConceptScheme>\n"
        "            <dct:title>MeSH</dct:title>\n"
        "          </skos:ConceptScheme>\n"
        "        </skos:inScheme>\n"
        "      </skos:Concept>\n"
        "    </dct:subject>\n"
        "    <dcat:keyword>custom</dcat:keyword>\n"
        "    <citedcat:isFundedBy>\n"
        "      <foaf:Project>\n"
        "        <dct:identifier "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#string">111023</dct:identifier>\n'
        "        <dct:title>Launching of the research program on meaning "
        "processing</dct:title>\n"
        "        <citedcat:isAwardedBy>\n"
        "          <foaf:Organization>\n"
        "            <dct:identifier "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#string"/>\n'
        "            <foaf:name>European Commission</foaf:name>\n"
        "          </foaf:Organization>\n"
        "        </citedcat:isAwardedBy>\n"
        "      </foaf:Project>\n"
        "    </citedcat:isFundedBy>\n"
        "    <citedcat:funder>\n"
        "      <foaf:Organization>\n"
        "        <dct:identifier "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#string"/>\n'
        "        <foaf:name>European Commission</foaf:name>\n"
        "      </foaf:Organization>\n"
        "    </citedcat:funder>\n"
        "    <dct:contributor>\n"
        '      <rdf:Description rdf:about="https://orcid.org/0000-0001-8135-3489">\n'
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>\n'
        "        <foaf:name>Nielsen, Lars Holm</foaf:name>\n"
        "        <foaf:givenName>Lars Holm</foaf:givenName>\n"
        "        <foaf:familyName>Nielsen</foaf:familyName>\n"
        "        <org:memberOf>\n"
        "          <foaf:Organization>\n"
        "            <foaf:name>CERN</foaf:name>\n"
        "          </foaf:Organization>\n"
        "        </org:memberOf>\n"
        "        <org:memberOf>\n"
        "          <foaf:Organization>\n"
        "            <foaf:name>TU Wien</foaf:name>\n"
        "          </foaf:Organization>\n"
        "        </org:memberOf>\n"
        "      </rdf:Description>\n"
        "    </dct:contributor>\n"
        "    <dct:contributor>\n"
        "      <rdf:Description>\n"
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>\n'
        "        <foaf:name>Dirk, Dirkin</foaf:name>\n"
        "        <foaf:givenName>Dirkin</foaf:givenName>\n"
        "        <foaf:familyName>Dirk</foaf:familyName>\n"
        "      </rdf:Description>\n"
        "    </dct:contributor>\n"
        "    <dct:issued "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2018/2020-09</dct:issued>\n'
        "    <dct:date "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1939/1945</dct:date>\n'
        "    <dct:modified "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2023-11-14</dct:modified>\n'
        "    <dct:language "
        'rdf:resource="http://publications.europa.eu/resource/authority/language/DAN"/>\n'
        '    <owl:sameAs rdf:resource="https://self-link.com"/>\n'
        "    <adms:identifier>\n"
        "      <adms:Identifier>\n"
        "        <skos:notation "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">https://self-link.com</skos:notation>\n'
        "        <adms:schemeAgency>URL</adms:schemeAgency>\n"
        "      </adms:Identifier>\n"
        "    </adms:identifier>\n"
        "    <adms:identifier>\n"
        "      <adms:Identifier>\n"
        "        <skos:notation>oai:invenio-rdm.com:12345-abcde</skos:notation>\n"
        "        <adms:schemeAgency>oai</adms:schemeAgency>\n"
        "      </adms:Identifier>\n"
        "    </adms:identifier>\n"
        "    <owl:sameAs "
        'rdf:resource="http://adsabs.harvard.edu/abs/1924MNRAS..84..308E"/>\n'
        "    <adms:identifier>\n"
        "      <adms:Identifier>\n"
        "        <skos:notation "
        'rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">http://adsabs.harvard.edu/abs/1924MNRAS..84..308E</skos:notation>\n'
        "        <adms:schemeAgency>bibcode</adms:schemeAgency>\n"
        "      </adms:Identifier>\n"
        "    </adms:identifier>\n"
        "    <dct:isReferencedBy>\n"
        '      <rdf:Description rdf:about="https://doi.org/10.1234/foo.bar">\n'
        "        <dct:identifier>https://doi.org/10.1234/foo.bar</dct:identifier>\n"
        '        <rdf:type rdf:resource="http://www.w3.org/ns/dcat#Dataset"/>\n'
        '        <dct:type rdf:resource="http://purl.org/dc/dcmitype/Dataset"/>\n'
        "      </rdf:Description>\n"
        "    </dct:isReferencedBy>\n"
        "    <foaf:isPrimaryTopicOf>\n"
        '      <rdf:Description rdf:about="https://doi.org/10.1234/baz.qux">\n'
        "        <dct:identifier>https://doi.org/10.1234/baz.qux</dct:identifier>\n"
        '        <rdf:type rdf:resource="http://www.w3.org/ns/dcat#CatalogRecord"/>\n'
        "      </rdf:Description>\n"
        "    </foaf:isPrimaryTopicOf>\n"
        "    <dct:isVersionOf>\n"
        '      <rdf:Description rdf:about="https://doi.org/10.1234/pgfpj-at058">\n'
        "        "
        "<dct:identifier>https://doi.org/10.1234/pgfpj-at058</dct:identifier>\n"
        "      </rdf:Description>\n"
        "    </dct:isVersionOf>\n"
        "    <owl:versionInfo>v1.0</owl:versionInfo>\n"
        "    <dct:description>A description with HTML tags</dct:description>\n"
        "    <dct:provenance>\n"
        "      <dct:ProvenanceStatement>\n"
        "        <rdfs:label>Bla bla bla</rdfs:label>\n"
        "      </dct:ProvenanceStatement>\n"
        "    </dct:provenance>\n"
        "    <dct:spatial>\n"
        "      <dct:Location>\n"
        "        <rdf:type "
        'rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>\n'
        "        <skos:prefLabel>test location place</skos:prefLabel>\n"
        "        <locn:geographicName>test location place</locn:geographicName>\n"
        "        <dcat:centroid "
        'rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral"><![CDATA[POINT(-32.94682 '
        "-60.63932)]]></dcat:centroid>\n"
        "        <dcat:centroid "
        'rdf:datatype="http://www.opengis.net/ont/geosparql#gmlLiteral"><![CDATA[<gml:Point '
        'srsName="http://www.opengis.net/def/crs/OGC/1.3/CRS84"><gml:pos '
        'srsDimension="2">-32.94682 '
        "-60.63932</gml:pos></gml:Point>]]></dcat:centroid>\n"
        "        <dcat:centroid "
        'rdf:datatype="http://www.opengis.net/ont/geosparql#geoJSONLiteral"><![CDATA[{"type":"Point","coordinates":[-32.94682,-60.63932]}]]></dcat:centroid>\n'
        "      </dct:Location>\n"
        "    </dct:spatial>\n"
        "    <dcat:distribution>\n"
        "      <dcat:Distribution>\n"
        "        <dct:extent>\n"
        "          <dct:SizeOrDuration>\n"
        "            <rdfs:label>11 pages</rdfs:label>\n"
        "          </dct:SizeOrDuration>\n"
        "        </dct:extent>\n"
        "        <dcat:mediaType "
        'rdf:resource="https://www.iana.org/assignments/media-types/application/pdf"/>\n'
        "        <dct:rights>\n"
        "          <dct:RightsStatement "
        'rdf:about="https://customlicense.org/licenses/by/4.0/">\n'
        "            <rdfs:label>A custom license</rdfs:label>\n"
        "          </dct:RightsStatement>\n"
        "        </dct:rights>\n"
        "        <dct:license "
        'rdf:resource="https://creativecommons.org/licenses/by/4.0/legalcode"/>\n'
        "        <dcat:accessURL "
        'rdf:resource="https://doi.org/10.1234/12345-abcde"/>\n'
        "      </dcat:Distribution>\n"
        "    </dcat:distribution>\n"
        "    <dcat:distribution>\n"
        "      <dcat:Distribution>\n"
        "        <dcat:downloadURL "
        'rdf:resource="https://127.0.0.1:5000/records/12345-abcde/files/test.txt"/>\n'
        "        <dcat:mediaType>text/plain</dcat:mediaType>\n"
        "        <dcat:byteSize>9</dcat:byteSize>\n"
        "        <dcat:accessURL "
        'rdf:resource="https://doi.org/10.1234/12345-abcde"/>\n'
        "      </dcat:Distribution>\n"
        "    </dcat:distribution>\n"
        "  </rdf:Description>\n"
        "</rdf:RDF>\n"
    )

    serializer = DCATSerializer()
    serialized_record = serializer.serialize_object(full_record_to_dict)
    assert expected_data == serialized_record
