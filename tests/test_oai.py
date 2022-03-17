# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test OAI-PMH support."""

from copy import deepcopy

from lxml import etree

from invenio_rdm_records.oai import datacite_etree, dublincore_etree, \
    oai_datacite_etree

# This tests would ideally be E2E. However, due to the lack of assets building
# in tests we cannot safely query the `/oai2d` endpoint, it will fail due to
# the lack of the `manifest.json` file.


def test_dublincore_serializer(running_app, full_record):
    full_record = deepcopy(full_record)
    full_record["access"]["status"] = "embargoed"

    expected_value = (
        '<oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n'  # noqa
        '  <dc:contributor>Nielsen, Lars Holm</dc:contributor>\n'
        '  <dc:creator>Nielsen, Lars Holm</dc:creator>\n'
        '  <dc:date>2018/2020-09</dc:date>\n'
        '  <dc:date>info:eu-repo/date/embargoEnd/2131-01-01</dc:date>\n'
        '  <dc:description>A description \nwith HTML tags</dc:description>\n'
        '  <dc:description>Bla bla bla</dc:description>\n'
        '  <dc:format>application/pdf</dc:format>\n'
        '  <dc:identifier>1924MNRAS..84..308E</dc:identifier>\n'
        '  <dc:identifier>10.5281/inveniordm.1234</dc:identifier>\n'
        '  <dc:language>dan</dc:language>\n'
        '  <dc:language>eng</dc:language>\n'
        '  <dc:publisher>InvenioRDM</dc:publisher>\n'
        '  <dc:relation>doi:10.1234/foo.bar</dc:relation>\n'
        '  <dc:rights>info:eu-repo/semantics/embargoedAccess</dc:rights>\n'
        '  <dc:rights>A custom license</dc:rights>\n'
        '  <dc:rights>https://customlicense.org/licenses/by/4.0/</dc:rights>\n'
        '  <dc:rights>Creative Commons Attribution 4.0 International</dc:rights>\n'  # noqa
        '  <dc:rights>https://creativecommons.org/licenses/by/4.0/legalcode</dc:rights>\n'  # noqa
        '  <dc:subject>custom</dc:subject>\n'
        '  <dc:title>InvenioRDM</dc:title>\n'
        '  <dc:type>info:eu-repo/semantic/other</dc:type>\n'
        '</oai_dc:dc>\n'
    )
    record = {"_source": full_record}
    ser_rec = etree.tostring(
        dublincore_etree(None, record),
        pretty_print=True
    )
    assert expected_value == ser_rec.decode("utf-8")


