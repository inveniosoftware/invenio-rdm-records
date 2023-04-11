// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";

export const DepositFormSubmitActions = {
  SAVE: "SAVE",
  PUBLISH: "PUBLISH",
  PUBLISH_WITHOUT_COMMUNITY: "PUBLISH_WITHOUT_COMMUNITY",
  PREVIEW: "PREVIEW",
  DELETE: "DELETE",
  RESERVE_PID: "RESERVE_PID",
  DISCARD_PID: "DISCARD_PID",
  SUBMIT_REVIEW: "SUBMIT_REVIEW",
};

/**
 * The current version of Formik does not allow to pass a context/arg to the submit action.
 * The assumption is that there must be only one Submit button in a form.
 * As a workaround, each submit button (Save, Publish, etc...) will:
 * 1. call `setSubmitContext` with the action name as first param (mandatory) and any extra context, if needed.
 * 2. call `formik.handleSubmit` to trigger the action.
 *
 * This might be fixed in future versions of Formik. See:
 * - https://github.com/jaredpalmer/formik/issues/214
 * - https://github.com/jaredpalmer/formik/issues/1792
 */
export const DepositFormSubmitContext = React.createContext({
  setSubmitContext: undefined,
});
