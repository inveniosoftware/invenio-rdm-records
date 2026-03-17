// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";

/**
 * Default allowed metadata fields configuration.
 */
export const defaultAllowedMetaFields = [
  { 
    id: "caption", 
    defaultValue: "", 
    isUserInput: true,
    condition: (file) => file.type && file.type.startsWith("image/") 
  },
  { 
    id: "featured", 
    defaultValue: false, 
    isUserInput: true,
    condition: (file) => file.type && file.type.startsWith("image/") 
  },
  { id: "fileNote", defaultValue: "", isUserInput: true },
  { id: "fileType", defaultValue: "", isUserInput: false },
];

/**
 * Higher-order function that generates a metaFields configuration function for Uppy Dashboard.
 * It combines standard built-in renderers ("fileNote", "caption", "featured") with any custom
 * fields passed in `allowedMetaFields`.
 * 
 * @param {Array<Object>} allowedMetaFields - Configuration for allowed meta fields. 
 * Expected shape: `{ id, defaultValue, isUserInput, name?, placeholder?, render?, condition? }`.
 * Users can provide custom UI fields by explicitly setting `name` and/or `render` attributes.
 * 
 * @returns {Function} Function `(file) => Array<Object>` required by Uppy Dashboard `metaFields` prop.
 */
export const getMetaFieldsRenderers = (allowedMetaFields) => {
  return (file) => {
    const fields = [];
    (allowedMetaFields || []).forEach((field) => {
      // 1) Evaluate if field has custom rendering properties (name, render).
      if (field.name || field.render) {
        const shouldRender = typeof field.condition === "function" ? field.condition(file) : true;
        if (shouldRender) {
          fields.push({
            id: field.id,
            name: field.name,
            placeholder: field.placeholder || "",
            // Render is optional, if missing Uppy falls back to standard text input
            ...(field.render && { render: field.render }),
          });
        }
        return; // Skip default handling
      }

      // 2) Default handlers for built-in known fields
      if (field.id === "fileNote") {
        fields.push({
          id: "fileNote",
          name: i18next.t("File Note"),
          placeholder: i18next.t("Set the file Note here"),
        });
      } else if (file.type && file.type.startsWith("image/")) {
        if (field.id === "caption") {
          fields.push({
            id: "caption",
            name: i18next.t("Caption"),
            placeholder: i18next.t("Set the Caption here"),
          });
        } else if (field.id === "featured") {
          fields.push({
            id: "featured",
            name: i18next.t("Feature Image"),
            render: ({ value, onChange, required, form }, h) => {
              return h("input", {
                type: "checkbox",
                onChange: (ev) => onChange(ev.target.checked),
                checked: value,
                defaultChecked: value,
                required,
                form,
              });
            },
          });
        }
      }
    });

    return fields;
  };
};

/**
 * Extends file metadata prior to upload with configured default values.
 * This ensures that required parameters are not lost and metadata is 
 * consistently structured before uploading.
 *
 * @param {Object} files - The Uppy files object dictionary.
 * @param {Array<Object>} allowedMetaFields - Configuration for metadata fields.
 * @returns {Object} Updated files dictionary.
 */
export const onBeforeUploadProcessMetaFields = (files, allowedMetaFields) => {
  const updatedFiles = {};
  
  Object.keys(files).forEach((fileID) => {
    const file = files[fileID];
    const metaDefaults = {};

    (allowedMetaFields || []).forEach((field) => {
      // Determine if this field should apply defaults to this file
      let isApplicable = true;
      if (typeof field.condition === "function") {
        isApplicable = field.condition(file);
      } else if (field.id === "caption" || field.id === "featured") {
        isApplicable = file.type && file.type.startsWith("image/");
      } // built-in 'fileNote' or any custom field without 'condition' is applicable universally

      if (isApplicable) {
        metaDefaults[field.id] = file.meta?.[field.id] ?? field.defaultValue;
      }
    });

    updatedFiles[fileID] = {
      ...file,
      meta: {
        ...file.meta,
        ...metaDefaults,
      }
    };
  });
  
  return updatedFiles;
};
