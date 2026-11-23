/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

/**
 * Kinds of error `parseCreatibutorFile` reports.
 */
export const CREATIBUTOR_FILE_ERROR = Object.freeze({
  /** No registered format handles the file's extension. */
  UNSUPPORTED: "unsupported",
  /** The matching format could not parse the file's content. */
  INVALID: "invalid",
});

/**
 * Find the format that handles a file name. Registered extensions are already
 * lower-cased. The longest match wins, so `.tar.gz` is preferred over `.gz`.
 */
const findFormat = (fileName, formats) => {
  const name = fileName.toLowerCase();
  return formats
    .filter((format) => name.endsWith(format.extension))
    .reduce(
      (best, format) =>
        !best || format.extension.length > best.extension.length ? format : best,
      undefined
    );
};

/**
 * Parse a creatibutor file using the format associated with its file extension.
 *
 * @param {string} text - raw content of the uploaded file
 * @param {string} fileName - uploaded filename, used to select the format
 * @param {Array<object>} formats - registered formats whose parsers may be used
 * @returns {{entries: Array|null, error: {type: string, format?: string}|null}} parsed entries or an error
 */
export const parseCreatibutorFile = (text, fileName, formats) => {
  if (!Array.isArray(formats)) {
    throw new TypeError(
      "parseCreatibutorFile requires the accepted formats as its third argument."
    );
  }

  const unsupported = {
    entries: null,
    error: { type: CREATIBUTOR_FILE_ERROR.UNSUPPORTED },
  };
  if (typeof text !== "string" || typeof fileName !== "string") return unsupported;

  const format = findFormat(fileName, formats);
  if (!format) return unsupported;

  const invalid = {
    entries: null,
    error: { type: CREATIBUTOR_FILE_ERROR.INVALID, format: format.label },
  };
  // Excel and some editors save files with a byte order mark.
  const content = text.replace(/^\uFEFF/, "");
  try {
    const entries = format.parse(content);
    return Array.isArray(entries) ? { entries, error: null } : invalid;
  } catch {
    return invalid;
  }
};
