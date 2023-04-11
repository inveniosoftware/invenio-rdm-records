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

  #mapCustomFields(record, customFields, mapValue) {
    if (customFields !== null) {
      for (const [key, value] of Object.entries(customFields)) {
        const isVocabularyField = this.vocabularyFields.includes(key);
        const _value = _isArray(value)
          ? value.map((v, i) => mapValue(v, i, isVocabularyField))
          : mapValue(value, null, isVocabularyField);
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
      if (i) value.__key = i;
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
