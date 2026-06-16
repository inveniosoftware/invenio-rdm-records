/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

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
