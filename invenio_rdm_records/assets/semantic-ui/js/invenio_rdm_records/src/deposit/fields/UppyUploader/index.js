// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { connect } from "react-redux";
import {
  deleteFile,
  importParentFiles,
  initializeFileUpload,
  uploadPart,
  finalizeUpload,
  saveAndFetchDraft,
  setUploadProgress,
} from "../../state/actions";
import { UppyUploaderComponent } from "./UppyUploader";

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
  initializeFileUpload: (draft, file) => dispatch(initializeFileUpload(draft, file)),
  finalizeUpload: (file) => dispatch(finalizeUpload(file.meta.links.commit, file)),
  importParentFiles: () => dispatch(importParentFiles()),
  setUploadProgress: (file, percent) => dispatch(setUploadProgress(file, percent)),
  deleteFile: (file) => dispatch(deleteFile(file)),
  uploadPart: (uploadParams) => dispatch(uploadPart(uploadParams)),
  saveAndFetchDraft: (draft) => dispatch(saveAndFetchDraft(draft)),
});

export const UppyUploader = connect(
  mapStateToProps,
  mapDispatchToProps
)(UppyUploaderComponent);
