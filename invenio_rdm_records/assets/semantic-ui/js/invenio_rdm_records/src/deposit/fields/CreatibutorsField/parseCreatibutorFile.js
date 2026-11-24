/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

/**
 * Parse a creatibutor file using the format associated with its file extension.
 *
 * @param {string} text - raw content of the uploaded file
 * @param {string} fileName - uploaded filename, used to select the format
 * @param {Array<object>} formats - formats whose parsers may be used.
 * @returns {{entries: Array|null, error: {type: string, format?: string}|null}} parsed entries or an error
 */
export const parseCreatibutorFile = (text, fileName, formats) => {
  if (!Array.isArray(formats)) {
    throw new TypeError(
      "parseCreatibutorFile requires the accepted formats as its third argument."
    );
  }

  if (typeof text !== "string" || typeof fileName !== "string") {
    return { entries: null, error: { type: "unsupported" } };
  }

  const extension = fileName.match(/(\.[^.]+)$/)?.[1]?.toLowerCase();
  const format = formats.find(
    (candidate) => candidate.extension.toLowerCase() === extension
  );
  if (!format) return { entries: null, error: { type: "unsupported" } };

  // Excel and some editors save files with a byte order mark.
  const content = text.replace(/^\uFEFF/, "");
  try {
    const entries = format.parse(content);
    return Array.isArray(entries)
      ? { entries, error: null }
      : { entries: null, error: { type: "invalid", format: format.label } };
  } catch {
    return { entries: null, error: { type: "invalid", format: format.label } };
  }
};
