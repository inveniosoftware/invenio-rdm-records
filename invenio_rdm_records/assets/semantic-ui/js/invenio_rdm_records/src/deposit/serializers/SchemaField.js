// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2024 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _cloneDeep from "lodash/cloneDeep";
import _get from "lodash/get";
import _pick from "lodash/pick";
import _set from "lodash/set";
import { Field } from "./Field";

export class SchemaField extends Field {
  /**
   * IMPORTANT: This component is so far only for list subfields, since
   * the use case of a single object with schema has not arisen yet.
   */
  constructor({ fieldpath, schema, deserializedDefault = [], serializedDefault = [] }) {
    super({ fieldpath, deserializedDefault, serializedDefault });
    this.schema = schema;
    this.schemaKeys = Object.keys(this.schema);
  }

  /**
   * Deserialize backend field given by `this.fieldPath` from `serialized`
   * object into format compatible with frontend using `this.schema`.
   * @method
   * @param {object} serialized - in API format
   * @returns {object} deserialized - in frontent format
   */
  deserialize(serialized, defaultLocale) {
    const fieldValues = _get(serialized, this.fieldpath, this.deserializedDefault);
    const deserializedElements = fieldValues.map((value, i) => {
      let deserializedElement = _pick(value, this.schemaKeys);
      this.schemaKeys.forEach((key) => {
        deserializedElement = this.schema[key].deserialize(
          deserializedElement,
          defaultLocale
        );
      });
      // Add __key
      deserializedElement.__key = i;
      return deserializedElement;
    });

    return _set(_cloneDeep(serialized), this.fieldpath, deserializedElements);
  }

  /**
   * Serialize frontend field given by `this.fieldPath` from `deserialized`
   * object into format compatible with backend using `this.schema`.
   * @method
   * @param {object} deserialized - in frontend format
   * @returns {object} serialized - in API format
   *
   */
  serialize(deserialized, defaultLocale) {
    const fieldValues = _get(deserialized, this.fieldpath, this.serializedDefault);
    const serializedElements = fieldValues?.map((value) => {
      let serializedElement = _pick(value, this.schemaKeys);
      this.schemaKeys.forEach((key) => {
        serializedElement = this.schema[key].serialize(
          serializedElement,
          defaultLocale
        );
      });
      return serializedElement;
    });
    if (serializedElements !== null) {
      return _set(_cloneDeep(deserialized), this.fieldpath, serializedElements);
    }
    return serializedElements;
  }
}
