/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";

export { jsonFileFormat } from "./json";

/**
 * Prop type of a creatibutor file format descriptor.
 *
 * The dialog receives the formats as a `fileFormats` prop. Instances override
 * that prop with `parametrize`.
 */
export const creatibutorFileFormatPropType = PropTypes.shape({
  /** Unique identifier of the format, e.g. `"json"`. */
  id: PropTypes.string.isRequired,
  /** Name shown in the dialog, e.g. `"JSON"`. */
  label: PropTypes.string.isRequired,
  /** File extension of the format, e.g. `".json"`. */
  extension: PropTypes.string.isRequired,
  /** Example content shown in the dialog. */
  example: PropTypes.string,
  /** Note shown under the example. */
  note: PropTypes.string,
  /** Parse the content into creatibutors, or `null` when it is not valid. */
  parse: PropTypes.func.isRequired,
});
