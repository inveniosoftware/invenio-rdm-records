// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _get from "lodash/get";
import _set from "lodash/set";
import _cloneDeep from "lodash/cloneDeep";

export class Field {
  constructor({
    fieldpath,
    deserializedDefault = null,
    serializedDefault = null,
    allowEmpty = false,
  }) {
    this.fieldpath = fieldpath;
    this.deserializedDefault = deserializedDefault;
    this.serializedDefault = serializedDefault;
    this.allowEmpty = allowEmpty;
  }

  deserialize(record) {
    let fieldValue = _get(record, this.fieldpath, this.deserializedDefault);
    if (fieldValue !== null) {
      return _set(_cloneDeep(record), this.fieldpath, fieldValue);
    }
    return record;
  }

  serialize(record) {
    let fieldValue = _get(record, this.fieldpath, this.serializedDefault);
    if (fieldValue !== null) {
      return _set(_cloneDeep(record), this.fieldpath, fieldValue);
    }
    return record;
  }
}
