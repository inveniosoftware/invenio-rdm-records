// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  DRAFT_FETCHED,
  FILE_DELETED_SUCCESS,
  FILE_DELETE_FAILED,
  FILE_IMPORT_FAILED,
  FILE_IMPORT_STARTED,
  FILE_IMPORT_SUCCESS,
  FILE_UPLOAD_SAVE_DRAFT_FAILED,
  FILE_UPLOAD_ADDED,
  FILE_UPLOAD_FINISHED,
  FILE_UPLOAD_FAILED,
} from "../types";
import { saveDraftWithUrlUpdate } from "./deposit";

export const uploadFiles = (draft, files) => {
  return async (dispatch, _, config) => {
    const savedDraft = await _fileUploadSaveDraft(
      dispatch,
      draft,
      config.service.drafts
    );

    // upload files
    const uploadFileUrl = savedDraft.data.links.files;
    for (const file of files) {
      dispatch(uploadFile(draft, file, uploadFileUrl));
    }
  };
};

export const finalizeUpload = (commitFileUrl, file) => {
  return async (dispatch, _, config) => {
    try {
      const response = await config.service.files.finalizeUpload(commitFileUrl, file);
      dispatch({
        type: FILE_UPLOAD_FINISHED,
        payload: {
          filename: file.name,
          size: response.size,
          checksum: response.checksum,
          links: response.links,
        },
      });
      return response;
    } catch (error) {
      dispatch({ type: FILE_UPLOAD_FAILED, payload: { filename: file.name } });
      throw error;
    }
  };
};

const _fileUploadSaveDraft = async (dispatch, draft, draftService) => {
  const response = await saveDraftWithUrlUpdate(draft, draftService);
  // update state with created draft
  dispatch({
    type: DRAFT_FETCHED,
    payload: { data: response.data },
  });
  return response;
};

export const initializeFileUpload = (draft, file) => {
  return async (dispatch, _, config) => {
    try {
      const savedDraft = await _fileUploadSaveDraft(
        dispatch,
        draft,
        config.service.drafts
      );
      const uploadFileUrl = savedDraft.data.links.files;
      const initializedFileMetadata = await config.service.files.initializeUpload(
        uploadFileUrl,
        file
      );
      dispatch({
        type: FILE_UPLOAD_ADDED,
        payload: {
          filename: file.name,
        },
      });
      return initializedFileMetadata;
    } catch (error) {
      console.error("Error uploading files", error, draft, file);
      dispatch({ type: FILE_UPLOAD_FAILED, payload: { filename: file.name } });
      throw error;
    }
  };
};

export const uploadFile = (draft, file, uploadUrl) => {
  return async (dispatch, _, config) => {
    let uploadFileUrl;
    try {
      console.log("uf", uploadUrl);
      config.service.files.upload(uploadUrl, file);
    } catch (error) {
      console.error("Error uploading files", error, draft, file);
      dispatch({
        type: FILE_UPLOAD_SAVE_DRAFT_FAILED,
        payload: { errors: error.errors },
      });
    }
  };
};

export const deleteFile = (file) => {
  return async (dispatch, _, config) => {
    try {
      const fileLinks = file.links;
      await config.service.files.delete(fileLinks);

      dispatch({
        type: FILE_DELETED_SUCCESS,
        payload: {
          filename: file.name,
        },
      });
    } catch (error) {
      if (error.response.status === 404 && file.uploadState?.isPending) {
        // pending file was removed from the backend thus we can remove it from the state
        dispatch({
          type: FILE_DELETED_SUCCESS,
          payload: {
            filename: file.name,
          },
        });
      } else {
        console.error("Error deleting file", error, file);
        dispatch({ type: FILE_DELETE_FAILED });
        throw error;
      }
    }
  };
};

export const importParentFiles = () => {
  return async (dispatch, getState, config) => {
    const draft = getState().deposit.record;
    if (!draft.id) return;

    dispatch({ type: FILE_IMPORT_STARTED });

    try {
      const draftLinks = draft.links;
      const files = await config.service.files.importParentRecordFiles(draftLinks);
      dispatch({
        type: FILE_IMPORT_SUCCESS,
        payload: { files: files },
      });
    } catch (error) {
      console.error("Error importing parent record files", error);
      dispatch({ type: FILE_IMPORT_FAILED });
      throw error;
    }
  };
};

export const getUploadParams = (draft, file, options) => {
  return async (dispatch, getState, config) => {
    const fileRecord = await dispatch(initializeFileUpload(draft, file));
    const params = await config.service.files.getUploadParams(
      fileRecord.links.content,
      file,
      options
    );

    return {
      ...params,
      links: fileRecord.links,
      file_id: fileRecord.file_id,
    };
  };
};
