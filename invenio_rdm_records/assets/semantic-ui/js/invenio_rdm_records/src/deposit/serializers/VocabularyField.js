// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _get from "lodash/get";
import _set from "lodash/set";
import _cloneDeep from "lodash/cloneDeep";

import { Field } from "../serializers";

export class VocabularyField extends Field {
  constructor({
    fieldpath,
    deserializedDefault = null,
    serializedDefault = null,
    labelField = "name",
  }) {
    super({ fieldpath, deserializedDefault, serializedDefault });
    this.labelField = labelField;
  }

  /**
   * Deserializes a given record.
   *
   * @param {object} record The record to be deserialized.
   *
   * @returns {object} Returns a deep copy of the given record, deserialized using the provided settings.
   */
  deserialize(record) {
    /**
     * Deserializes an object.
     *
     * If the object contains an id, its returned as-is.
     *
     * @param {object} value The object to be deserialized.
     *
     * @returns {(object|*)} Returns a clone of the given object or its 'id' property, if exists.
     */
    const _deserialize = (value) => {
      if (value?.id) {
        return value.id;
      }
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

  serialize(record) {
    const _serialize = (value) => {
      if (typeof value === "string") {
        return { id: value };
      }

      return {
        ...(value.id ? { id: value.id } : {}),
        ...(value[this.labelField] && { [this.labelField]: value[this.labelField] }),
      };
    };

    let fieldValue = _get(record, this.fieldpath, this.serializedDefault);
    let serializedValue = null;
    if (fieldValue !== null) {
      serializedValue = Array.isArray(fieldValue)
        ? fieldValue.map(_serialize)
        : _serialize(fieldValue); // fieldValue is a string
    }

    return _set(_cloneDeep(record), this.fieldpath, serializedValue || fieldValue);
  }
}
