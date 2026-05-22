/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { connect } from "react-redux";
import { deleteFile, importParentFiles, uploadFiles } from "../../state/actions";
import { FileUploaderComponent } from "./FileUploader";
import { showHideOverridable } from "react-invenio-forms";

const mapStateToProps = (state) => {
  const { links, entries } = state.files;
  return {
    files: entries,
    links,
    record: state.deposit.record,
    config: state.deposit.config,
    permissions: state.deposit.permissions,
    isFileImportInProgress: state.files.isFileImportInProgress,
    hasParentRecord: Boolean(
      state.deposit.record?.versions?.index && state.deposit.record?.versions?.index > 1
    ),
  };
};

const mapDispatchToProps = (dispatch) => ({
  uploadFiles: (draft, files) => dispatch(uploadFiles(draft, files)),
  importParentFiles: () => dispatch(importParentFiles()),
  deleteFile: (file) => dispatch(deleteFile(file)),
});

export const FileUploader = connect(
  mapStateToProps,
  mapDispatchToProps
)(
  showHideOverridable(
    "InvenioRdmRecords.DepositForm.FileUploader",
    FileUploaderComponent
  )
);

export { FileUploaderArea, FilesListTable } from "./FileUploaderArea";
export { FileUploaderToolbar } from "./FileUploaderToolbar";
export { getFilesList } from "./utils";