def test_datacite_serializer(running_app, full_record):
    expected_value = (
        '<resource xmlns="http://datacite.org/schema/kernel-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.3/metadata.xsd">\n'  # noqa
        '  <identifier identifierType="DOI">10.5281/inveniordm.1234</identifier>\n'  # noqa
        '  <alternateIdentifiers>\n'
        '    <alternateIdentifier alternateIdentifierType="bibcode">1924MNRAS..84..308E</alternateIdentifier>\n'  # noqa
        '  </alternateIdentifiers>\n'
        '  <creators>\n'
        '    <creator>\n'
        '      <creatorName nameType="Personal">Nielsen, Lars Holm</creatorName>\n'  # noqa
        '      <givenName>Lars Holm</givenName>\n'
        '      <familyName>Nielsen</familyName>\n'
        '      <nameIdentifier nameIdentifierScheme="ORCID">0000-0001-8135-3489</nameIdentifier>\n'  # noqa
        '      <affiliation>free-text</affiliation>\n'
        '      <affiliation affiliationIdentifier="01ggx4157" affiliationIdentifierScheme="ROR">CERN</affiliation>\n'  # noqa
        '    </creator>\n'
        '  </creators>\n'
        '  <titles>\n'
        '    <title>InvenioRDM</title>\n'
        '    <title xml:lang="eng" titleType="Subtitle">a research data management platform</title>\n'  # noqa
        '  </titles>\n'
        '  <publisher>InvenioRDM</publisher>\n'
        '  <publicationYear>2018</publicationYear>\n'
        '  <subjects>\n'
        '    <subject>custom</subject>\n'
        '    <subject subjectScheme="MeSH">Abdominal Injuries</subject>\n'
        '  </subjects>\n'
        '  <contributors>\n'
        '    <contributor contributorType="Other">\n'
        '      <contributorName nameType="Personal">Nielsen, Lars Holm</contributorName>\n'  # noqa
        '      <givenName>Lars Holm</givenName>\n'
        '      <familyName>Nielsen</familyName>\n'
        '      <nameIdentifier nameIdentifierScheme="ORCID">0000-0001-8135-3489</nameIdentifier>\n'  # noqa
        '      <affiliation affiliationIdentifier="01ggx4157" affiliationIdentifierScheme="ROR">CERN</affiliation>\n'  # noqa
        '    </contributor>\n'
        '  </contributors>\n'
        '  <dates>\n'
        '    <date dateType="Issued">2018/2020-09</date>\n'
        '    <date dateType="Other" dateInformation="A date">1939/1945</date>\n'  # noqa
        '  </dates>\n'
        '  <language>dan</language>\n'
        '  <resourceType resourceTypeGeneral="Image">Photo</resourceType>\n'
        '  <relatedIdentifiers>\n'
        '    <relatedIdentifier relatedIdentifierType="DOI" relationType="IsCitedBy" resourceTypeGeneral="Dataset">10.1234/foo.bar</relatedIdentifier>\n'  # noqa
        '  </relatedIdentifiers>\n'
        '  <sizes>\n'
        '    <size>11 pages</size>\n'
        '  </sizes>\n'
        '  <formats>\n'
        '    <format>application/pdf</format>\n'
        '  </formats>\n'
        '  <version>v1.0</version>\n'
        '  <rightsList>\n'
        '    <rights rightsURI="https://customlicense.org/licenses/by/4.0/">A custom license</rights>\n'  # noqa
        '    <rights rightsURI="https://creativecommons.org/licenses/by/4.0/legalcode" rightsIdentifierScheme="spdx" rightsIdentifier="cc-by-4.0">Creative Commons Attribution 4.0 International</rights>\n'  # noqa
        '  </rightsList>\n'
        '  <descriptions>\n'
        '    <description descriptionType="Abstract">A description \nwith HTML tags</description>\n'  # noqa
        '    <description descriptionType="Methods" xml:lang="eng">Bla bla bla</description>\n'  # noqa
        '  </descriptions>\n'
        '  <geoLocations>\n'
        '    <geoLocation>\n'
        '      <geoLocationPlace>test location place</geoLocationPlace>\n'
        '      <geoLocationPoint>\n'
        '        <pointLongitude>-60.63932</pointLongitude>\n'
        '        <pointLatitude>-32.94682</pointLatitude>\n'
        '      </geoLocationPoint>\n'
        '    </geoLocation>\n'
        '  </geoLocations>\n'
        '  <fundingReferences>\n'
        '    <fundingReference>\n'
        '      <funderName>European Commission</funderName>\n'
        '      <funderIdentifier funderIdentifierType="ROR">00k4n6c32</funderIdentifier>\n'  # noqa
        '      <awardNumber>755021</awardNumber>\n'
        '      <awardTitle>Personalised Treatment For Cystic Fibrosis Patients With Ultra-rare CFTR Mutations (and beyond)</awardTitle>\n'  # noqa
        '    </fundingReference>\n'
        '  </fundingReferences>\n'
        '</resource>\n'
    )

    record = {"_source": full_record}
    ser_rec = etree.tostring(
        datacite_etree(None, record),
        pretty_print=True
    )
    assert expected_value == ser_rec.decode("utf-8")


