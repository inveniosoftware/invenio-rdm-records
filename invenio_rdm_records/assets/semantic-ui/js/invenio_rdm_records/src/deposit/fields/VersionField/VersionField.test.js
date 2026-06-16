/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import ReactDOM from "react-dom";

import { Form, Formik } from "formik";

import { VersionField } from "./VersionField";

it("renders without crashing", () => {
  const div = document.createElement("div");

  ReactDOM.render(
    <Formik>
      {() => (
        <Form>
          <VersionField fieldPath="fieldPath" />
        </Form>
      )}
    </Formik>,
    div
  );
});
