// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { i18next } from "@translations/invenio_rdm_records/i18next";

/**
 * Enumeration of possible supported Uppy dashboard events.
 * @constant {Object}
 * @property {string} EDIT_FILE - Event triggered when a single file is requested for metadata editing.
 * @property {string} UPLOAD_FILE_WITHOUT_EDIT - Event triggered for auto-uploading without explicit editing user interaction.
 */
export const UPPY_EVENTS = {
  EDIT_FILE: "edit-file",
  UPLOAD_FILE_WITHOUT_EDIT: "upload-file-without-edit",
};

/**
 * Computes conditional UI properties for the Uppy Dashboard based on the active event state.
 *
 * @param {Object} startEvent - The currently active event, if any (e.g. { event: UPPY_EVENTS.EDIT_FILE }).
 * @returns {Object} A dictionary of props specifically mapped to the `<Dashboard />` component dynamically.
 */
export const getUppyDashboardEventsProps = (startEvent) => {
  const isEditEvent = startEvent?.event === UPPY_EVENTS.EDIT_FILE;

  return {
    autoOpen: isEditEvent ? "metaEditor" : null,
    hideUploadButton: isEditEvent ? true : false,
    disableLocalFiles: isEditEvent ? true : false,
    showSelectedFiles: startEvent.event === UPPY_EVENTS.UPLOAD_FILE_WITHOUT_EDIT ? false : true,
    hideCancelButton: isEditEvent ? true : false,
    ...(isEditEvent && { note: i18next.t("Select existing files to modify metadata.") }),
  };
};

/**
 * React hook that binds a custom listener bridging Uppy UI's internal 'save changes' button
 * (in the meta editor panel) to automatically trigger file upload when the `EDIT_FILE` event is active.
 *
 * @param {Object} uppy - The active Uppy instance.
 * @param {Object} startEvent - The active Uppy start event specifying current user interaction mode.
 */
export const useUppyFileEditSaveSync = (uppy, startEvent) => {
  React.useEffect(() => {
    if (!uppy || !startEvent || startEvent.event !== UPPY_EVENTS.EDIT_FILE) return;

    uppy.on("dashboard:file-edit-start", async (file) => {
      // inline delay and DOM check helper
      const waitForElement = (selector) => {
        return new Promise((resolve) => {
          if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
          }
          const observer = new MutationObserver((mutations) => {
            if (document.querySelector(selector)) {
              observer.disconnect();
              resolve(document.querySelector(selector));
            }
          });
          observer.observe(document.body, { childList: true, subtree: true });
        });
      };

      const saveChangesButton = await waitForElement(
        ".uppy-Dashboard-FileCard-actions > button[type=submit]"
      );
      const uploadCallback = async () => {
        await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for the Uppy file.meta state to update
        uppy.upload();
      };
      saveChangesButton.addEventListener("click", uploadCallback);
      uppy.on("complete", (result) => {
        saveChangesButton.removeEventListener("click", uploadCallback);
      });
    });
  }, [uppy, startEvent]);
};
