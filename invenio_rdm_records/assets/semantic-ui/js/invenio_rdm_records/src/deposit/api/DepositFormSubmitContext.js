/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

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
