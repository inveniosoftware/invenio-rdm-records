# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from invenio_rdm_records.resources.serializers import DCATSerializer


def test_dcat_serializer(running_app, enhanced_full_record):
    enhanced_full_record["links"] = dict(self_html="https://self-link.com")
    expected_data = [
        "<?xml version='1.0' encoding='utf-8'?>",
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:adms="http://www.w3.org/ns/adms#" xmlns:bibo="http://purl.org/ontology/bibo/" xmlns:citedcat="https://w3id.org/citedcat-ap/" xmlns:dct="http://purl.org/dc/terms/" xmlns:dctype="http://purl.org/dc/dcmitype/" xmlns:dcat="http://www.w3.org/ns/dcat#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:gsp="http://www.opengis.net/ont/geosparql#" xmlns:locn="http://www.w3.org/ns/locn#" xmlns:org="http://www.w3.org/ns/org#" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:prov="http://www.w3.org/ns/prov#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:vcard="http://www.w3.org/2006/vcard/ns#" xmlns:wdrs="http://www.w3.org/2007/05/powder-s#">',  # noqa
        '  <rdf:Description rdf:about="https://doi.org/10.1234/inveniordm.1234">',  # noqa
        '    <rdf:type rdf:resource="http://www.w3.org/ns/dcat#Dataset"/>',  # noqa
        '    <dct:type rdf:resource="http://purl.org/dc/dcmitype/Image"/>',  # noqa
        '    <dct:identifier rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">https://doi.org/10.1234/inveniordm.1234</dct:identifier>',  # noqa
        '    <foaf:page rdf:resource="https://doi.org/10.1234/inveniordm.1234"/>',  # noqa
        "    <dct:creator>",
        '      <rdf:Description rdf:about="https://orcid.org/0000-0001-8135-3489">',  # noqa
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>',  # noqa
        "        <foaf:name>Nielsen, Lars Holm</foaf:name>",
        "        <foaf:givenName>Lars Holm</foaf:givenName>",
        "        <foaf:familyName>Nielsen</foaf:familyName>",
        "        <org:memberOf>",
        "          <foaf:Organization>",
        "            <foaf:name>free-text</foaf:name>",
        "          </foaf:Organization>",
        "        </org:memberOf>",
        "        <org:memberOf>",
        '          <foaf:Organization rdf:about="https://ror.org/https://ror.org/01ggx4157">',  # noqa
        '            <dct:identifier rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">https://ror.org/01ggx4157</dct:identifier>',  # noqa
        "            <foaf:name>CERN</foaf:name>",
        "          </foaf:Organization>",
        "        </org:memberOf>",
        "      </rdf:Description>",
        "    </dct:creator>",
        "    <dct:creator>",
        "      <rdf:Description>",
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>',  # noqa
        "        <foaf:name>Tom, Blabin</foaf:name>",
        "        <foaf:givenName>Blabin</foaf:givenName>",
        "        <foaf:familyName>Tom</foaf:familyName>",
        "      </rdf:Description>",
        "    </dct:creator>",
        "    <dct:title>InvenioRDM</dct:title>",
        "    <dct:publisher>",
        "      <foaf:Agent>",
        "        <foaf:name>InvenioRDM</foaf:name>",
        "      </foaf:Agent>",
        "    </dct:publisher>",
        '    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#gYear">2018</dct:issued>',  # noqa
        "    <dcat:keyword>custom</dcat:keyword>",
        "    <citedcat:isFundedBy>",
        "      <foaf:Project>",
        '        <dct:identifier rdf:datatype="http://www.w3.org/2001/XMLSchema#string">111023</dct:identifier>',  # noqa
        "        <dct:title>Launching of the research program on meaning processing</dct:title>",
        '        <citedcat:isAwardedBy rdf:resource="https://ror.org/00k4n6c32"/>',  # noqa
        "      </foaf:Project>",
        "    </citedcat:isFundedBy>",
        '    <citedcat:funder rdf:resource="https://ror.org/00k4n6c32"/>',  # noqa
        "    <dct:contributor>",
        '      <rdf:Description rdf:about="https://orcid.org/0000-0001-8135-3489">',  # noqa
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>',  # noqa
        "        <foaf:name>Nielsen, Lars Holm</foaf:name>",
        "        <foaf:givenName>Lars Holm</foaf:givenName>",
        "        <foaf:familyName>Nielsen</foaf:familyName>",
        "        <org:memberOf>",
        "          <foaf:Organization>",
        "            <foaf:name>TU Wien</foaf:name>",
        "          </foaf:Organization>",
        "        </org:memberOf>",
        "        <org:memberOf>",
        '          <foaf:Organization rdf:about="https://ror.org/https://ror.org/01ggx4157">',  # noqa
        '            <dct:identifier rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">https://ror.org/01ggx4157</dct:identifier>',  # noqa
        "            <foaf:name>CERN</foaf:name>",
        "          </foaf:Organization>",
        "        </org:memberOf>",
        "      </rdf:Description>",
        "    </dct:contributor>",
        "    <dct:contributor>",
        "      <rdf:Description>",
        '        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>',  # noqa
        "        <foaf:name>Dirk, Dirkin</foaf:name>",
        "        <foaf:givenName>Dirkin</foaf:givenName>",
        "        <foaf:familyName>Dirk</foaf:familyName>",
        "      </rdf:Description>",
        "    </dct:contributor>",
        '    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2018/2020-09</dct:issued>',  # noqa
        '    <dct:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1939/1945</dct:date>',  # noqa
        '    <dct:language rdf:resource="http://publications.europa.eu/resource/authority/language/DAN"/>',  # noqa
        '    <owl:sameAs rdf:resource="https://self-link.com"/>',  # noqa
        "    <adms:identifier>",
        "      <adms:Identifier>",
        '        <skos:notation rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">https://self-link.com</skos:notation>',  # noqa
        "        <adms:schemeAgency>URL</adms:schemeAgency>",
        "      </adms:Identifier>",
        "    </adms:identifier>",
        "    <adms:identifier>",
        "      <adms:Identifier>",
        "        <skos:notation>oai:invenio-rdm.com:vs40t-1br10</skos:notation>",
        "        <adms:schemeAgency>oai</adms:schemeAgency>",
        "      </adms:Identifier>",
        "    </adms:identifier>",
        '    <owl:sameAs rdf:resource="http://adsabs.harvard.edu/abs/1924MNRAS..84..308E"/>',  # noqa
        "    <adms:identifier>",
        "      <adms:Identifier>",
        '        <skos:notation rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">http://adsabs.harvard.edu/abs/1924MNRAS..84..308E</skos:notation>',  # noqa
        "        <adms:schemeAgency>bibcode</adms:schemeAgency>",
        "      </adms:Identifier>",
        "    </adms:identifier>",
        "    <dct:isReferencedBy>",
        '      <rdf:Description rdf:about="https://doi.org/10.1234/foo.bar">',  # noqa
        "        <dct:identifier>https://doi.org/10.1234/foo.bar</dct:identifier>",
        '        <rdf:type rdf:resource="http://www.w3.org/ns/dcat#Dataset"/>',  # noqa
        '        <dct:type rdf:resource="http://purl.org/dc/dcmitype/Dataset"/>',  # noqa
        "      </rdf:Description>",
        "    </dct:isReferencedBy>",
        "    <dct:isVersionOf>",
        '      <rdf:Description rdf:about="https://doi.org/10.1234/inveniordm.1234.parent">',  # noqa
        "        <dct:identifier>https://doi.org/10.1234/inveniordm.1234.parent</dct:identifier>",  # noqa
        "      </rdf:Description>",
        "    </dct:isVersionOf>",
        "    <owl:versionInfo>v1.0</owl:versionInfo>",
        "    <dct:description>A description with HTML tags</dct:description>",
        "    <dct:provenance>",
        "      <dct:ProvenanceStatement>",
        "        <rdfs:label>Bla bla bla</rdfs:label>",
        "      </dct:ProvenanceStatement>",
        "    </dct:provenance>",
        "    <dct:spatial>",
        "      <dct:Location>",
        '        <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>',  # noqa
        "        <skos:prefLabel>test location place</skos:prefLabel>",
        "        <locn:geographicName>test location place</locn:geographicName>",
        '        <dcat:centroid rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral"><![CDATA[POINT(-60.63932 -32.94682)]]></dcat:centroid>',  # noqa
        '        <dcat:centroid rdf:datatype="http://www.opengis.net/ont/geosparql#gmlLiteral"><![CDATA[<gml:Point srsName="http://www.opengis.net/def/crs/OGC/1.3/CRS84"><gml:pos srsDimension="2">-60.63932 -32.94682</gml:pos></gml:Point>]]></dcat:centroid>',  # noqa
        '        <dcat:centroid rdf:datatype="http://www.opengis.net/ont/geosparql#geoJSONLiteral"><![CDATA[{"type":"Point","coordinates":[-60.63932,-32.94682]}]]></dcat:centroid>',  # noqa
        "      </dct:Location>",
        "    </dct:spatial>",
        "    <dcat:distribution>",
        "      <dcat:Distribution>",
        "        <dct:extent>",
        "          <dct:SizeOrDuration>",
        "            <rdfs:label>11 pages</rdfs:label>",
        "          </dct:SizeOrDuration>",
        "        </dct:extent>",
        '        <dcat:mediaType rdf:resource="https://www.iana.org/assignments/media-types/application/pdf"/>',  # noqa
        "        <dct:rights>",
        '          <dct:RightsStatement rdf:about="https://customlicense.org/licenses/by/4.0/">',  # noqa
        "            <rdfs:label>A custom license</rdfs:label>",
        "          </dct:RightsStatement>",
        "        </dct:rights>",
        '        <dct:license rdf:resource="https://creativecommons.org/licenses/by/4.0/legalcode"/>',  # noqa
        '        <dcat:accessURL rdf:resource="https://doi.org/10.1234/inveniordm.1234"/>',  # noqa
        "      </dcat:Distribution>",
        "    </dcat:distribution>",
        "    <dcat:distribution>",
        "      <dcat:Distribution>",
        '        <dcat:downloadURL rdf:resource="https://127.0.0.1:5000/records/w502q-xzh22/files/big-dataset.zip"/>',  # noqa
        "        <dcat:mediaType>application/zip</dcat:mediaType>",  # noqa
        "        <dcat:byteSize>1114324524355</dcat:byteSize>",  # noqa
        '        <dcat:accessURL rdf:resource="https://doi.org/10.1234/inveniordm.1234"/>',  # noqa
        "      </dcat:Distribution>",
        "    </dcat:distribution>",
        "  </rdf:Description>",
        "</rdf:RDF>",
        "",  # this is because of the split
    ]

    serializer = DCATSerializer()
    serialized_record = serializer.serialize_object(enhanced_full_record)
    assert serialized_record == "\n".join(expected_data)
