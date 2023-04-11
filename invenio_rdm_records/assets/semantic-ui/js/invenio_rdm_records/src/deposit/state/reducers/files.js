// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  FILE_DELETED_SUCCESS,
  FILE_DELETE_FAILED,
  FILE_IMPORT_FAILED,
  FILE_IMPORT_STARTED,
  FILE_IMPORT_SUCCESS,
  FILE_UPLOAD_ADDED,
  FILE_UPLOAD_CANCELLED,
  FILE_UPLOAD_FAILED,
  FILE_UPLOAD_FINISHED,
  FILE_UPLOAD_IN_PROGRESS,
  FILE_UPLOAD_SAVE_DRAFT_FAILED,
  FILE_UPLOAD_SET_CANCEL_FUNCTION,
} from "../types";

export const UploadState = {
  // initial: 'initial', // no file or the initial file selected
  uploading: "uploading", // currently uploading a file from the UI
  error: "error", // upload failed
  finished: "finished", // upload finished (uploaded file is the field's current file)
  pending: "pending", // files retrieved from the backend are in pending state
};

const initialState = {};

const fileReducer = (state = initialState, action) => {
  let newState;
  // Filename needs to be normalised due to encoding differences between client and server.
  const remoteFileName = action.payload?.filename?.normalize() ?? "";
  switch (action.type) {
    case FILE_UPLOAD_ADDED:
      return {
        ...state,
        entries: {
          ...state.entries,
          [remoteFileName]: {
            progressPercentage: 0,
            name: remoteFileName,
            size: 0,
            status: UploadState.pending,
            checksum: null,
            links: null,
            cancelUploadFn: null,
          },
        },
        actionState: action.type,
      };
    case FILE_UPLOAD_IN_PROGRESS:
      return {
        ...state,
        entries: {
          ...state.entries,
          [remoteFileName]: {
            ...state.entries[remoteFileName],
            progressPercentage: action.payload.percent,
            status: UploadState.uploading,
          },
        },
        isFileUploadInProgress: true,
        actionState: action.type,
      };
    case FILE_UPLOAD_FINISHED:
      newState = {
        ...state,
        entries: {
          ...state.entries,
          [remoteFileName]: {
            ...state.entries[remoteFileName],
            status: UploadState.finished,
            size: action.payload.size,
            progressPercentage: 100,
            checksum: action.payload.checksum,
            links: action.payload.links,
            cancelUploadFn: null,
          },
        },
      };
      return {
        ...newState,
        isFileUploadInProgress: Object.values(newState.entries).some(
          (value) => value.status === UploadState.uploading
        ),
        actionState: action.type,
      };
    case FILE_UPLOAD_SAVE_DRAFT_FAILED:
      return {
        ...state,
        errors: { ...action.payload.errors },
        actionState: action.type,
      };
    case FILE_UPLOAD_FAILED:
      newState = {
        ...state,
        entries: {
          ...state.entries,
          [remoteFileName]: {
            ...state.entries[remoteFileName],
            status: UploadState.error,
            cancelUploadFn: null,
          },
        },
      };
      return {
        ...newState,
        isFileUploadInProgress: Object.values(newState.entries).some(
          (value) => value.status === UploadState.uploading
        ),
        actionState: action.type,
      };
    case FILE_UPLOAD_SET_CANCEL_FUNCTION:
      return {
        ...state,
        entries: {
          ...state.entries,
          [remoteFileName]: {
            ...state.entries[remoteFileName],
            cancelUploadFn: action.payload.cancelUploadFn,
          },
        },
        actionState: action.type,
      };
    case FILE_UPLOAD_CANCELLED: {
      // eslint-disable-next-line no-unused-vars
      const { [remoteFileName]: cancelledFile, ...afterCancellationEntriesState } =
        state.entries;
      return {
        ...state,
        entries: {
          ...afterCancellationEntriesState,
        },
        isFileUploadInProgress: Object.values(afterCancellationEntriesState).some(
          (value) => value.status === UploadState.uploading
        ),
        actionState: action.type,
      };
    }
    case FILE_DELETED_SUCCESS: {
      // eslint-disable-next-line no-unused-vars
      const { [remoteFileName]: deletedFile, ...afterDeletionEntriesState } =
        state.entries;
      return {
        ...state,
        entries: { ...afterDeletionEntriesState },
        isFileUploadInProgress: Object.values(afterDeletionEntriesState).some(
          (value) => value.status === UploadState.uploading
        ),
        actionState: action.type,
      };
    }
    case FILE_DELETE_FAILED:
      return {
        ...state,
        actionState: action.type,
      };
    case FILE_IMPORT_STARTED:
      return {
        ...state,
        isFileImportInProgress: true,
        actionState: action.type,
      };
    case FILE_IMPORT_SUCCESS:
      return {
        ...state,
        entries: { ...action.payload.files },
        isFileImportInProgress: false,
        actionState: action.type,
      };
    case FILE_IMPORT_FAILED:
      return {
        ...state,
        isFileImportInProgress: false,
        actionState: action.type,
      };
    default:
      return state;
  }
};

export default fileReducer;
