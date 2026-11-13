/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { parseCreatibutorFile } from "./parseCreatibutorFile";

const JSON_FILE = `[
  {
    "person_or_org": { "type": "personal", "family_name": "Smith" }
  },
  {
    "person_or_org": { "type": "organizational", "name": "CERN" }
  }
]`;

const AUTHOR_XML_FILE = `<collaborationauthorlist
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/">
  <cal:authors>
    <foaf:Person>
      <foaf:givenName>Jane</foaf:givenName>
      <foaf:familyName>Smith</foaf:familyName>
    </foaf:Person>
  </cal:authors>
</collaborationauthorlist>`;

describe("parseCreatibutorFile", () => {
  it("parses a JSON array of creatibutors", () => {
    expect(parseCreatibutorFile(JSON_FILE)).toEqual(JSON.parse(JSON_FILE));
  });

  it("parses an author.xml author list", () => {
    expect(parseCreatibutorFile(AUTHOR_XML_FILE)).toEqual([
      {
        person_or_org: {
          type: "personal",
          given_name: "Jane",
          family_name: "Smith",
        },
      },
    ]);
  });

  it("detects the format regardless of leading whitespace and BOM", () => {
    expect(parseCreatibutorFile(`\uFEFF\n  ${JSON_FILE}`)).toHaveLength(2);
    expect(parseCreatibutorFile(`\uFEFF  ${AUTHOR_XML_FILE}`)).toHaveLength(1);
  });

  it("returns null for invalid JSON", () => {
    expect(parseCreatibutorFile('{ "person_or_org": {} }')).toBeNull();
    expect(parseCreatibutorFile("not a file")).toBeNull();
    expect(parseCreatibutorFile('["a string"]')).toBeNull();
    expect(parseCreatibutorFile("[]")).toEqual([]);
  });

  it("returns null for unsupported files", () => {
    expect(parseCreatibutorFile("Smith, Jane\nDoe, John")).toBeNull();
    expect(parseCreatibutorFile(null)).toBeNull();
  });
});
