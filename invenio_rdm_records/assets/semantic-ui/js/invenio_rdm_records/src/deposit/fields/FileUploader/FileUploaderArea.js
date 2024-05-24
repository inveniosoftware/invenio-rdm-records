// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2024 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2022 Graz University of Technology.
// Copyright (C)      2022 TU Wien.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React, { Component, useState } from "react";
import Dropzone from "react-dropzone";
import {
  Button,
  Checkbox,
  Grid,
  Header,
  Icon,
  Popup,
  Progress,
  Segment,
  Table,
} from "semantic-ui-react";
import { humanReadableBytes } from "react-invenio-forms";

const FileTableHeader = ({ filesLocked }) => (
  <Table.Header>
    <Table.Row>
      <Table.HeaderCell>
        {i18next.t("Preview")}{" "}
        <Popup
          content="Set the default preview"
          trigger={<Icon fitted name="help circle" size="small" />}
        />
      </Table.HeaderCell>
      <Table.HeaderCell>{i18next.t("Filename")}</Table.HeaderCell>
      <Table.HeaderCell>{i18next.t("Size")}</Table.HeaderCell>
      {!filesLocked && (
        <Table.HeaderCell textAlign="center">{i18next.t("Progress")}</Table.HeaderCell>
      )}
      {!filesLocked && <Table.HeaderCell />}
    </Table.Row>
  </Table.Header>
);

FileTableHeader.propTypes = {
  filesLocked: PropTypes.bool,
};

FileTableHeader.defaultProps = {
  filesLocked: false,
};

