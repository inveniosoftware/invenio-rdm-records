/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

/**
 * Order of the built-in JSON format, used by every format that does not set an
 * `order` of its own. Use a lower value to offer a format before JSON and a
 * higher one to offer it after; formats with the same order keep their
 * registration order.
 */
export const DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER = 100;
