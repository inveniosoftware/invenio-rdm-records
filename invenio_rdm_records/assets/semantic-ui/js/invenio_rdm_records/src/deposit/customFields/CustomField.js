// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _get from "lodash/get";
import _set from "lodash/set";
import _cloneDeep from "lodash/cloneDeep";
import _isArray from "lodash/isArray";
import _isObject from "lodash/isObject";
import { Field } from "../serializers";

export class CustomField extends Field {
  constructor({
    fieldpath,
    deserializedDefault = null,
    serializedDefault = null,
    allowEmpty = false,
    vocabularyFields = [],
  }) {
    super({ fieldpath, deserializedDefault, serializedDefault, allowEmpty });
    this.vocabularyFields = vocabularyFields;
  }

  recursiveMapping(value, isVocabularyField, mapValue) {
    // Since Arrays are a subset of Objects, if _isArray were the else if, we would never get to that condition.
    let _value = null;
    if (_isArray(value))
      _value = value.map((v, i) => mapValue(v, i, isVocabularyField));
    else if (_isObject(value) && !isVocabularyField) {
      for (let key in value)
        value[key] = this.recursiveMapping(value[key], isVocabularyField, mapValue);
      _value = value;
    } else _value = mapValue(value, null, isVocabularyField);
    return _value;
  }

  #mapCustomFields(record, customFields, mapValue) {
    if (customFields !== null) {
      for (const [key, value] of Object.entries(customFields)) {
        const isVocabularyField = this.vocabularyFields.includes(key);
        const _value = this.recursiveMapping(value, isVocabularyField, mapValue);
        record = _set(record, `custom_fields.${key}`, _value);
      }
    }
  }

  deserialize(record) {
    const _deserialize = (value, i = undefined, isVocabulary = false) => {
      if (isVocabulary && value?.id) {
        return value.id;
      }
      // Add __key if i is passed i.e is an array. This is needed because of ArrayField
      // internal implementation
      // Note: if i is an array of strings, then we exclude the above as you cannot set
      // a property on a string
      if (i && typeof value === "object" && value !== null) value.__key = i;
      return value;
    };

    const _record = _cloneDeep(record);
    const customFields = _get(record, this.fieldpath, this.deserializedDefault);
    this.#mapCustomFields(_record, customFields, _deserialize);
    return _record;
  }

  serialize(record) {
    const _serialize = (value, i = undefined, isVocabulary = false) => {
      if (isVocabulary && typeof value === "string") {
        return { id: value };
      }
      // Delete internal __key from the sent request payload
      delete value.__key;
      return value;
    };
    const _record = _cloneDeep(record);
    const customFields = _get(record, this.fieldpath, this.serializedDefault);
    this.#mapCustomFields(_record, customFields, _serialize);
    return _record;
  }
}
