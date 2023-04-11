// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Formik } from "formik";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import { AccessRightFieldCmp } from "./AccessRightField";
import "@testing-library/jest-dom/extend-expect";

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

// 2
it("Can render restricted access - record with files, restricted comm", () => {
  const setFieldValueMock = jest.fn();

  const formikProps = {
    fieldPath: "access",
    formik: {
      field: { value: { record: "restricted", files: "restricted" } },
      form: {
        setFieldValue: setFieldValueMock,
        values: { files: { enabled: true } },
        initialValues: {
          access: { record: "restricted", files: "restricted" },
        },
      },
    },
    community: { access: { visibility: "restricted" } },
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
  ).toHaveClass("active");

  // check public button not active
  expect(
    container.querySelector('[data-testid="protection-buttons-component-public"]')
  ).not.toHaveClass("active");

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
  ).toContain("Restricted");

  // check if files restricted
  expect(container.querySelector('[data-testid="access-files"]').textContent).toContain(
    "The full record is restricted"
  );
});

// 2.1
it("Can render restricted access - record without files, restricted comm", () => {
  const setFieldValueMock = jest.fn();

  const formikProps = {
    fieldPath: "access",
    formik: {
      field: { value: { record: "restricted", files: "restricted" } },
      form: {
        setFieldValue: setFieldValueMock,
        initialValues: {
          access: {
            record: "restricted",
            files: "restricted",
            embargo: {},
          },
        },
        values: { files: { enabled: false } },
      },
    },
    community: { access: { visibility: "restricted" } },
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

  expect(
    container.querySelector('[data-testid="protection-buttons-component-public"]')
  ).toHaveClass("disabled");

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
  ).toContain("Restricted");

  // check if files disabled
  expect(container.querySelector('[data-testid="access-files"]').textContent).toContain(
    "The record has no files."
  );
});

it("Can render restricted access - record with files, restricted comm, embargoed", () => {
  // even active embargo should not allow the deposit to un-restrict the record
  const setFieldValueMock = jest.fn();

  const formikProps = {
    fieldPath: "access",
    formik: {
      field: {
        value: {
          record: "restricted",
          files: "restricted",
          embargo: { until: "3000-12-01", reason: "unknown", active: true },
        },
      },
      form: {
        setFieldValue: setFieldValueMock,
        values: { files: { enabled: true } },
        initialValues: {
          access: {
            embargo: { until: "3000-12-01", reason: "unknown", active: true },
            record: "restricted",
            files: "restricted",
          },
        },
      },
    },
    community: { access: { visibility: "restricted" } },
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
  ).toHaveClass("active");

  // check public button not active
  expect(
    container.querySelector('[data-testid="protection-buttons-component-public"]')
  ).not.toHaveClass("active");

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
  ).toContain("Embargoed (full record)");

  // check if files disabled
  expect(container.querySelector('[data-testid="access-files"]').textContent).toContain(
    "The full record is restricted."
  );
});
