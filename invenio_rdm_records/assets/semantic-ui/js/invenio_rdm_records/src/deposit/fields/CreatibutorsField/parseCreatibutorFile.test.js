/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { jsonFileFormat } from "./fileFormats/json";
import { parseCreatibutorFile } from "./parseCreatibutorFile";

const JSON_FILE = `[
  {
    "person_or_org": { "type": "personal", "family_name": "Smith" }
  },
  {
    "person_or_org": { "type": "organizational", "name": "CERN" }
  }
]`;

const CUSTOM_FILE = `Smith, Jane`;

const customFormat = {
  id: "custom",
  label: "Custom",
  extension: ".custom",
  parse: (text) => [
    { person_or_org: { type: "personal", given_name: "Jane", family_name: "Smith" } },
  ],
};

// The parser never reads the registry, so this suite cannot affect other suites.
const formats = [jsonFileFormat, customFormat];

describe("parseCreatibutorFile", () => {
  it("parses JSON using the filename extension", () => {
    expect(parseCreatibutorFile(JSON_FILE, "authors.json", formats)).toEqual({
      entries: JSON.parse(JSON_FILE),
      error: null,
    });
  });

  it("matches extensions case-insensitively and parses a BOM", () => {
    expect(
      parseCreatibutorFile(`\uFEFF\n  ${JSON_FILE}`, "AUTHORS.JSON", formats).entries
    ).toHaveLength(2);
  });

  it("parses a file in a supplied format", () => {
    expect(parseCreatibutorFile(CUSTOM_FILE, "authors.custom", formats)).toEqual({
      entries: [
        {
          person_or_org: { type: "personal", given_name: "Jane", family_name: "Smith" },
        },
      ],
      error: null,
    });
  });

  it("matches multi-part extensions, preferring the longest", () => {
    const entries = (id) => () =>
      [{ person_or_org: { type: "personal", family_name: id } }];
    const multi = [
      { ...customFormat, id: "gz", extension: ".gz", parse: entries("gz") },
      { ...customFormat, id: "tgz", extension: ".tar.gz", parse: entries("tar.gz") },
    ];

    expect(
      parseCreatibutorFile("x", "Authors.TAR.GZ", multi).entries[0].person_or_org
        .family_name
    ).toBe("tar.gz");
    expect(
      parseCreatibutorFile("x", "authors.gz", multi).entries[0].person_or_org
        .family_name
    ).toBe("gz");
  });

  it("returns an unsupported error for an unrecognized extension", () => {
    expect(parseCreatibutorFile(CUSTOM_FILE, "authors.xml", formats)).toEqual({
      entries: null,
      error: { type: "unsupported" },
    });
  });

  it("returns an unsupported error when the accepted list is empty", () => {
    expect(parseCreatibutorFile(CUSTOM_FILE, "authors.custom", [])).toEqual({
      entries: null,
      error: { type: "unsupported" },
    });
  });

  it("reports the selected format when its parser rejects the contents", () => {
    expect(parseCreatibutorFile("not JSON", "authors.json", formats)).toEqual({
      entries: null,
      error: { type: "invalid", format: "JSON" },
    });
    expect(parseCreatibutorFile('["a string"]', "authors.json", formats)).toEqual({
      entries: null,
      error: { type: "invalid", format: "JSON" },
    });
  });

  it("accepts an empty array and rejects non-string content", () => {
    expect(parseCreatibutorFile("[]", "authors.json", formats)).toEqual({
      entries: [],
      error: null,
    });
    expect(parseCreatibutorFile(null, "authors.json", formats)).toEqual({
      entries: null,
      error: { type: "unsupported" },
    });
  });

  it("requires the accepted formats", () => {
    expect(() => parseCreatibutorFile(CUSTOM_FILE, "authors.custom")).toThrow(
      /requires the accepted formats as its third argument/
    );
  });
});
