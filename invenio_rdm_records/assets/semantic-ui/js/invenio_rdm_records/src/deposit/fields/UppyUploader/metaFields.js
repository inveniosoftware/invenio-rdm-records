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
    name: i18next.t("Caption"),
    placeholder: i18next.t("Set the Caption here"),
    condition: (file) => file.type && file.type.startsWith("image/") 
  },
  { 
    id: "featured", 
    defaultValue: false, 
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
    condition: (file) => file.type && file.type.startsWith("image/") 
  },
  { 
    id: "fileNote", 
    defaultValue: "", 
    name: i18next.t("File Note"),
    placeholder: i18next.t("Set the file Note here"),
  },
  { 
    id: "fileType", 
    defaultValue: (file) => {
      if (file.type) {
        if (file.type.startsWith("image/")) return "image";
      }
      return "other";
    },
  },
];

/**
 * Higher-order function that generates a metaFields configuration function for Uppy Dashboard.
 * Evaluates custom fields passed in `allowedMetaFields` to render them.
 * 
 * @param {Array<Object>} allowedMetaFields - Configuration for allowed meta fields. 
 * Expected shape: `{ id, defaultValue, name?, placeholder?, render?, condition? }`.
 * Users can provide custom UI fields by explicitly setting `name` and/or `render` attributes.
 * `defaultValue` can either be a static mapped value, or a dynamic function `(file) => any`.
 * 
 * @returns {Function} Function `(file) => Array<Object>` required by Uppy Dashboard `metaFields` prop.
 */
export const getMetaFieldsRenderers = (allowedMetaFields) => {
  return (file) => {
    const fields = [];
    (allowedMetaFields || []).forEach((field) => {
      // Evaluate if field has rendering properties (name, render).
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
    file.meta["metadata"] = file.meta?.metadata || {};
    const metadataDefaults = {};

    (allowedMetaFields || []).forEach((field) => {
      // Determine if this field should apply defaults to this file
      const isApplicable = typeof field.condition === "function" ? field.condition(file) : true;

      if (isApplicable) {
        if (file.meta.metadata?.[field.id] === undefined && file.meta?.[field.id] === undefined) {
          const value = typeof field.defaultValue === "function" ? field.defaultValue(file) : field?.defaultValue;
          metadataDefaults[field.id] = value;
          return;
        }
        metadataDefaults[field.id] = file.meta.metadata?.[field.id] || file.meta?.[field.id];
      }
    });

    updatedFiles[fileID] = {
      ...file,
      meta: {
        ...file.meta,
        metadata: {
          ...file.meta.metadata,
          ...metadataDefaults,
        }
      }
    };
  });
  
  return updatedFiles;
};
