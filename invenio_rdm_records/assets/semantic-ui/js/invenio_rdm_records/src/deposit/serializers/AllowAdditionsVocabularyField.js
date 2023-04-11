// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { VocabularyField } from "./VocabularyField";
import _cloneDeep from "lodash/cloneDeep";
import _get from "lodash/get";
import _set from "lodash/set";

export class AllowAdditionsVocabularyField extends VocabularyField {
  deserialize(record) {
    const fieldValue = _get(record, this.fieldpath, this.deserializedDefault);
    // We deserialize the values in the format
    // {id: 'vocab_id', <labelField>: 'vacab_name'} for controlled values
    // and {<labelField>: 'vocab_name'} for user added entries
    const _deserialize = (value) => ({
      ...(value.id ? { id: value.id } : {}),
      [this.labelField]: value[this.labelField],
    });
    let deserializedValue = null;
    if (fieldValue !== null) {
      deserializedValue = Array.isArray(fieldValue)
        ? fieldValue.map(_deserialize)
        : _deserialize(fieldValue);
    }
    return _set(_cloneDeep(record), this.fieldpath, deserializedValue || fieldValue);
  }
}
