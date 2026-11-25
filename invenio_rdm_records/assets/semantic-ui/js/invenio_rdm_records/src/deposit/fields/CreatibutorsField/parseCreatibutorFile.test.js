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

  it("normalizes exported role objects and preserves other role values", () => {
    const entries = [
      { role: { id: "editor", title: { en: "Editor" } } },
      { role: "hostinginstitution" },
      { role: { title: { en: "Editor" } } },
      { role: { id: 123 } },
      { role: null },
      { name: "No role" },
    ];

    expect(
      parseCreatibutorFile(JSON.stringify(entries), "contributors.json", formats)
    ).toEqual({
      entries: [
        { role: "editor" },
        { role: "hostinginstitution" },
        { role: { title: { en: "Editor" } } },
        { role: { id: 123 } },
        { role: null },
        { name: "No role" },
      ],
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
