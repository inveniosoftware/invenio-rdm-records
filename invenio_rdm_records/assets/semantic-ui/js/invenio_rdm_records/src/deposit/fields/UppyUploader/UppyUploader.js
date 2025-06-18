// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import Uppy from "@uppy/core";
import { Dashboard } from "@uppy/react";
import ImageEditor from "@uppy/image-editor";
import { useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import { Grid, Message, Icon, Button } from "semantic-ui-react";
import Overridable from "react-overridable";
import RDMUppyUploaderPlugin from "./RDMUppyUploaderPlugin";
import { NewVersionButton } from "../../controls/NewVersionButton";
import { UploadState } from "../../state/reducers/files";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { getFilesList, FilesListTable, FileUploaderToolbar } from "../FileUploader";
import { useUppyLocale } from "./locale";

const defaultDashboardProps = {
  showRemoveButtonAfterComplete: false,
  showLinkToFileUploadResult: true,
  proudlyDisplayPoweredByUppy: false,
  hideProgressAfterFinish: true,
  hidePauseResumeButton: true,
  disableLocalFiles: false,
  // Allows to select both files and folders
  fileManagerSelectionType: "both",
  height: "100%",
  width: "100%",
  autoOpen: null,
  autoOpenFileEditor: false,
};

export const UppyUploaderComponent = ({
  config,
  files,
  isDraftRecord,
  hasParentRecord,
  quota,
  permissions,
  record,
  initializeFileUpload,
  finalizeUpload,
  deleteFile,
  uploadPart,
  saveAndFetchDraft,
  setUploadProgress,
  importParentFiles,
  importButtonIcon,
  importButtonText,
  isFileImportInProgress,
  fileUploadConcurrency,
  decimalSizeDisplay,
  filesLocked,
  allowEmptyFiles,
  ...uiProps
}) => {
  // We extract the working copy of the draft stored as `values` in formik
  const { values: formikDraft, errors, initialErrors } = useFormikContext();
  const { filesList } = getFilesList(files);
  const hasError = (errors.files || initialErrors?.files) && files;
  const locale = useUppyLocale();
  const filesEnabled = _get(formikDraft, "files.enabled", false);
  const filesSize = filesList.reduce((totalSize, file) => (totalSize += file.size), 0);
  const lockFileUploader = !isDraftRecord && filesLocked;
  const filesLeft = filesList.length < quota.maxFiles;
  const displayImportBtn =
    filesEnabled && isDraftRecord && hasParentRecord && !filesList.length;

  const transfersConfig = React.useMemo(() => {
    const {
      transfer_types: transferType,
      enabled_transfer_types: enabledTypes,
      default_transfer_type: defaultType,
    } = config;
    return {
      transferType,
      enabledTypes,
      defaultType,
    };
  }, [config]);

  const restrictions = React.useMemo(
    () => ({
      minFileSize: allowEmptyFiles ? 0 : 1,
      maxNumberOfFiles: quota.maxFiles - filesList.length,
      maxTotalFileSize: quota.maxStorage - filesSize,
    }),
    [allowEmptyFiles, quota, filesList, filesSize]
  );

  const isTransferSupported = React.useCallback(
    (transferType) => transfersConfig.enabledTypes.includes(transferType),
    [transfersConfig]
  );

  const [uppy] = useState(() =>
    new Uppy({
      debug: false,
      autoProceed: false,
      restrictions,
      locale,
    })
      .use(RDMUppyUploaderPlugin, {
        limit: fileUploadConcurrency,
        transferType: transfersConfig.transferType,
        isTransferSupported,
        quota,
        // Bind Redux file actions to the uploader plugin
        initializeFileUpload,
        finalizeUpload,
        saveAndFetchDraft,
        setUploadProgress,
        uploadPart,
        abortUpload: (file) => deleteFile(file),
        checkPartIntegrity: true,
      })
      .use(ImageEditor)
  );

  React.useEffect(() => {
    const uploaderPlugin = uppy.getPlugin("RDMUppyUploaderPlugin");
    if (uploaderPlugin) {
      // Synchronize uploader state with current formik state
      uploaderPlugin.draftRecord = formikDraft;
    }
  }, [uppy, formikDraft]);

  React.useEffect(() => {
    // Synchronize uppy locale with i18next
    uppy.setOptions({ locale });
  }, [uppy, locale]);

  React.useEffect(() => {
    uppy.setOptions({ restrictions });
  }, [uppy, restrictions]);

  React.useEffect(() => {
    const dashboardPlugin = uppy.getPlugin("uppy-uploader-dashboard");
    if (!dashboardPlugin) {
      return;
    }
    dashboardPlugin.setOptions({ disabled: !filesLeft });
  }, [uppy, filesLeft]);

  return (
    <Overridable
      id="ReactInvenioDeposit.FileUploader.layout"
      config={config}
      files={files}
      isDraftRecord={isDraftRecord}
      hasParentRecord={hasParentRecord}
      quota={quota}
      permissions={permissions}
      record={record}
      initializeFileUpload={initializeFileUpload}
      finalizeUpload={finalizeUpload}
      uploadPart={uploadPart}
      saveAndFetchDraft={saveAndFetchDraft}
      setUploadProgress={setUploadProgress}
      deleteFile={deleteFile}
      importParentFiles={importParentFiles}
      importButtonIcon={importButtonIcon}
      importButtonText={importButtonText}
      isFileImportInProgress={isFileImportInProgress}
      decimalSizeDisplay={decimalSizeDisplay}
      filesEnabled={filesEnabled}
      filesList={filesList}
      displayImportBtn={displayImportBtn}
      filesSize={filesSize}
      filesLocked={lockFileUploader}
      hasError={hasError}
      uppy={uppy}
      {...uiProps}
    >
      <Grid className="file-uploader">
        <Grid.Row className="pt-10 pb-5">
          {!lockFileUploader && (
            <FileUploaderToolbar
              {...uiProps}
              config={config}
              filesEnabled={filesEnabled}
              filesList={filesList}
              filesSize={filesSize}
              quota={quota}
              decimalSizeDisplay={decimalSizeDisplay}
            />
          )}
        </Grid.Row>
        <Overridable
          id="ReactInvenioDeposit.FileUploader.ImportButton.container"
          importButtonIcon={importButtonIcon}
          importButtonText={importButtonText}
          importParentFiles={importParentFiles}
          isFileImportInProgress={isFileImportInProgress}
          displayImportBtn={displayImportBtn}
          {...uiProps}
        >
          {displayImportBtn && (
            <Grid.Row className="pb-5 pt-5">
              <Grid.Column width={16}>
                <Message visible info>
                  <div className="right-floated display-inline-block">
                    <Button
                      type="button"
                      size="mini"
                      primary
                      icon={importButtonIcon}
                      content={importButtonText}
                      onClick={() => importParentFiles()}
                      disabled={isFileImportInProgress}
                      loading={isFileImportInProgress}
                    />
                  </div>
                  <p className="display-inline-block mt-5">
                    <Icon name="info circle" />
                    {i18next.t("You can import files from the previous version.")}
                  </p>
                </Message>
              </Grid.Column>
            </Grid.Row>
          )}
        </Overridable>
        <Overridable
          id="ReactInvenioDeposit.FileUploader.FileUploaderArea.container"
          filesList={filesList}
          filesLocked={lockFileUploader}
          filesEnabled={filesEnabled}
          deleteFile={deleteFile}
          decimalSizeDisplay={decimalSizeDisplay}
          uppy={uppy}
          {...uiProps}
        >
          {filesEnabled && (
            <Grid.Row stretched className="pt-0 pb-0">
              <Grid.Column width={16}>
                {filesList.length !== 0 && (
                  <Grid.Column verticalAlign="middle">
                    <FilesListTable
                      filesList={filesList}
                      filesEnabled={filesEnabled}
                      filesLocked={lockFileUploader}
                      deleteFile={deleteFile}
                      decimalSizeDislay={decimalSizeDisplay}
                    />
                  </Grid.Column>
                )}
                {!(!isDraftRecord && filesLocked) && (
                  <Dashboard
                    style={{ width: "100%" }}
                    uppy={uppy}
                    id="uppy-uploader-dashboard"
                    disabled={!filesLeft || lockFileUploader}
                    // `null` means "do not display a Done button in a status bar"
                    doneButtonHandler={null}
                    note={i18next.t(
                      "File addition, removal or modification are not allowed after you have published your upload."
                    )}
                    {...defaultDashboardProps}
                    {...uiProps}
                  />
                )}
              </Grid.Column>
            </Grid.Row>
          )}
        </Overridable>
        <Overridable
          id="ReactInvenioDeposit.FileUploader.NewVersionButton.container"
          isDraftRecord={isDraftRecord}
          draft={formikDraft}
          filesLocked={lockFileUploader}
          permissions={permissions}
          record={record}
          {...uiProps}
        >
          {!isDraftRecord && filesLocked && (
            <Grid.Row className="file-upload-note pt-5">
              <Grid.Column width={16}>
                <Message info>
                  <NewVersionButton
                    record={record}
                    onError={() => {}}
                    className="right-floated"
                    disabled={!permissions.can_new_version}
                  />
                  <p className="mt-5 display-inline-block">
                    <Icon name="info circle" size="large" />
                    {i18next.t(
                      "You must create a new version to add, modify or delete files."
                    )}
                  </p>
                </Message>
              </Grid.Column>
            </Grid.Row>
          )}
        </Overridable>
      </Grid>
    </Overridable>
  );
};

const fileDetailsShape = PropTypes.objectOf(
  PropTypes.shape({
    name: PropTypes.string,
    size: PropTypes.number,
    progressPercentage: PropTypes.number,
    checksum: PropTypes.string,
    links: PropTypes.object,
    cancelUploadFn: PropTypes.func,
    state: PropTypes.oneOf(Object.values(UploadState)),
    enabled: PropTypes.bool,
  })
);

UppyUploaderComponent.propTypes = {
  config: PropTypes.object,
  files: fileDetailsShape,
  fileUploadConcurrency: PropTypes.number,
  isDraftRecord: PropTypes.bool,
  hasParentRecord: PropTypes.bool,
  quota: PropTypes.shape({
    maxStorage: PropTypes.number,
    maxFiles: PropTypes.number,
  }),
  record: PropTypes.object,
  importButtonIcon: PropTypes.string,
  importButtonText: PropTypes.string,
  isFileImportInProgress: PropTypes.bool,
  importParentFiles: PropTypes.func.isRequired,
  initializeFileUpload: PropTypes.func.isRequired,
  finalizeUpload: PropTypes.func.isRequired,
  uploadPart: PropTypes.func.isRequired,
  setUploadProgress: PropTypes.func.isRequired,
  saveAndFetchDraft: PropTypes.func.isRequired,
  deleteFile: PropTypes.func.isRequired,
  decimalSizeDisplay: PropTypes.bool,
  filesLocked: PropTypes.bool,
  permissions: PropTypes.object,
  allowEmptyFiles: PropTypes.bool,
};

UppyUploaderComponent.defaultProps = {
  permissions: undefined,
  config: undefined,
  files: undefined,
  fileUploadConcurrency: 3,
  record: undefined,
  isFileImportInProgress: false,
  isDraftRecord: true,
  hasParentRecord: false,
  quota: {
    maxFiles: 5,
    maxStorage: 10 ** 10,
  },
  importButtonIcon: "sync",
  importButtonText: i18next.t("Import files"),
  decimalSizeDisplay: true,
  filesLocked: false,
  allowEmptyFiles: true,
};
