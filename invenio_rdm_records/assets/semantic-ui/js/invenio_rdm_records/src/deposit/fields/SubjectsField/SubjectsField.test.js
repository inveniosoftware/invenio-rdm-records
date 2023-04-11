// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Form, Formik } from "formik";
import React from "react";
import ReactDOM from "react-dom";

import { SubjectsField } from "./SubjectsField";

// TODO: Re-enable when SubjectsField is supported
it.skip("renders without crashing", () => {
  const div = document.createElement("div");
  const limitToOptions = [
    { text: "All", value: "all" },
    { text: "MeSH", value: "mesh" },
  ];
  const options = [
    { title: "Deep Learning", id: "dl", scheme: "user" },
    { title: "MeSH: Cognitive Neuroscience", id: "cn", scheme: "mesh" },
    { title: "FAST: Glucagonoma", id: "gl", scheme: "fast" },
  ];

  ReactDOM.render(
    <Formik>
      {() => (
        <Form>
          <SubjectsField
            fieldPath="fieldPath"
            limitToOptions={limitToOptions}
            options={options}
          />
        </Form>
      )}
    </Formik>,
    div
  );
});
