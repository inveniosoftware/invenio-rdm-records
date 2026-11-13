/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER } from "../constants";

const JSON_IMPORT_EXAMPLE = `[
  {
    "person_or_org": {
      "type": "personal",
      "family_name": "Smith",
      "given_name": "Jane",
      "identifiers": [{ "scheme": "orcid", "identifier": "0000-0002-1825-0097" }]
    },
    "affiliations": [{ "name": "CERN" }]
  },
  {
    "person_or_org": {
      "type": "organizational",
      "name": "European Organization for Nuclear Research"
    }
  }
]`;

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
  return parsed;
};

/**
 * The built-in format: a JSON array of creatibutor objects, as accepted by the
 * deposit form.
 *
 * Its order is `DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER`, the default for formats
 * that do not set one: register a format with a lower order to offer it before
 * JSON, a higher one to offer it after.
 */
export const jsonFileFormat = {
  id: "json",
  label: i18next.t("JSON"),
  extension: ".json",
  order: DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER,
  example: JSON_IMPORT_EXAMPLE,
  parse: parseJson,
};
