/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

const JSON_IMPORT_EXAMPLE = `[
  {
    "person_or_org": {
      "type": "personal",
      "family_name": "Smith",
      "given_name": "Jane",
      "identifiers": [{ "scheme": "orcid", "identifier": "0000-0002-1825-0097" }]
    },
    "affiliations": [{ "name": "CERN" }],
    "role": "editor"
  },
  {
    "person_or_org": {
      "type": "organizational",
      "name": "European Organization for Nuclear Research"
    }
  }
]`;

const normalizeRole = (entry) => {
  const { role } = entry;
  if (!role || typeof role !== "object" || typeof role.id !== "string") {
    return entry;
  }

  return { ...entry, role: role.id };
};

/**
 * Parse a raw file text as a JSON array of plain objects.
 * Returns the parsed array when the data formatting is valid,
 * or `null` when the data cannot be interpreted in the expected format.
 */
const parseJson = (text) => {
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    return null;
  }
  if (!Array.isArray(parsed)) {
    return null;
  }
  for (const entry of parsed) {
    if (typeof entry !== "object" || entry === null || Array.isArray(entry)) {
      return null;
    }
  }
  return parsed.map(normalizeRole);
};

/**
 * JSON Format for creatibutors import.
 */
export const jsonFileFormat = {
  id: "json",
  label: "JSON",
  extension: ".json",
  example: JSON_IMPORT_EXAMPLE,
  parse: parseJson,
};
