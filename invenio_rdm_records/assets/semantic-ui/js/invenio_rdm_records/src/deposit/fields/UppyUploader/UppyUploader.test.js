/*
 * SPDX-FileCopyrightText: 2026 Dhairya Jangir.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import { fireEvent, render, within } from "@testing-library/react";
import "@testing-library/jest-dom/extend-expect";
import { Formik } from "formik";
import { I18nextProvider } from "react-i18next";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { OverridableContext } from "react-overridable";
import { Provider } from "react-redux";
import { createStore } from "redux";
import { UppyUploaderComponent } from "./UppyUploader";

// File transfers and the Uppy dashboard are outside these editing-control tests.
// Keep the existing editing accordion, modal, and new-version button real.
jest.mock(
  "@uppy/core",
  () =>
    class Uppy {
      use() {
        return this;
      }
      close() {}
      setOptions() {}
      getPlugin() {}
      getState() {
        return { files: {} };
      }
      on() {}
      off() {}
    }
);
jest.mock("@uppy/react", () => ({
  Dashboard: () => <div data-testid="uppy-dashboard" />,
}));
jest.mock("@uppy/image-editor", () => jest.fn());
jest.mock("./RDMUppyUploaderPlugin", () => jest.fn());
jest.mock("./locale", () => ({ useUppyLocale: () => ({}) }));
jest.mock("../FileUploader/QuotaManager/QuotaManager", () => ({
  QuotaManager: () => null,
}));

const allowedFileModification = {
  enabled: true,
  valid_user: true,
  allowed: true,
  fileModification: {
    allowed: true,
    policy: { description: "You can correct minor errors in your published files." },
  },
  context: { days_until: 15 },
};

const renderUploader = (overrides = {}, componentOverrides = {}) => {
  const record = {
    id: "published-record",
    is_published: overrides.isDraftRecord !== true,
    files: { enabled: true },
    links: {
      file_modification: "/api/records/published-record/file-modification",
      versions: "/api/records/published-record/versions",
    },
  };
  const props = {
    record,
    config: {
      transfer_types: {},
      enabled_transfer_types: [],
      allow_external_doi_versions: true,
    },
    files: {},
    isDraftRecord: false,
    filesLocked: true,
    permissions: { can_new_version: true },
    fileModification: allowedFileModification,
    initializeFileUpload: jest.fn(),
    finalizeUpload: jest.fn(),
    deleteFile: jest.fn(),
    uploadPart: jest.fn(),
    saveAndFetchDraft: jest.fn(),
    setUploadProgress: jest.fn(),
    importParentFiles: jest.fn(),
    ...overrides,
  };

  return render(
    <Provider store={createStore(() => ({}))}>
      <I18nextProvider i18n={i18next}>
        <OverridableContext.Provider value={componentOverrides}>
          <Formik initialValues={props.record} onSubmit={() => {}}>
            <UppyUploaderComponent {...props} />
          </Formik>
        </OverridableContext.Provider>
      </I18nextProvider>
    </Provider>
  );
};

describe("published-file editing in the Uppy uploader", () => {
  it("preserves policy and custom props for an existing action override", () => {
    const customActions = jest.fn(() => <div>Custom published-file actions</div>);
    const { getByText } = renderUploader(
      { customUiProperty: "instance-specific value" },
      {
        "ReactInvenioDeposit.FileUploader.NewVersionButton.container": customActions,
      }
    );

    expect(getByText("Custom published-file actions")).toBeInTheDocument();
    const overrideProps = customActions.mock.calls[0][0];
    expect(overrideProps.fileModification).toBe(allowedFileModification);
    expect(overrideProps.customUiProperty).toBe("instance-specific value");
  });

  it("lets an eligible user open the existing file-correction checklist", () => {
    const { getByText, getByRole, queryByTestId } = renderUploader();

    expect(queryByTestId("uppy-dashboard")).not.toBeInTheDocument();
    fireEvent.click(getByText("Edit files"));
    fireEvent.click(getByText("Edit published files"));

    const dialog = within(getByRole("dialog"));
    expect(dialog.getByText("File modification checklist:")).toBeInTheDocument();
    expect(
      dialog.getByText("You can correct minor errors in your published files.", {
        exact: false,
      })
    ).toBeInTheDocument();
    expect(dialog.getByText("Enable file editing").closest("button")).toBeDisabled();
  });

  it("keeps the support explanation available when an eligible user's policy has expired", () => {
    const { getByText, getByRole } = renderUploader({
      fileModification: {
        ...allowedFileModification,
        allowed: false,
        fileModification: { allowed: false },
      },
    });

    fireEvent.click(getByText("Edit files"));
    fireEvent.click(getByText("Edit published files"));

    const dialog = within(getByRole("dialog"));
    expect(
      dialog.getByText(/Please contact us to request file modification/)
    ).toBeInTheDocument();
    expect(dialog.queryByText("Enable file editing")).not.toBeInTheDocument();
  });

  it.each([
    ["disabled", { enabled: false, valid_user: true }],
    ["not available to this user", { enabled: true, valid_user: false }],
    ["not configured", undefined],
  ])(
    "keeps the new-version guidance when file editing is %s",
    (_, fileModification) => {
      const { getByText, queryByText } = renderUploader({ fileModification });

      expect(queryByText("Edit files")).not.toBeInTheDocument();
      expect(queryByText("Edit published files")).not.toBeInTheDocument();
      expect(
        getByText("You must create a new version to add, modify or delete files.")
      ).toBeInTheDocument();
      expect(getByText("New version").closest("button")).not.toBeDisabled();
    }
  );

  it.each([
    ["the editing accordion", allowedFileModification],
    ["the new-version guidance", { enabled: false }],
  ])("respects the new-version permission in %s", (_, fileModification) => {
    const { getByText } = renderUploader({
      permissions: { can_new_version: false },
      fileModification,
    });

    if (fileModification.enabled) {
      fireEvent.click(getByText("Edit files"));
    }
    expect(getByText("New version").closest("button")).toBeDisabled();
  });

  it.each([
    ["a new draft", { isDraftRecord: true, filesLocked: false }],
    ["an unlocked published record", { isDraftRecord: false, filesLocked: false }],
  ])("shows the uploader without a correction prompt for %s", (_, overrides) => {
    const { getByTestId, queryByText } = renderUploader(overrides);

    expect(getByTestId("uppy-dashboard")).toBeInTheDocument();
    expect(queryByText("Edit files")).not.toBeInTheDocument();
    expect(queryByText("Edit published files")).not.toBeInTheDocument();
    expect(queryByText("New version")).not.toBeInTheDocument();
  });
});
