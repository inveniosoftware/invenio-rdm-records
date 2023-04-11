// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Formik } from "formik";
import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import { AccessRightFieldCmp } from "./AccessRightField";
import "@testing-library/jest-dom/extend-expect";

/* tests should verify those use cases:
   1) record public, community public, files enabled
      restriction buttons:
          public: active, restricted: active
      embargo field: enabled
      files section: no restriction
      message:

    1.1) files disabled
      file section: no files

   2) record restricted, community restricted, files enabled

      restriction buttons:
          public: disabled, restricted: active
      embargo field: disabled
      files section: restricted

    2.1) files disabled
      file section: no files

   3) record restricted, community public, files enabled
      restriction buttons:
          public: active, restricted: active, default
      embargo field enabled
      files section: restricted
      message:

    3.1) files disabled
      file section: no files

   4) record public, community restricted, files enabled
      should not happen!

      restriction buttons:
          public: disabled, restricted: active, default
      embargo field: disabled
      files section: no restriction
      message:

    4.1) files disabled
      file section: no files
*/

let container;

beforeEach(() => {
  // setup a DOM element as a render target
  container = document.createElement("div");
  document.body.appendChild(container);
});
afterEach(() => {
  // cleanup on exiting
  unmountComponentAtNode(container);
  container.remove();
  container = null;
});

it("Can render public access - record without files, public comm, not embargoed", () => {
  const setFieldValueMock = jest.fn();

  const formikProps = {
    fieldPath: "access",
    formik: {
      field: {
        value: {
          record: "restricted",
          files: "restricted",
          embargo: { until: "1900-12-01", reason: "unknown", active: false },
        },
      },
      form: {
        setFieldValue: setFieldValueMock,
        values: { files: { enabled: false } },
        initialValues: {
          access: {
            embargo: { until: "1900-12-01", reason: "unknown", active: false },
            record: "restricted",
            files: "restricted",
          },
        },
      },
    },
    community: { access: { visibility: "public" } },
    isMetadataOnly: true,
    label: "Access",
    labelIcon: "shield",
  };

  act(() => {
    render(
      <Formik initialValues={formikProps.formik.form.initialValues} onSubmit={() => {}}>
        <AccessRightFieldCmp {...formikProps} />
      </Formik>,
      container
    );
  });

  // check restricted button active
  expect(
    container.querySelector('[data-testid="protection-buttons-component-restricted"]')
  ).toHaveClass("active");

  // check public button not active
  expect(
    container.querySelector('[data-testid="protection-buttons-component-public"]')
  ).not.toHaveClass("active");

  // check embargo checkbox disabled
  expect(
    container.querySelector('[data-testid="embargo-checkbox-component"]')
  ).not.toHaveClass("disabled");

  // check embargo option disabled
  expect(
    container.querySelector('[data-testid="option-list-embargo"]')
  ).not.toHaveClass("disabled");

  // check if message informs about restriction
  expect(
    container.querySelector('[data-testid="access-message"]').textContent
  ).toContain("Restricted");

  // check if files disabled
  expect(container.querySelector('[data-testid="access-files"]').textContent).toContain(
    "The record has no files."
  );
});

it("Can render public access - record with files, public comm, not embargoed", () => {
  const setFieldValueMock = jest.fn();
  const formikProps = {
    fieldPath: "access",
    formik: {
      field: {
        value: {
          record: "public",
          files: "public",
          embargo: { until: "3000-12-01", reason: "unknown", active: false },
        },
      },
      form: {
        setFieldValue: setFieldValueMock,
        values: { files: { enabled: true } },
        initialValues: {
          access: {
            embargo: { until: "3000-12-01", reason: "unknown", active: false },
            record: "public",
            files: "public",
          },
        },
      },
    },
    community: { access: { visibility: "public" } },
    isMetadataOnly: false,
    label: "Access",
    labelIcon: "shield",
  };

  act(() => {
    render(
      <Formik initialValues={formikProps.formik.form.initialValues} onSubmit={() => {}}>
        <AccessRightFieldCmp {...formikProps} />
      </Formik>,
      container
    );
  });

  // check restricted button active
  expect(
    container.querySelector('[data-testid="protection-buttons-component-restricted"]')
  ).not.toHaveClass("active");

  // check public button not active
  expect(
    container.querySelector('[data-testid="protection-buttons-component-public"]')
  ).toHaveClass("active");

  // check embargo checkbox disabled
  expect(
    container.querySelector('[data-testid="embargo-checkbox-component"]')
  ).toHaveClass("disabled");

  // check embargo option disabled
  expect(container.querySelector('[data-testid="option-list-embargo"]')).toHaveClass(
    "disabled"
  );

  // check if message informs about restriction
  expect(
    container.querySelector('[data-testid="access-message"]').textContent
  ).toContain("The record and files are publicly accessible.");

  // check if files disabled
  expect(container.querySelector('[data-testid="access-files"]').textContent).toContain(
    "Files onlyPublicRestricted"
  );
});
