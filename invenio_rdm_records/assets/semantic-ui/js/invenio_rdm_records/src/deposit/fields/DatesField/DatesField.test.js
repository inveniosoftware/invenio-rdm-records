// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";

import { Form, Formik } from "formik";

import { DatesField } from "./DatesField";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const options = {
    type: [
      {
        text: "type Text 1",
        value: "typeValue1",
      },
      {
        text: "type Text 2",
        value: "typeValue2",
      },
    ],
  };

  ReactDOM.render(
    <Formik>
      {() => (
        <Form>
          <DatesField fieldPath="fieldPath" options={options} />
        </Form>
      )}
    </Formik>,
    div
  );
});
