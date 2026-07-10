/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2025 CESNET.
 * SPDX-FileCopyrightText: 2025 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import React, { useState } from "react";
import Uppy from "@uppy/core";
import { Dashboard } from "@uppy/react";
import ImageEditor from "@uppy/image-editor";
import { useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import { Button, Dimmer, Grid, Icon, Message } from "semantic-ui-react";
import Overridable from "react-overridable";
import RDMUppyUploaderPlugin from "./RDMUppyUploaderPlugin";
import { NewVersionButton } from "../../controls/NewVersionButton";
import { UploadState } from "../../state/reducers/files";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { getFilesList, FilesListTable, FileUploaderToolbar } from "../FileUploader";
import { useUppyLocale } from "./locale";
import { humanReadableBytes } from "react-invenio-forms";

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

const normalizeFileName = (name) =>
  typeof name === "string" ? name.normalize?.() ?? name : name;

const defaultOnBeforeFileAdded = (currentFile, currentFiles = {}) =>
  !Object.hasOwn(currentFiles, currentFile.id);

const createDuplicateFileChecker = (uppy, filesList) => {
  return (file, files) => {
    const normalizedName = normalizeFileName(file.name);
    if (!normalizedName) {
      return defaultOnBeforeFileAdded(file, files);
    }

    const alreadyUploaded = filesList.some((item) => {
      const existingName = normalizeFileName(item.name);
      return existingName === normalizedName && !item.uploadState.isFailed;
    });

    if (!alreadyUploaded) {
      return defaultOnBeforeFileAdded(file, files);
    }

    uppy.info(
      i18next.t("{{filename}} is already part of this upload.", {
        filename: file.name,
      }),
      "warning"
    );
    // See https://uppy.io/docs/uppy/#onbeforefileaddedfile-files
    return false;
  };
};

export const createFileValidator = (
  uppy,
  filesList,
  filesSize,
  quota,
  decimalSizeDisplay
) => {
  const duplicateFileChecker = createDuplicateFileChecker(uppy, filesList);

  return (file, files) => {
    const uppyFilesSize = Object.values(files).reduce(
      (totalSize, uppyFile) => (totalSize += uppyFile.size),
      0
    );
    const wouldBeTotalFiles = filesList.length + Object.keys(files).length + 1;
    const wouldBeTotalSize = filesSize + uppyFilesSize + file.size;

    if (wouldBeTotalFiles > quota.maxFiles) {
      uppy.info(
        i18next.t(
          "Uploading this file would result in {{total}} files (max. {{maxFiles}}).",
          {
            total: wouldBeTotalFiles,
            maxFiles: quota.maxFiles,
          }
        ),
        "warning"
      );
      return false;
    }

    if (wouldBeTotalSize > quota.maxStorage) {
      uppy.info(
        i18next.t(
          "Uploading this file would result in {{total}} of used storage (max. {{limit}}).",
          {
            total: humanReadableBytes(wouldBeTotalSize, decimalSizeDisplay),
            limit: humanReadableBytes(quota.maxStorage, decimalSizeDisplay),
          }
        ),
        "warning"
      );
      return false;
    }

    if (quota.maxFileSize && file.size > quota.maxFileSize) {
      uppy.info(
        i18next.t(
          "Uploading this file would exceed the maximum file size of {{limit}}.",
          {
            limit: humanReadableBytes(quota.maxFileSize, decimalSizeDisplay),
          }
        ),
        "warning"
      );
      return false;
    }

    return duplicateFileChecker(file, files);
  };
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
  const { filesList } = getFilesList(files ?? {});
  const hasError = (errors.files || initialErrors?.files) && files;
  const locale = useUppyLocale();
  const filesEnabled = _get(formikDraft, "files.enabled", false);
  const filesSize = filesList.reduce((totalSize, file) => (totalSize += file.size), 0);
  const lockFileUploader = !isDraftRecord && filesLocked;
  const filesLeft = filesList.length < quota.maxFiles;
  const storageLeft = filesSize < quota.maxStorage;
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
      maxNumberOfFiles: Math.max(0, quota.maxFiles - filesList.length),
      maxTotalFileSize: Math.max(0, quota.maxStorage - filesSize),
      maxFileSize: quota.maxFileSize,
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
    return () => {
      // https://uppy.io/blog/2017/05/0.16/#dom-element-in-target-option-uppyclose-for-tearing-down-an-uppy-instance
      uppy.close();
    };
  }, [uppy]);

  React.useEffect(() => {
    uppy.setOptions({ restrictions });
  }, [uppy, restrictions]);

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
    uppy.setOptions({
      onBeforeFileAdded: createFileValidator(
        uppy,
        filesList,
        filesSize,
        quota,
        decimalSizeDisplay
      ),
    });
  }, [uppy, filesList, filesSize, quota, decimalSizeDisplay]);

  const [uppyHasFiles, setUppyHasFiles] = useState(false);
  React.useEffect(() => {
    const update = () =>
      setUppyHasFiles(Object.keys(uppy.getState().files || {}).length > 0);
    uppy.on("file-added", update);
    uppy.on("file-removed", update);
    update();
    return () => {
      uppy.off("file-added", update);
      uppy.off("file-removed", update);
    };
  }, [uppy]);

  const showQuotaOverlay =
    (!filesLeft || !storageLeft) && !lockFileUploader && !uppyHasFiles;

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
                  <div
                    inert={showQuotaOverlay ? "" : undefined}
                    style={{ position: "relative", width: "100%", zIndex: 0 }}
                  >
                    <Dashboard
                      style={{ width: "100%" }}
                      uppy={uppy}
                      id="uppy-uploader-dashboard"
                      disabled={lockFileUploader}
                      // `null` means "do not display a Done button in a status bar"
                      doneButtonHandler={null}
                      note={i18next.t(
                        "File addition, removal or modification are not allowed after you have published your upload."
                      )}
                      {...defaultDashboardProps}
                      {...uiProps}
                    />
                    {showQuotaOverlay && (
                      <Dimmer active style={{ cursor: "not-allowed" }}>
                        <Message compact icon inverted>
                          <Icon name="ban" />
                          <Message.Content>
                            {i18next.t(
                              "The file quota has been reached. No more files can be uploaded."
                            )}
                          </Message.Content>
                        </Message>
                      </Dimmer>
                    )}
                  </div>
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
    maxFileSize: PropTypes.number,
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
    maxFileSize: undefined,
  },
  importButtonIcon: "sync",
  importButtonText: i18next.t("Import files"),
  decimalSizeDisplay: true,
  filesLocked: false,
  allowEmptyFiles: true,
};
