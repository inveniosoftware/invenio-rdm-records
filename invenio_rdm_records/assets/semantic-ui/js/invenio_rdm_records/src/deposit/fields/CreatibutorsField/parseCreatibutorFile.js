/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { parseAuthorXml } from "./parseAuthorXml";

const FILE_FORMAT = {
  JSON: "json",
  AUTHOR_XML: "author_xml",
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
  return parsed;
};

const detectFormat = (text) => {
  const content = text.trimStart();
  if (content.startsWith("<")) return FILE_FORMAT.AUTHOR_XML;
  if (content.startsWith("[") || content.startsWith("{")) return FILE_FORMAT.JSON;
  return null;
};

/**
 * Parse a creatibutor file into an array of creatibutor objects.
 *
 * Supported formats are a JSON array of creatibutors and author list XML (`author.xml`).
 *
 * @param {string} text - raw content of the uploaded file
 * @returns {Array|null} the parsed entries, or `null` when the content is not
 *   in a supported format
 */
export const parseCreatibutorFile = (text) => {
  if (typeof text !== "string") return null;
  // Excel and some editors save files with a byte order mark.
  const content = text.replace(/^\uFEFF/, "");

  switch (detectFormat(content)) {
    case FILE_FORMAT.JSON:
      return parseJson(content);
    case FILE_FORMAT.AUTHOR_XML:
      return parseAuthorXml(content);
    default:
      return null;
  }
};
