// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

/**
 * Enumeration of possible supported Uppy dashboard events.
 * @constant {Object}
 * @property {string} UPLOAD_FILE_WITHOUT_EDIT - Event triggered for auto-uploading without explicit editing user interaction.
 */
export const UPPY_EVENTS = {
  UPLOAD_FILE_WITHOUT_EDIT: "upload-file-without-edit",
};

/**
 * Computes conditional UI properties for the Uppy Dashboard based on the active event state.
 *
 * @param {Object} startEvent - The currently active event, if any (e.g. { event: UPPY_EVENTS.EDIT_FILE }).
 * @returns {Object} A dictionary of props specifically mapped to the `<Dashboard />` component dynamically.
 */
export const getUppyDashboardEventsProps = (startEvent) => {
  return {
    showSelectedFiles: startEvent.event === UPPY_EVENTS.UPLOAD_FILE_WITHOUT_EDIT ? false : true,
  };
};
