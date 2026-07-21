// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

/**
 * Default allowed metadata fields configuration.
 * @example
 * [
 *   { 
 *     id: "caption", 
 *     defaultValue: "", 
 *     name: i18next.t("Caption"),
 *     placeholder: i18next.t("Set the Caption here"),
 *     condition: (file) => file.type && file.type.startsWith("image/") 
 *   },
 *   { 
 *     id: "featured", 
 *     defaultValue: false, 
 *     name: i18next.t("Feature Image"),
 *     render: ({ value, onChange, required, form }, h) => {
 *       return h("input", {
 *         type: "checkbox",
 *         onChange: (ev) => onChange(ev.target.checked),
 *         checked: value,
 *         defaultChecked: value,
 *         required,
 *         form,
 *       });
 *     },
 *     condition: (file) => file.type && file.type.startsWith("image/") 
 *   },
 *   { 
 *     id: "fileNote", 
 *     defaultValue: "", 
 *     name: i18next.t("File Note"),
 *     placeholder: i18next.t("Set the file Note here"),
 *   },
 *   { 
 *     id: "fileType", 
 *     defaultValue: (file) => {
 *       if (file.type) {
 *         if (file.type.startsWith("image/")) return "image";
 *       }
 *       return "other";
 *     },
 *   },
 * ]
 * 
 * @type {Object[]} metaFields - Array of metadata field configuration objects. Each object defines how a specific metadata field should be handled and rendered in the Uppy Dashboard.
 * @property {string} metaFields[].id - The unique identifier of the metadata field. Used as the key in the file.meta.metadata dictionary.
 * @property {any|function(Object): any} [metaFields[].defaultValue] - Default value or a function resolving a default value based on the file object.
 * @property {string} [metaFields[].name] - Optional display name of the field. If provided, it will be used to render a standard input field, otherwise it won't be editable in UI.
 * @property {string} [metaFields[].placeholder] - Optional placeholder text for the input UI.
 * @property {function(Object, Function): Object} [metaFields[].render] - Optional custom render function for advanced UI rendering of the field using Preact `h` function. If not provided, a standard text input will be rendered when `name` is set. See {@link https://uppy.io/docs/dashboard/#metafields|Uppy Dashboard metaFields documentation}.
 * @property {function(Object): Boolean} [metaFields[].condition] - Optional function to conditionally attach or render the field based on the respective file properties (e.g. file.type).
 */
export const defaultAllowedMetaFields = [
  // { 
  //   id: "description",
  //   defaultValue: "",
  //   name: i18next.t("Description"),
  //   placeholder: i18next.t("Set the file description here"),
  // },
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
 * @param {Object} uppyFiles - The Uppy files object dictionary.
 * @param {Object} invenioFiles - The files object from Invenio.
 * @param {Array<Object>} allowedMetaFields - Configuration for metadata fields.
 * @returns {Object} Updated files dictionary.
 */
export const onBeforeUploadProcessMetaFields = (uppyFiles, invenioFiles, allowedMetaFields) => {
  const updatedFiles = {};
  
  Object.keys(uppyFiles).forEach((fileID) => {
    const uppyFile = uppyFiles[fileID];
    const invenioFile = invenioFiles[uppyFile.meta?.file_id ?? uppyFile.id] || {};
    uppyFile.meta["metadata"] = uppyFile.meta?.metadata || invenioFile?.metadata || {};
    const metadataDefaults = {};

    (allowedMetaFields || []).forEach((field) => {
      // Determine if this field should apply defaults to this file
      const isApplicable = typeof field.condition === "function" ? field.condition(uppyFile) : true;

      if (isApplicable) {
        if (uppyFile.meta.metadata?.[field.id] === undefined && uppyFile.meta?.[field.id] === undefined) {
          const value = typeof field.defaultValue === "function" ? field.defaultValue(uppyFile) : field?.defaultValue;
          metadataDefaults[field.id] = value;
          return;
        }
        metadataDefaults[field.id] = uppyFile.meta.metadata?.[field.id] || uppyFile.meta?.[field.id];
      }
    });

    updatedFiles[fileID] = {
      ...uppyFile,
      meta: {
        ...uppyFile.meta,
        metadata: {
          ...uppyFile.meta.metadata,
          ...metadataDefaults,
        }
      }
    };
  });
  
  return updatedFiles;
};
