// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _get from "lodash/get";
import _isEqual from "lodash/isEqual";

import { Field } from "./Field";

export class DatesField extends Field {
  /**
   * Serialize frontend dates to backend dates.
   * Strips it out if only default entry is there.
   * @method
   * @param {object} record - in frontend format
   * @returns {object} record - in API format
   */
  serialize(record) {
    const recordDates = _get(record, this.fieldpath, this.serializedDefault);
    // Remove dates if only the default empty date is there
    // NOTE: We have to do this because a date is show for UI sake, but if not
    //       filled, it would be sent to backend and generate a validation
    //       error
    // NOTE: This check is because null values are stripped at first.
    //       We might want to revisit that...
    if (_isEqual(recordDates, [{ type: "accepted" }])) {
      delete record.metadata.dates;
    }

    return record;
  }
}
