// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { getIn } from "formik";

export const getFieldErrors = (form, fieldPath) => {
  return (
    getIn(form.errors, fieldPath, null) || getIn(form.initialErrors, fieldPath, null)
  );
};
