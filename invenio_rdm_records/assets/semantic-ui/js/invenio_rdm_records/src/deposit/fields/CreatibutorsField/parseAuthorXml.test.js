/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { parseAuthorXml } from "./parseAuthorXml";

// The fixtures follow the examples published in
// https://github.com/inspirehep/author.xml/tree/main/example-files
const MINIMAL_EXAMPLE = `<?xml version="1.0" encoding="UTF-8"?>
<collaborationauthorlist
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/"
>
  <cal:organizations>
    <foaf:Organization id="a1">
      <cal:orgDomain>http://yerphi.am</cal:orgDomain>
      <foaf:name>Yerevan Phys. Inst.</foaf:name>
      <cal:orgName source="INSPIRE">Yerevan Phys. Inst.</cal:orgName>
      <cal:orgName source="ROR">https://ror.org/00ad27c73</cal:orgName>
    </foaf:Organization>
    <foaf:Organization id="a109">
      <foaf:name>CERN</foaf:name>
      <cal:orgName source="ROR">https://ror.org/01ggx4157</cal:orgName>
    </foaf:Organization>
  </cal:organizations>
  <cal:authors>
    <foaf:Person>
      <foaf:name>Vardan Khachatryan</foaf:name>
      <foaf:givenName>Vardan</foaf:givenName>
      <foaf:familyName>Khachatryan</foaf:familyName>
      <cal:authorNamePaper>V. Khachatryan</cal:authorNamePaper>
      <cal:authorNamePaperGiven>V.</cal:authorNamePaperGiven>
      <cal:authorNamePaperFamily>Khachatryan</cal:authorNamePaperFamily>
      <cal:authorAffiliations>
        <cal:authorAffiliation organizationid="a1"/>
      </cal:authorAffiliations>
      <cal:authorids>
        <cal:authorid source="ORCID">https://orcid.org/0000-0002-1825-0097</cal:authorid>
        <cal:authorid source="INSPIRE">INSPIRE-00314584</cal:authorid>
      </cal:authorids>
    </foaf:Person>
    <foaf:Person>
      <foaf:name>Benjamin C. Shen</foaf:name>
      <foaf:givenName>Benjamin C.</foaf:givenName>
      <foaf:familyName>Shen</foaf:familyName>
      <cal:authorStatus>Deceased</cal:authorStatus>
      <cal:authorNamePaper>B.C. Shen</cal:authorNamePaper>
      <cal:authorAffiliations>
        <cal:authorAffiliation organizationid="a109"/>
      </cal:authorAffiliations>
    </foaf:Person>
  </cal:authors>
</collaborationauthorlist>`;

const MULTICOLLABORATION_EXAMPLE = `<?xml version="1.0" encoding="UTF-8"?>
<collaborationauthorlist
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/"
>
  <cal:organizations>
    <foaf:Organization id="a59a">
      <cal:orgDomain>http://www.infn.it/</cal:orgDomain>
      <foaf:name>INFN, Florence</foaf:name>
      <cal:orgName source="INSPIRE">INFN, Florence</cal:orgName>
      <cal:orgName source="ROR">https://ror.org/04wgrhj04</cal:orgName>
    </foaf:Organization>
    <foaf:Organization id="a59b">
      <cal:orgDomain>http://www.unifi.it/</cal:orgDomain>
      <foaf:name>Florence U.</foaf:name>
      <cal:orgName source="ROR">https://ror.org/00m9ns448</cal:orgName>
    </foaf:Organization>
    <foaf:Organization id="a139">
      <cal:orgDomain>http://www.fnal.gov/</cal:orgDomain>
      <foaf:name>Fermilab</foaf:name>
      <cal:orgName source="ROR">https://ror.org/020h68657</cal:orgName>
    </foaf:Organization>
  </cal:organizations>
  <cal:authors>
    <foaf:Person>
      <foaf:name>Marcello Abbrescia</foaf:name>
      <foaf:givenName>Marcello</foaf:givenName>
      <foaf:familyName>Abbrescia</foaf:familyName>
      <cal:authorNamePaper>M. Abbrescia</cal:authorNamePaper>
      <cal:authorAffiliations>
        <cal:authorAffiliation organizationid="a59a"/>
        <cal:authorAffiliation organizationid="a59b"/>
        <cal:authorAffiliation organizationid="a139" connection="Also at"/>
      </cal:authorAffiliations>
      <cal:authorids>
        <cal:authorid source="INSPIRE">INSPIRE-00125803</cal:authorid>
      </cal:authorids>
    </foaf:Person>
  </cal:authors>
</collaborationauthorlist>`;

