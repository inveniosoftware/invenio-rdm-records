// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2022 Graz University of Technology.
// Copyright (C)      2022 TU Wien.
// Copyright (C)      2024 KTH Royal Institute of Technology.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import Uppy from "@uppy/core";
import { Dashboard } from "@uppy/react";
import { useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Grid } from "semantic-ui-react";
import Overridable from "react-overridable";
import { MultipartUploaderPlugin } from "./MultipartUploaderPlugin";
import {
  useFilesList,
  FilesListTable,
  FileUploaderToolbar,
} from "../FileUploader";
import { useUppyLocale } from "./locale";

const defaultDashboardProps = {
  proudlyDisplayPoweredByUppy: false,
  height: "100%",
  width: "100%",
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
  const { values: formikDraft } = useFormikContext();
  const { filesList } = useFilesList(files);
  const locale = useUppyLocale();

  const filesEnabled = _get(formikDraft, "files.enabled", false);
  const filesSize = filesList.reduce((totalSize, file) => (totalSize += file.size), 0);
  const lockFileUploader = !isDraftRecord && filesLocked;
  const filesLeft = filesList.length < quota.maxFiles;

  const restrictions = {
    minFileSize: allowEmptyFiles ? 0 : 1,
    maxNumberOfFiles: quota.maxFiles - filesList.length,
    maxTotalFileSize: quota.maxStorage - filesSize,
  };

  function checkForDuplicates(file, files) {
    console.log(files, filesList.includes(file.name), filesList, file.name);
  }

  const [uppy] = useState(
    () =>
      new Uppy({
        debug: true,
        autoProceed: true,
        restrictions,
        locale,
        onBeforeFileAdded: checkForDuplicates,
      }).use(MultipartUploaderPlugin, {
        // Bind Redux file actions to the uploader plugin
        initializeUpload: (file) => initializeFileUpload(formikDraft, file),
        finalizeUpload: (file) => finalizeUpload(file.meta.links.commit, file),
        getUploadParams: (file, options) => getUploadParams(formikDraft, file, options),
        abortUpload: (file, uploadId) =>
          deleteFile(file.links, { params: { uploadId } }),
        // Calculate & verify checksum for every uploaded part
        // TODO: this feature currently computes part checksums,
        // but S3 presign url don't like it when Content-MD5 header is added
        // *after* their creation. PUT request with this added header
        // results in HTTP 400 Bad Request. Needs more investigation.
        checkPartIntegrity: false,
      })
  );

  uppy.setOptions({ locale });

  React.useEffect(() => {
    const dashboardPlugin = uppy.getPlugin("Dashboard");
    if (!dashboardPlugin) return;
    dashboardPlugin.setOptions({
      disabled: !filesLeft,
    });
  }, [filesLeft, uppy]);

  // TODO: this hook-based approach could be used after React upgrade
  // const filesList = useUppyState(uppy, (state) => state.files);
  // const totalProgress = useUppyState(uppy, (state) => state.totalProgress);

  const displayImportBtn =
    filesEnabled && isDraftRecord && hasParentRecord && !filesList.length;
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
              <Dashboard
                style={{ width: "100%" }}
                uppy={uppy}
                id="uppy-uploader-dashboard"
                disabled={!filesLeft}
                // `null` means "do not display a Done button in a status bar"
                doneButtonHandler={null}
                {...defaultDashboardProps}
                {...uiProps}
              />
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
