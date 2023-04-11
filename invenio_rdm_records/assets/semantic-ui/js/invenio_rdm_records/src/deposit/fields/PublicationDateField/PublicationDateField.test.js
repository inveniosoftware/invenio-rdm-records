// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";

import { Form, Formik } from "formik";

import { PublicationDateField } from "./PublicationDateField";

it("renders without crashing", () => {
  const div = document.createElement("div");

  ReactDOM.render(
    <Formik>
      {() => (
        <Form>
          <PublicationDateField fieldPath="fieldPath" />
        </Form>
      )}
    </Formik>,
    div
  );
});
