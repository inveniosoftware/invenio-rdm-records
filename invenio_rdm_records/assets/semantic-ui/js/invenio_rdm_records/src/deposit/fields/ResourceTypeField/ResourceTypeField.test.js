/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import ReactDOM from "react-dom";

import { Form, Formik } from "formik";

import { ResourceTypeField } from "./ResourceTypeField";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const options = [
    {
      icon: "",
      id: "resource-type-id-A",
      type_name: "Type A",
      subtype_name: "Subtype A",
    },
    {
      icon: "frown outline",
      id: "resource-type-id-B",
      type_name: "Type B",
      subtype_name: "Subtype B",
    },
  ];

  ReactDOM.render(
    <Formik>
      {() => (
        <Form>
          <ResourceTypeField fieldPath="fieldPath" options={options} />
        </Form>
      )}
    </Formik>,
    div
  );
});
