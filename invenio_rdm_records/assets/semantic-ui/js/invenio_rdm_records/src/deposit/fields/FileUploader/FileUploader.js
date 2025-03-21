// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2022 Graz University of Technology.
// Copyright (C)      2022 TU Wien.
// Copyright (C)      2024 KTH Royal Institute of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { useFormikContext } from "formik";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import _map from "lodash/map";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Button, Grid, Icon, Message, Modal } from "semantic-ui-react";
import { UploadState } from "../../state/reducers/files";
import { NewVersionButton } from "../../controls/NewVersionButton";
import { FileUploaderArea } from "./FileUploaderArea";
import { FileUploaderToolbar } from "./FileUploaderToolbar";
import { humanReadableBytes } from "react-invenio-forms";
import Overridable from "react-overridable";

// NOTE: This component has to be a function component to allow
//       the `useFormikContext` hook.
export const FileUploaderComponent = ({
  config,
  files,
  isDraftRecord,
  hasParentRecord,
  quota,
  permissions,
  record,
  uploadFiles,
  deleteFile,
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
  const { values: formikDraft, errors, initialErrors } = useFormikContext();
  const hasError = (errors.files || initialErrors?.files) && files;

  const filesEnabled = _get(formikDraft, "files.enabled", false);
  const [warningMsg, setWarningMsg] = useState();
  const lockFileUploader = !isDraftRecord && filesLocked;

  const filesList = Object.values(files).map((fileState) => {
    return {
      name: fileState.name,
      size: fileState.size,
      checksum: fileState.checksum,
      links: fileState.links,
      uploadState: {
        // initial: fileState.status === UploadState.initial,
        isFailed: fileState.status === UploadState.error,
        isUploading: fileState.status === UploadState.uploading,
        isFinished: fileState.status === UploadState.finished,
        isPending: fileState.status === UploadState.pending,
      },
      progressPercentage: fileState.progressPercentage,
      cancelUploadFn: fileState.cancelUploadFn,
    };
  });

  const filesSize = filesList.reduce((totalSize, file) => (totalSize += file.size), 0);

  const dropzoneParams = {
    preventDropOnDocument: true,
    onDropAccepted: (acceptedFiles) => {
      const maxFileNumberReached =
        filesList.length + acceptedFiles.length > quota.maxFiles;
      const acceptedFilesSize = acceptedFiles.reduce(
        (totalSize, file) => (totalSize += file.size),
        0
      );
      const maxFileStorageReached = filesSize + acceptedFilesSize > quota.maxStorage;

      const filesNames = _map(filesList, "name");
      const filesNamesSet = new Set(filesNames);

      const { duplicateFiles, emptyFiles, nonEmptyFiles } = acceptedFiles.reduce(
        (accumulators, file) => {
          if (filesNamesSet.has(file.name)) {
            accumulators.duplicateFiles.push(file);
          } else if (file.size === 0) {
            accumulators.emptyFiles.push(file);
          } else {
            accumulators.nonEmptyFiles.push(file);
          }

          return accumulators;
        },
        { duplicateFiles: [], emptyFiles: [], nonEmptyFiles: [] }
      );

      const hasEmptyFiles = !_isEmpty(emptyFiles);
      const hasDuplicateFiles = !_isEmpty(duplicateFiles);

      if (maxFileNumberReached) {
        setWarningMsg(
          <div className="content">
            <Message
              warning
              icon="warning circle"
              header={i18next.t("Could not upload files.")}
              content={i18next.t(
                `Uploading the selected files would result in ${
                  filesList.length + acceptedFiles.length
                } files (max.${quota.maxFiles})`
              )}
            />
          </div>
        );
      } else if (maxFileStorageReached) {
        setWarningMsg(
          <div className="content">
            <Message
              warning
              icon="warning circle"
              header={i18next.t("Could not upload files.")}
              content={
                <>
                  {i18next.t("Uploading the selected files would result in")}{" "}
                  {humanReadableBytes(
                    filesSize + acceptedFilesSize,
                    decimalSizeDisplay
                  )}
                  {i18next.t("but the limit is")}
                  {humanReadableBytes(quota.maxStorage, decimalSizeDisplay)}.
                </>
              }
            />
          </div>
        );
      } else {
        let warnings = [];

        if (hasDuplicateFiles) {
          warnings.push(
            <Message
              warning
              icon="warning circle"
              header={i18next.t("The following files already exist")}
              list={_map(duplicateFiles, "name")}
            />
          );
        }

        if (!allowEmptyFiles && hasEmptyFiles) {
          warnings.push(
            <Message
              warning
              icon="warning circle"
              header={i18next.t("Could not upload all files.")}
              content={i18next.t("Empty files were skipped.")}
              list={_map(emptyFiles, "name")}
            />
          );
        }

        if (!_isEmpty(warnings)) {
          setWarningMsg(<div className="content">{warnings}</div>);
        }

        const filesToUpload = allowEmptyFiles
          ? [...nonEmptyFiles, ...emptyFiles]
          : nonEmptyFiles;

        // Proceed with uploading files if there are any to upload
        if (!_isEmpty(filesToUpload)) {
          uploadFiles(formikDraft, filesToUpload);
        }
      }
    },
    multiple: true,
    noClick: true,
    noKeyboard: true,
    disabled: false,
  };

  const filesLeft = filesList.length < quota.maxFiles;
  if (!filesLeft) {
    dropzoneParams["disabled"] = true;
  }

  const displayImportBtn =
    filesEnabled && isDraftRecord && hasParentRecord && !filesList.length;
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
      uploadFiles={uploadFiles}
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
      dropzoneParams={dropzoneParams}
      warningMsg={warningMsg}
      setWarningMsg={setWarningMsg}
      filesLocked={lockFileUploader}
      hasError={hasError}
      {...uiProps}
    >
      <>
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
            dropzoneParams={dropzoneParams}
            filesLocked={lockFileUploader}
            hasError={hasError}
            filesEnabled={filesEnabled}
            deleteFile={deleteFile}
            decimalSizeDisplay={decimalSizeDisplay}
            {...uiProps}
          >
            {filesEnabled && (
              <Grid.Row className="pt-0 pb-0">
                <FileUploaderArea
                  {...uiProps}
                  filesList={filesList}
                  dropzoneParams={dropzoneParams}
                  filesLocked={lockFileUploader}
                  hasError={hasError}
                  filesEnabled={filesEnabled}
                  deleteFile={deleteFile}
                  decimalSizeDisplay={decimalSizeDisplay}
                />
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
            {isDraftRecord ? (
              <Grid.Row className="file-upload-note pt-5">
                <Grid.Column width={16}>
                  <Message visible warning>
                    <p>
                      <Icon name="warning sign" />
                      {i18next.t(
                        "File addition, removal or modification are not allowed after you have published your upload."
                      )}
                    </p>
                  </Message>
                </Grid.Column>
              </Grid.Row>
            ) : (
              filesLocked && (
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
              )
            )}
          </Overridable>
        </Grid>
        <Overridable
          id="ReactInvenioDeposit.FileUploader.Modal.container"
          warningMsg={warningMsg}
          setWarningMsg={setWarningMsg}
          {...uiProps}
        >
          <Modal
            open={!!warningMsg}
            header="Warning!"
            content={warningMsg}
            onClose={() => setWarningMsg()}
            closeIcon
          />
        </Overridable>
      </>
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

FileUploaderComponent.propTypes = {
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
  uploadFiles: PropTypes.func.isRequired,
  deleteFile: PropTypes.func.isRequired,
  decimalSizeDisplay: PropTypes.bool,
  filesLocked: PropTypes.bool,
  permissions: PropTypes.object,
  allowEmptyFiles: PropTypes.bool,
};

FileUploaderComponent.defaultProps = {
  permissions: undefined,
  config: undefined,
  files: undefined,
  record: undefined,
  isFileImportInProgress: false,
  dragText: i18next.t("Drag and drop files"),
  isDraftRecord: true,
  hasParentRecord: false,
  quota: {
    maxFiles: 5,
    maxStorage: 10 ** 10,
  },
  uploadButtonIcon: "upload",
  uploadButtonText: i18next.t("Upload files"),
  importButtonIcon: "sync",
  importButtonText: i18next.t("Import files"),
  decimalSizeDisplay: true,
  filesLocked: false,
  allowEmptyFiles: true,
};
