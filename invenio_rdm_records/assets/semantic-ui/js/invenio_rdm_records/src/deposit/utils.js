// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { set } from "lodash";

/**
 * Traverse the leaves (non-Object, non-Array values) of obj and execute func
 * on each.
 *
 * @param {object} obj - generic Object
 * @param {function} func - (leaf) => ... (identity by default)
 *
 */
export function leafTraverse(obj, func = (l) => l) {
  if (typeof obj === "object") {
    // Objects and Arrays
    for (const key in obj) {
      leafTraverse(obj[key], func);
    }
  } else {
    func(obj);
  }
}

/**
 * Sort a list of string values (options).
 * @param {list} options
 * @returns
 */
export function sortOptions(options) {
  return options.sort((o1, o2) => o1.text.localeCompare(o2.text));
}

/**
 * Scroll page to top
 */
export function scrollTop() {
  window.scrollTo({
    top: 0,
    left: 0,
    behavior: "smooth",
  });
}

/**
 * Converts a flat array of error objects into a nested structure.
 * @param {Array} flatErrors - Array of error objects with a `field` path.
 * @returns {Object} Nested error object or undefined if input is invalid.
 */
export function nestErrors(flatErrors) {
  if (!Array.isArray(flatErrors) || flatErrors.length === 0) return undefined;

  const nestedErrors = {};

  for (const { field, messages, severity, description } of flatErrors) {
    if (!field || !Array.isArray(messages) || messages.length === 0) continue;

    set(nestedErrors, field, {
      message: messages.join(" "),
      severity,
      description,
    });
  }

  return Object.keys(nestedErrors).length ? nestedErrors : undefined;
}
