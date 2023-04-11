// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Field } from "../serializers";
import _cloneDeep from "lodash/cloneDeep";
import _get from "lodash/get";
import _set from "lodash/set";

export class FundingField extends Field {
  constructor({ fieldpath, deserializedDefault = null, serializedDefault = null }) {
    super({ fieldpath, deserializedDefault, serializedDefault });
  }

  /**
   * Deserializes a funding record.
   *
   * @param {object} record the funding record to be deserialized.
   * @param {string} defaultLocale - The default locale
   *
   * @returns {object} the deserialized record.
   */
  deserialize(record, defaultLocale) {
    /**
     * Deserializes a record. In case the record contains a 'title' property, it will extract its 'en' property.
     *
     * @param {object} value The object to be deserialized.
     *
     * @todo record's title is deserialized reading an 'en' locale. This needs to take into account the current locale or pass that
     * responsability to backend.
     *
     * @returns {(object|*)} Returns a deep copy of the given object.
     */
    const _deserialize = (value) => {
      const deserializedValue = _cloneDeep(value);
      if (value?.title) {
        deserializedValue.title = value.title[defaultLocale];
      }

      if (value.identifiers) {
        const allowedIdentifiers = ["url"];

        allowedIdentifiers.forEach((identifier) => {
          let identifierValue = null;
          value.identifiers.forEach((v) => {
            if (v.scheme === identifier) {
              identifierValue = v.identifier;
            }
          });

          if (identifierValue) {
            deserializedValue[identifier] = identifierValue;
          }
        });

        delete deserializedValue["identifiers"];
      }
      return deserializedValue;
    };

    const fieldValue = _get(record, this.fieldpath, this.deserializedDefault);
    let deserializedValue = null;
    if (fieldValue !== null) {
      deserializedValue = Array.isArray(fieldValue)
        ? fieldValue.map(_deserialize)
        : _deserialize(fieldValue);
    }

    return _set(_cloneDeep(record), this.fieldpath, deserializedValue || fieldValue);
  }

  /**
   * Serializes a funding record.
   *
   * @param {object} record
   * @param {string} defaultLocale - The default locale
   *
   * @returns
   */
  serialize(record, defaultLocale) {
    /**
     * Serializes a record. Either returns a new object with the record's id or returns a deep copy of the record.
     *
     * @param {object} value
     *
     * @todo record's title is serialized forcing an 'en' locale. This needs to take into account the current locale or pass that
     * responsability to backend.
     *
     * @returns an object containing the record's id, if it has an 'id' property.
     */
    const _serialize = (value) => {
      if (value.id) {
        return { id: value.id };
      }

      // Record is a custom record, without explicit 'id'
      const clonedValue = _cloneDeep(value);
      if (value.title) {
        clonedValue.title = {
          [defaultLocale]: value.title,
        };
      }

      if (value.url) {
        clonedValue.identifiers = [
          {
            identifier: value.url,
            scheme: "url",
          },
        ];
        delete clonedValue["url"];
      }

      return clonedValue;
    };

    let fieldValue = _get(record, this.fieldpath, this.serializedDefault);
    let serializedValue = null;
    if (fieldValue !== null) {
      serializedValue = Array.isArray(fieldValue)
        ? fieldValue.map(_serialize)
        : _serialize(fieldValue);
    }

    return _set(_cloneDeep(record), this.fieldpath, serializedValue || fieldValue);
  }
}