const wrapAuthors = (authors) => `<?xml version="1.0" encoding="UTF-8"?>
<collaborationauthorlist
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/"
>
  <cal:authors>
    ${authors}
  </cal:authors>
</collaborationauthorlist>`;

describe("parseAuthorXml", () => {
  it("parses the example minimal author list", () => {
    expect(parseAuthorXml(MINIMAL_EXAMPLE)).toEqual([
      {
        person_or_org: {
          type: "personal",
          given_name: "Vardan",
          family_name: "Khachatryan",
          identifiers: [{ scheme: "orcid", identifier: "0000-0002-1825-0097" }],
        },
        affiliations: [{ id: "00ad27c73", name: "Yerevan Phys. Inst." }],
      },
      {
        person_or_org: {
          type: "personal",
          given_name: "Benjamin C.",
          family_name: "Shen",
        },
        affiliations: [{ id: "01ggx4157", name: "CERN" }],
      },
    ]);
  });

  it("resolves every affiliation of an author in a multicollaboration list", () => {
    const [entry] = parseAuthorXml(MULTICOLLABORATION_EXAMPLE);

    expect(entry.affiliations).toEqual([
      { id: "04wgrhj04", name: "INFN, Florence" },
      { id: "00m9ns448", name: "Florence U." },
      { id: "020h68657", name: "Fermilab" },
    ]);
    // The only identifier is an INSPIRE one, which has no scheme in InvenioRDM.
    expect(entry.person_or_org).toEqual({
      type: "personal",
      given_name: "Marcello",
      family_name: "Abbrescia",
    });
  });

  it("imports the identifier schemes InvenioRDM knows, in any casing", () => {
    const [entry] = parseAuthorXml(
      wrapAuthors(`<foaf:Person>
        <foaf:givenName>Jane</foaf:givenName>
        <foaf:familyName>Smith</foaf:familyName>
        <cal:authorids>
          <cal:authorid source="ORCID">0000-0002-1825-0097</cal:authorid>
          <cal:authorid source="orcid">0000-0002-1825-0097</cal:authorid>
          <cal:authorid source="Gnd">https://d-nb.info/gnd/118757989</cal:authorid>
          <cal:authorid source="ISNI">0000 0001 2141 8603</cal:authorid>
          <cal:authorid source="ROR">ror:04wx9ry42</cal:authorid>
          <cal:authorid source="INSPIRE">INSPIRE-00314584</cal:authorid>
          <cal:authorid source="INTERNAL">123456</cal:authorid>
        </cal:authorids>
      </foaf:Person>`)
    );

    expect(entry.person_or_org.identifiers).toEqual([
      { scheme: "orcid", identifier: "0000-0002-1825-0097" },
      { scheme: "gnd", identifier: "118757989" },
      { scheme: "isni", identifier: "0000 0001 2141 8603" },
      { scheme: "ror", identifier: "04wx9ry42" },
    ]);
  });

  it("falls back to the free-text name when the structured name is missing", () => {
    const [entry] = parseAuthorXml(
      wrapAuthors(`<foaf:Person>
        <foaf:name>Vardan Khachatryan</foaf:name>
        <cal:authorNamePaper>V. Khachatryan</cal:authorNamePaper>
      </foaf:Person>`)
    );

    expect(entry.person_or_org).toEqual({
      type: "personal",
      given_name: "Vardan",
      family_name: "Khachatryan",
    });
    expect(entry.affiliations).toBeUndefined();
  });

  it("falls back to the paper name when the free-text name is missing", () => {
    const [entry] = parseAuthorXml(
      wrapAuthors(`<foaf:Person>
        <cal:authorNamePaper>G.F. Donald</cal:authorNamePaper>
      </foaf:Person>`)
    );

    expect(entry.person_or_org).toEqual({
      type: "personal",
      given_name: "G.F.",
      family_name: "Donald",
    });
  });

  it("prefers the explicit paper family name over splitting free text", () => {
    const [entry] = parseAuthorXml(
      wrapAuthors(`<foaf:Person>
        <foaf:name>Johannes Diderik van der Waals</foaf:name>
        <foaf:givenName>Johannes Diderik</foaf:givenName>
        <cal:authorNamePaper>J.D. van der Waals</cal:authorNamePaper>
        <cal:authorNamePaperFamily>van der Waals</cal:authorNamePaperFamily>
      </foaf:Person>`)
    );

    expect(entry.person_or_org).toMatchObject({
      given_name: "Johannes Diderik",
      family_name: "van der Waals",
    });
  });

  it("ignores organizations that no author refers to", () => {
    expect(
      parseAuthorXml(`<?xml version="1.0" encoding="UTF-8"?>
        <collaborationauthorlist
          xmlns:foaf="http://xmlns.com/foaf/0.1/"
          xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/"
        >
          <cal:organizations>
            <foaf:Organization id="a1">
              <foaf:name>CERN</foaf:name>
            </foaf:Organization>
          </cal:organizations>
          <cal:authors>
            <foaf:Person>
              <foaf:givenName>Jane</foaf:givenName>
              <foaf:familyName>Smith</foaf:familyName>
            </foaf:Person>
          </cal:authors>
        </collaborationauthorlist>`)
    ).toEqual([
      {
        person_or_org: {
          type: "personal",
          given_name: "Jane",
          family_name: "Smith",
        },
      },
    ]);
  });

  it("does not take an organization name from cal:orgName", () => {
    const [entry] = parseAuthorXml(`<?xml version="1.0" encoding="UTF-8"?>
      <collaborationauthorlist
        xmlns:foaf="http://xmlns.com/foaf/0.1/"
        xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/"
      >
        <cal:organizations>
          <foaf:Organization id="a1">
            <cal:orgName source="ROR">https://ror.org/01ggx4157</cal:orgName>
            <cal:orgName source="InstId">808</cal:orgName>
          </foaf:Organization>
          <foaf:Organization id="a2">
            <cal:orgName source="InstId">809</cal:orgName>
          </foaf:Organization>
        </cal:organizations>
        <cal:authors>
          <foaf:Person>
            <foaf:givenName>Jane</foaf:givenName>
            <foaf:familyName>Smith</foaf:familyName>
            <cal:authorAffiliations>
              <cal:authorAffiliation organizationid="a1"/>
              <cal:authorAffiliation organizationid="a2"/>
            </cal:authorAffiliations>
          </foaf:Person>
        </cal:authors>
      </collaborationauthorlist>`);

    // The ROR becomes the identifier; neither the ROR URL nor the internal
    // institution id is stored as an affiliation name.
    expect(entry.affiliations).toEqual([{ id: "01ggx4157" }]);
  });

  it("returns an empty array for an author list without authors", () => {
    expect(parseAuthorXml(wrapAuthors(""))).toEqual([]);
  });

  it("returns null when the XML is not an author list", () => {
    expect(
      parseAuthorXml(`<authorml xmlns="http://inspirehep.net/ns/authorml">
        <authors>
          <author><givenName>Jane</givenName><familyName>Smith</familyName></author>
        </authors>
      </authorml>`)
    ).toBeNull();
    expect(parseAuthorXml("<html><body>Smith, Jane</body></html>")).toBeNull();
  });

  it("returns null when the XML cannot be parsed", () => {
    expect(parseAuthorXml("<collaborationauthorlist><cal:authors>")).toBeNull();
    expect(parseAuthorXml("Smith, Jane")).toBeNull();
    expect(parseAuthorXml("")).toBeNull();
    expect(parseAuthorXml(null)).toBeNull();
  });
});
