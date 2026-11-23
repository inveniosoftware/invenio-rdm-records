/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER } from "./constants";
import { jsonFileFormat } from "./json";

export { DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER };

/**
 * Prop type of a creatibutor file format descriptor.
 */
export const creatibutorFileFormatPropType = PropTypes.shape({
  /** Unique identifier of the format, e.g. `"json"`. */
  id: PropTypes.string.isRequired,
  /**
   * Name shown in the dialog, e.g. `"JSON"`. Pass it already translated
   * (`i18next.t("JSON")`): the dialog shows it as given.
   */
  label: PropTypes.string.isRequired,
  /** File extension of the format, e.g. `".json"` or `"json"`. */
  extension: PropTypes.string.isRequired,
  /**
   * Position of the format in the dialog. Lower values are offered first and
   * the default is `100`, which is the order of the built-in JSON format.
   */
  order: PropTypes.number,
  /** Example content shown in the dialog. */
  example: PropTypes.string,
  /** Note shown under the example, already translated like `label`. */
  note: PropTypes.string,
  /** Parse the content into creatibutors, or `null` when it is not valid. */
  parse: PropTypes.func.isRequired,
});

const normalizeExtension = (extension) => {
  const normalized = extension.trim().toLowerCase();
  return normalized.startsWith(".") ? normalized : `.${normalized}`;
};

const isNonEmptyString = (value) => typeof value === "string" && value.trim() !== "";

const assertFileFormat = (fileFormat) => {
  const invalid = [];
  if (!isNonEmptyString(fileFormat?.id)) invalid.push("id");
  if (!isNonEmptyString(fileFormat?.label)) invalid.push("label");
  if (!isNonEmptyString(fileFormat?.extension)) invalid.push("extension");
  if (typeof fileFormat?.parse !== "function") invalid.push("parse function");
  if (invalid.length > 0) {
    throw new TypeError(
      "A creatibutor file format requires a non-empty id, label, extension and " +
        `a parse function. Missing or invalid: ${invalid.join(", ")}.`
    );
  }

  if (fileFormat.order !== undefined && !Number.isFinite(fileFormat.order)) {
    throw new TypeError(
      `The order of the creatibutor file format "${fileFormat.id}" must be a finite number.`
    );
  }
};

/**
 * Create a creatibutor file format registry.
 *
 * @returns {object} file format registry
 */
export const createCreatibutorFileFormatRegistry = () => {
  const registered = [];
  let sequence = 0;

  const indexOfId = (id) => registered.findIndex(({ format }) => format.id === id);

  /**
   * Register a format. Duplicate ids and extensions are rejected; unregister
   * the existing format explicitly before registering a replacement.
   *
   * @param {object} fileFormat - format descriptor, see the prop type above
   * @returns {object} the registered, normalized format
   */
  const register = (fileFormat) => {
    assertFileFormat(fileFormat);

    const existingId = registered.find(({ format }) => format.id === fileFormat.id);
    if (existingId) {
      throw new Error(
        `Cannot register the creatibutor file format "${fileFormat.id}": a format with this id is already registered. Unregister it before registering another format with the same id.`
      );
    }

    const extension = normalizeExtension(fileFormat.extension);
    const conflict = registered.find(({ format }) => format.extension === extension);
    if (conflict) {
      throw new Error(
        `Cannot register the creatibutor file format "${fileFormat.id}": the ` +
          `extension "${extension}" is already used by "${conflict.format.id}". ` +
          `Unregister the format "${conflict.format.id}" before registering this format.`
      );
    }

    const format = Object.freeze({
      order: DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER,
      ...fileFormat,
      extension,
    });
    registered.push({ sequence: sequence++, format });
    return format;
  };

  /**
   * Remove a registered format.
   *
   * @param {string} id - id of the format to remove
   * @returns {object} the removed format
   */
  const unregister = (id) => {
    const index = indexOfId(id);
    if (index === -1) {
      throw new Error(`No creatibutor file format is registered with the id "${id}".`);
    }
    return registered.splice(index, 1)[0].format;
  };

  /**
   * Snapshot of the registered formats, ordered by their `order` property ascending.
   *
   * @returns {Array<object>} registered formats, sorted by `order`
   */
  const getFormats = () =>
    registered
      .slice()
      .sort((a, b) => a.format.order - b.format.order || a.sequence - b.sequence)
      .map(({ format }) => format);

  return Object.freeze({ register, unregister, getFormats });
};

const fileFormatRegistry = createCreatibutorFileFormatRegistry();

/**
 * Register a format in the "add authors/contributors from file" dialog.
 *
 * @param {object} fileFormat - format descriptor, see the prop type above
 * @returns {object} the registered format
 */
export const registerCreatibutorFileFormat = (fileFormat) =>
  fileFormatRegistry.register(fileFormat);

/**
 * Remove a format from the "add authors/contributors from file" dialog.
 *
 * @param {string} id - id of the format to remove
 * @returns {object} the removed format
 */
export const unregisterCreatibutorFileFormat = (id) =>
  fileFormatRegistry.unregister(id);

/**
 * Return the registered creatibutor file formats, in the order they are offered.
 *
 * @returns {Array<object>} registered format descriptors
 */
export const getCreatibutorFileFormats = () => fileFormatRegistry.getFormats();

// Register the built-in JSON format.
registerCreatibutorFileFormat(jsonFileFormat);