def test_oai_datacite_serializer(running_app, full_record):
    expected_value = (
        '<oai_datacite xmlns="http://schema.datacite.org/oai/oai-1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.datacite.org/oai/oai-1.1/ http://schema.datacite.org/oai/oai-1.1/oai.xsd">\n'  # noqa
        '  <schemaVersion>4.3</schemaVersion>\n'
        '  <datacentreSymbol>TEST</datacentreSymbol>\n'
        '  <payload>\n'
        '    <resource xmlns="http://datacite.org/schema/kernel-4" xsi:schemaLocation="http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.3/metadata.xsd">\n'  # noqa
        '      <identifier identifierType="DOI">10.5281/inveniordm.1234</identifier>\n'  # noqa
        '      <alternateIdentifiers>\n'
        '        <alternateIdentifier alternateIdentifierType="bibcode">1924MNRAS..84..308E</alternateIdentifier>\n'  # noqa
        '      </alternateIdentifiers>\n'
        '      <creators>\n'
        '        <creator>\n'
        '          <creatorName nameType="Personal">Nielsen, Lars Holm</creatorName>\n'  # noqa
        '          <givenName>Lars Holm</givenName>\n'
        '          <familyName>Nielsen</familyName>\n'
        '          <nameIdentifier nameIdentifierScheme="ORCID">0000-0001-8135-3489</nameIdentifier>\n'  # noqa
        '          <affiliation>free-text</affiliation>\n'
        '          <affiliation affiliationIdentifier="01ggx4157" affiliationIdentifierScheme="ROR">CERN</affiliation>\n'  # noqa
        '        </creator>\n'
        '      </creators>\n'
        '      <titles>\n'
        '        <title>InvenioRDM</title>\n'
        '        <title xml:lang="eng" titleType="Subtitle">a research data management platform</title>\n'  # noqa
        '      </titles>\n'
        '      <publisher>InvenioRDM</publisher>\n'
        '      <publicationYear>2018</publicationYear>\n'
        '      <subjects>\n'
        '        <subject>custom</subject>\n'
        '        <subject subjectScheme="MeSH">Abdominal Injuries</subject>\n'
        '      </subjects>\n'
        '      <contributors>\n'
        '        <contributor contributorType="Other">\n'
        '          <contributorName nameType="Personal">Nielsen, Lars Holm</contributorName>\n'  # noqa
        '          <givenName>Lars Holm</givenName>\n'
        '          <familyName>Nielsen</familyName>\n'
        '          <nameIdentifier nameIdentifierScheme="ORCID">0000-0001-8135-3489</nameIdentifier>\n'  # noqa
        '          <affiliation affiliationIdentifier="01ggx4157" affiliationIdentifierScheme="ROR">CERN</affiliation>\n'  # noqa
        '        </contributor>\n'
        '      </contributors>\n'
        '      <dates>\n'
        '        <date dateType="Issued">2018/2020-09</date>\n'
        '        <date dateType="Other" dateInformation="A date">1939/1945</date>\n'  # noqa
        '      </dates>\n'
        '      <language>dan</language>\n'
        '      <resourceType resourceTypeGeneral="Image">Photo</resourceType>\n'  # noqa
        '      <relatedIdentifiers>\n'
        '        <relatedIdentifier relatedIdentifierType="DOI" relationType="IsCitedBy" resourceTypeGeneral="Dataset">10.1234/foo.bar</relatedIdentifier>\n'  # noqa
        '      </relatedIdentifiers>\n'
        '      <sizes>\n'
        '        <size>11 pages</size>\n'
        '      </sizes>\n'
        '      <formats>\n'
        '        <format>application/pdf</format>\n'
        '      </formats>\n'
        '      <version>v1.0</version>\n'
        '      <rightsList>\n'
        '        <rights rightsURI="https://customlicense.org/licenses/by/4.0/">A custom license</rights>\n'  # noqa
        '        <rights rightsURI="https://creativecommons.org/licenses/by/4.0/legalcode" rightsIdentifierScheme="spdx" rightsIdentifier="cc-by-4.0">Creative Commons Attribution 4.0 International</rights>\n'  # noqa
        '      </rightsList>\n'
        '      <descriptions>\n'
        '        <description descriptionType="Abstract">A description \nwith HTML tags</description>\n'  # noqa
        '        <description descriptionType="Methods" xml:lang="eng">Bla bla bla</description>\n'  # noqa
        '      </descriptions>\n'
        '      <geoLocations>\n'
        '        <geoLocation>\n'
        '          <geoLocationPlace>test location place</geoLocationPlace>\n'
        '          <geoLocationPoint>\n'
        '            <pointLongitude>-60.63932</pointLongitude>\n'
        '            <pointLatitude>-32.94682</pointLatitude>\n'
        '          </geoLocationPoint>\n'
        '        </geoLocation>\n'
        '      </geoLocations>\n'
        '      <fundingReferences>\n'
        '        <fundingReference>\n'
        '          <funderName>European Commission</funderName>\n'
        '          <funderIdentifier funderIdentifierType="ROR">00k4n6c32</funderIdentifier>\n'  # noqa
        '          <awardNumber>755021</awardNumber>\n'
        '          <awardTitle>Personalised Treatment For Cystic Fibrosis Patients With Ultra-rare CFTR Mutations (and beyond)</awardTitle>\n'  # noqa
        '        </fundingReference>\n'
        '      </fundingReferences>\n'
        '    </resource>\n'
        '  </payload>\n'
        '</oai_datacite>\n'
    )
    record = {"_source": full_record}
    ser_rec = etree.tostring(
        oai_datacite_etree(None, record),
        pretty_print=True
    )
    assert expected_value == ser_rec.decode("utf-8")
