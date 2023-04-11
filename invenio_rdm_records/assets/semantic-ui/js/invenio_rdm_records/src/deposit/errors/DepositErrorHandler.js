// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _get from "lodash/get";
import _join from "lodash/join";

export class DepositErrorHandler {
  /* eslint-disable-next-line no-unused-vars */
  extractErrors(error, record) {
    const backendErrors = _get(error, "response.data.errors", []);
    const backendErrorMessage = _get(error, "response.data.message", "");
    let frontendErrors = { message: backendErrorMessage };
    for (const fieldError of backendErrors) {
      const errorPath = _join([...fieldError.parents, fieldError.field], ".");
      frontendErrors[errorPath] = fieldError.message;
    }

    return frontendErrors;
  }
}
