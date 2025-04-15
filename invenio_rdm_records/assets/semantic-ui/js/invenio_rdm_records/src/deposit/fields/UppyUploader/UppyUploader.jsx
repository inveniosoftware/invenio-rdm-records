// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";

import Uppy from "@uppy/core";
import { Dashboard } from "@uppy/react";
import ImageEditor from '@uppy/image-editor';

import { useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import { Grid, Message, Icon, Button } from "semantic-ui-react";
import Overridable from "react-overridable";
import InvenioMultipartUploader from "./InvenioMultipartUploader";
import InvenioFilesProvider from "./InvenioFilesProvider";
import { NewVersionButton } from "../../controls/NewVersionButton";
import { i18next } from "@translations/invenio_rdm_records/i18next";

import {
  useFilesList,
  FilesListTable,
  FileUploaderToolbar,
} from "../FileUploader";
import { useUppyLocale } from "./locale";

const defaultDashboardProps = {
  showRemoveButtonAfterComplete: false,
  showLinkToFileUploadResult: true,
  proudlyDisplayPoweredByUppy: false,
  hideProgressAfterFinish: true,
  hidePauseResumeButton: true,
  disableLocalFiles: false,
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
  uploadFiles,
  initializeFileUpload,
  finalizeUpload,
  deleteFile,
  getUploadParams,
  saveAndFetchDraft,
  importParentFiles,
  importButtonIcon,
  importButtonText,
  isFileImportInProgress,
  decimalSizeDisplay,
  filesLocked,
  allowEmptyFiles,
  ...uiProps
}) => {
  // We extract the working copy of the draft stored as `values` in formik
  const { values: formikDraft} = useFormikContext();
  const { filesList } = useFilesList(files);
  const locale = useUppyLocale();
  const filesEnabled = _get(formikDraft, "files.enabled", false);
  const filesSize = filesList.reduce((totalSize, file) => (totalSize += file.size), 0);
  const lockFileUploader = !isDraftRecord && filesLocked;
  const filesLeft = filesList.length < quota.maxFiles;
  const displayImportBtn =
    filesEnabled && isDraftRecord && hasParentRecord && !filesList.length;

  const restrictions = {
    minFileSize: allowEmptyFiles ? 0 : 1,
    maxNumberOfFiles: quota.maxFiles - filesList.length,
    maxTotalFileSize: quota.maxStorage - filesSize,
  };

  const [uppy] = useState(
    () =>
      new Uppy({
        debug: true,
        autoProceed: false,
        restrictions,
        locale,
      }).use(InvenioMultipartUploader, {
        // Bind Redux file actions to the uploader plugin
        draftRecord: formikDraft,
        initializeFileUpload,
        finalizeUpload,
        saveAndFetchDraft,
        getUploadParams,
        abortUpload: (file, uploadId) =>
          deleteFile(file, { params: { uploadId } }),
        // Calculate & verify checksum for every uploaded part
        // TODO: this feature currently computes part checksums,
        // but S3 presign url don't like it when Content-MD5 header is added
        // *after* their creation. PUT request with this added header
        // results in HTTP 400 Bad Request. Needs more investigation.
        checkPartIntegrity: false,
      })
      .use(ImageEditor)
  );

  // TODO: this is a WIP to provide users with possibility
  // to manually pick which individual files do they want to import from a record.
  if (displayImportBtn) {
    if (!uppy.getPlugin("InvenioFilesProvider")) {
      uppy.use(InvenioFilesProvider, { files });
    }
  }

  React.useEffect(() => {
    uppy.setOptions({
      locale
    });
  }, [uppy, locale]);

  React.useEffect(() => {
    uppy.setOptions({
      restrictions
    });
  }, [restrictions]);

  React.useEffect(() => {
    const dashboardPlugin = uppy.getPlugin("uppy-uploader-dashboard");
    if (!dashboardPlugin) return;
    dashboardPlugin.setOptions({
      disabled: !filesLeft,
    });
  }, [uppy, filesLeft]);

  // TODO: this hook-based approach to sync with uppy state could be used after React>=v18 upgrade
  // const filesList = useUppyState(uppy, (state) => state.files);
  // const totalProgress = useUppyState(uppy, (state) => state.totalProgress);
  return (
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
              <Dashboard
                style={{ width: "100%" }}
                uppy={uppy}
                id="uppy-uploader-dashboard"
                disabled={!filesLeft}
                // `null` means "do not display a Done button in a status bar"
                doneButtonHandler={null}
                // metaFields={metaFields}
                note={i18next.t(
                  "File addition, removal or modification are not allowed after you have published your upload."
                )}
                {...defaultDashboardProps}
                {...uiProps}
              />
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
        {(!isDraftRecord && filesLocked) && (
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
    state: PropTypes.any, // PropTypes.oneOf(Object.values(UploadState)), can't reach UploadState from here
    enabled: PropTypes.bool,
  })
);

UppyUploaderComponent.propTypes = {
  config: PropTypes.object,
  dragText: PropTypes.string,
  files: fileDetailsShape,
  isDraftRecord: PropTypes.bool,
  hasParentRecord: PropTypes.bool,
  quota: PropTypes.shape({
    maxStorage: PropTypes.number,
    maxFiles: PropTypes.number,
  }),
  record: PropTypes.object,
  uploadButtonIcon: PropTypes.string,
  uploadButtonText: PropTypes.string,
  importButtonIcon: PropTypes.string,
  importButtonText: PropTypes.string,
  isFileImportInProgress: PropTypes.bool,
  importParentFiles: PropTypes.func.isRequired,
  initializeFileUpload: PropTypes.func.isRequired,
  uploadFile: PropTypes.func.isRequired,
  uploadFiles: PropTypes.func.isRequired,
  finalizeUpload: PropTypes.func.isRequired,
  getUploadParams: PropTypes.func.isRequired,
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
  record: undefined,
  isFileImportInProgress: false,
  // dragText: i18next.t("Drag and drop files"),
  isDraftRecord: true,
  hasParentRecord: false,
  quota: {
    maxFiles: 5,
    maxStorage: 10 ** 10,
  },
  uploadButtonIcon: "upload",
  // uploadButtonText: i18next.t("Upload files"),
  importButtonIcon: "sync",
  // importButtonText: i18next.t("Import files"),
  decimalSizeDisplay: true,
  filesLocked: false,
  allowEmptyFiles: true,
};
