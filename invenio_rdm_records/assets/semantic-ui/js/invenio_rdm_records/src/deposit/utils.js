/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

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