const FileTableRow = ({
  filesLocked,
  file,
  deleteFile,
  defaultPreview,
  setDefaultPreview,
  decimalSizeDisplay,
}) => {
  const [isCancelling, setIsCancelling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const isDefaultPreview = defaultPreview === file.name;

  const handleDelete = async (file) => {
    setIsDeleting(true);
    try {
      await deleteFile(file);
      if (isDefaultPreview) {
        setDefaultPreview("");
      }
    } catch (error) {
      setIsDeleting(false);
      console.error(error);
    }
  };

  const handleCancelUpload = (file) => {
    setIsCancelling(true);
    file.cancelUploadFn();
  };

  return (
    <Table.Row key={file.name}>
      <Table.Cell data-label={i18next.t("Default preview")} width={2}>
        {/* TODO: Investigate if react-deposit-forms optimized Checkbox field
                  would be more performant */}
        <Checkbox
          checked={isDefaultPreview}
          onChange={() => setDefaultPreview(isDefaultPreview ? "" : file.name)}
        />
      </Table.Cell>
      <Table.Cell data-label={i18next.t("Filename")} width={10}>
        <div>
          {file.uploadState.isPending ? (
            <div>{file.name}</div>
          ) : (
            <a
              href={_get(file, "links.content", "")}
              target="_blank"
              rel="noopener noreferrer"
              className="mr-5 text-break"
            >
              {file.name}
            </a>
          )}
          <br />
          {file.checksum && (
            <div className="ui text-muted">
              <span style={{ fontSize: "10px" }}>{file.checksum}</span>{" "}
              <Popup
                content={i18next.t(
                  "This is the file fingerprint (MD5 checksum), which can be used to verify the file integrity."
                )}
                trigger={<Icon fitted name="help circle" size="small" />}
                position="top center"
              />
            </div>
          )}
        </div>
      </Table.Cell>
      <Table.Cell data-label={i18next.t("Size")} width={2}>
        {file.size ? humanReadableBytes(file.size, decimalSizeDisplay) : ""}
      </Table.Cell>
      {!filesLocked && (
        <Table.Cell
          className="file-upload-pending"
          data-label={i18next.t("Progress")}
          width={2}
        >
          {!file.uploadState?.isPending && (
            <Progress
              className="file-upload-progress primary"
              percent={file.progressPercentage}
              error={file.uploadState.isFailed}
              size="medium"
              progress
              autoSuccess
              active
            />
          )}
          {file.uploadState?.isPending && <span>{i18next.t("Pending")}</span>}
        </Table.Cell>
      )}
      {!filesLocked && (
        <Table.Cell textAlign="right" width={2}>
          {(file.uploadState?.isFinished ||
            file.uploadState?.isFailed ||
            file.uploadState?.isPending) &&
            (isDeleting ? (
              <Icon loading name="spinner" />
            ) : (
              <Icon
                link
                className="action primary"
                name="trash alternate outline"
                disabled={isDeleting}
                onClick={() => handleDelete(file)}
                aria-label={i18next.t("Delete file")}
                title={i18next.t("Delete file")}
              />
            ))}
          {file.uploadState?.isUploading && (
            <Button
              compact
              type="button"
              negative
              size="tiny"
              disabled={isCancelling}
              onClick={() => handleCancelUpload(file)}
            >
              {isCancelling ? <Icon loading name="spinner" /> : i18next.t("Cancel")}
            </Button>
          )}
        </Table.Cell>
      )}
    </Table.Row>
  );
};

FileTableRow.propTypes = {
  filesLocked: PropTypes.bool,
  file: PropTypes.object,
  deleteFile: PropTypes.func.isRequired,
  defaultPreview: PropTypes.string,
  setDefaultPreview: PropTypes.func.isRequired,
  decimalSizeDisplay: PropTypes.bool,
};

FileTableRow.defaultProps = {
  filesLocked: false,
  file: undefined,
  defaultPreview: undefined,
  decimalSizeDisplay: false,
};

const FileUploadBox = ({
  filesLocked,
  filesList,
  dragText,
  uploadButtonIcon,
  uploadButtonText,
  openFileDialog,
}) =>
  !filesLocked && (
    <Segment
      basic
      padded="very"
      className={filesList.length ? "file-upload-area" : "file-upload-area no-files"}
    >
      <Grid columns={3} textAlign="center">
        <Grid.Row verticalAlign="middle">
          <Grid.Column mobile={16} tablet={7} computer={7}>
            <Header size="small">{dragText}</Header>
          </Grid.Column>

          <Grid.Column className="mt-10 mb-10" mobile={16} tablet={2} computer={2}>
            - {i18next.t("or")} -
          </Grid.Column>

          <Grid.Column mobile={16} tablet={7} computer={7}>
            <Button
              type="button"
              primary
              labelPosition="left"
              icon={uploadButtonIcon}
              content={uploadButtonText}
              onClick={() => openFileDialog()}
              disabled={openFileDialog === null}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Segment>
  );

FileUploadBox.propTypes = {
  filesLocked: PropTypes.bool.isRequired,
  filesList: PropTypes.array,
  dragText: PropTypes.string,
  uploadButtonIcon: PropTypes.node,
  uploadButtonText: PropTypes.string,
  openFileDialog: PropTypes.func,
};

FileUploadBox.defaultProps = {
  filesList: undefined,
  dragText: undefined,
  uploadButtonIcon: undefined,
  uploadButtonText: undefined,
  openFileDialog: null,
};

const FilesListTable = ({ filesLocked, filesList, deleteFile, decimalSizeDisplay }) => {
  const { setFieldValue, values: formikDraft } = useFormikContext();
  const defaultPreview = _get(formikDraft, "files.default_preview", "");
  return (
    <Table>
      <FileTableHeader filesLocked={filesLocked} />
      <Table.Body>
        {filesList.map((file) => {
          return (
            <FileTableRow
              key={file.name}
              filesLocked={filesLocked}
              file={file}
              deleteFile={deleteFile}
              defaultPreview={defaultPreview}
              setDefaultPreview={(filename) =>
                setFieldValue("files.default_preview", filename)
              }
              decimalSizeDisplay={decimalSizeDisplay}
            />
          );
        })}
      </Table.Body>
    </Table>
  );
};

FilesListTable.propTypes = {
  filesLocked: PropTypes.bool,
  filesList: PropTypes.array,
  deleteFile: PropTypes.func,
  decimalSizeDisplay: PropTypes.bool,
};

FilesListTable.defaultProps = {
  filesLocked: undefined,
  filesList: undefined,
  deleteFile: undefined,
  decimalSizeDisplay: undefined,
};

export class FileUploaderArea extends Component {
  render() {
    const { filesEnabled, dropzoneParams, filesList } = this.props;
    return filesEnabled ? (
      <Dropzone {...dropzoneParams}>
        {({ getRootProps, getInputProps, open: openFileDialog }) => (
          <Grid.Column width={16}>
            <span {...getRootProps()}>
              <input {...getInputProps()} />
              {filesList.length !== 0 && (
                <Grid.Column verticalAlign="middle">
                  <FilesListTable {...this.props} />
                </Grid.Column>
              )}
              <FileUploadBox {...this.props} openFileDialog={openFileDialog} />
            </span>
          </Grid.Column>
        )}
      </Dropzone>
    ) : (
      <Grid.Column width={16}>
        <Segment basic padded="very" className="file-upload-area no-files">
          <Grid textAlign="center">
            <Grid.Row verticalAlign="middle">
              <Grid.Column>
                <Header size="medium">
                  {i18next.t("This is a Metadata-only record.")}
                </Header>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Segment>
      </Grid.Column>
    );
  }
}

FileUploaderArea.propTypes = {
  deleteFile: PropTypes.func,
  dragText: PropTypes.string,
  dropzoneParams: PropTypes.object,
  filesEnabled: PropTypes.bool.isRequired,
  filesList: PropTypes.array,
  filesLocked: PropTypes.bool,
  links: PropTypes.object,
  setDefaultPreviewFile: PropTypes.func,
  uploadButtonIcon: PropTypes.string,
  uploadButtonText: PropTypes.string,
  decimalSizeDisplay: PropTypes.bool,
};

FileUploaderArea.defaultProps = {
  deleteFile: undefined,
  dragText: undefined,
  dropzoneParams: undefined,
  filesList: undefined,
  filesLocked: false,
  links: undefined,
  setDefaultPreviewFile: undefined,
  uploadButtonIcon: undefined,
  uploadButtonText: undefined,
  decimalSizeDisplay: undefined,
};
