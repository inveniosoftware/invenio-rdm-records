/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import ReactDOM from "react-dom";

import { Form, Formik } from "formik";

import { RelatedWorksField } from "./RelatedWorksField";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const options = {
    relations: [{ text: "Is supplemented by", value: "issupplementedby" }],
    scheme: [{ text: "Arxiv", value: "arxiv" }],
    resource_type: [{ text: "Dataset", value: "dataset", icon: "table" }],
  };

  ReactDOM.render(
    <Formik>
      {() => (
        <Form>
          <RelatedWorksField fieldPath="fieldPath" options={options} />
        </Form>
      )}
    </Formik>,
    div
  );
});
