// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2025 CESNET.
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

export const saveAndFetchDraft = (draft) => {
  return async (dispatch, _, config) => {
    try {
      const response = await saveDraftWithUrlUpdate(draft, config.service.drafts);
      // update state with created draft
      dispatch({
        type: DRAFT_FETCHED,
        payload: { data: response.data },
      });
      return response.data;
    } catch (error) {
      console.error("Error saving a draft record", error, draft);
      dispatch({
        type: FILE_UPLOAD_SAVE_DRAFT_FAILED,
        payload: { errors: error.errors },
      });
      throw error;
    }
  };
};

export const uploadFile = (draft, file, uploadUrl) => {
  return async (dispatch, _, config) => {
    try {
      config.service.files.upload(uploadUrl, file);
    } catch (error) {
      console.error("Error uploading file", error, draft, file);
      dispatch({
        type: FILE_UPLOAD_FAILED,
        payload: { errors: error.errors, payload: { filename: file.name } },
      });
      throw error;
    }
  };
};

export const uploadFiles = (draft, files) => {
  return async (dispatch, _, config) => {
    try {
      const savedDraft = await dispatch(saveAndFetchDraft(draft));

      // upload files
      const uploadFileUrl = savedDraft.links.files;
      for (const file of files) {
        dispatch(uploadFile(draft, file, uploadFileUrl));
      }
    } catch (error) {
      console.error("Error uploading files", error, draft, files);
      throw error;
    }
  };
};

export const initializeFileUpload = (draft, file) => {
  return async (dispatch, _, config) => {
    try {
      dispatch({
        type: FILE_UPLOAD_ADDED,
        payload: {
          filename: file.name,
        },
      });
      return await config.service.files.initializeUpload(draft.links.files, file);
    } catch (error) {
      const axiosError = error?.t0 && error.t0.isAxiosError ? error.t0 : error;

      console.error("Error uploading file", axiosError, draft, file);
      dispatch({ type: FILE_UPLOAD_FAILED, payload: { filename: file.name } });

      const errorMessage =
        axiosError?.response?.data?.message || axiosError?.message || "Upload failed";
      throw new Error(errorMessage);
    }
  };
};

export const uploadPart = (uploadParams) => {
  return async (dispatch, _, config) => {
    return config.service.files.uploadPart(uploadParams);
  };
};

export const finalizeUpload = (commitFileUrl, file) => {
  return async (dispatch, _, config) => {
    try {
      const response = await config.service.files.finalizeUpload(commitFileUrl, file);
      const { key: filename, size, checksum, links, ...extraData } = response;
      dispatch({
        type: FILE_UPLOAD_FINISHED,
        payload: {
          filename,
          size,
          checksum,
          links,
          extraData,
        },
      });
      return response;
    } catch (error) {
      console.error("Error uploading file", error, file);
      dispatch({ type: FILE_UPLOAD_FAILED, payload: { filename: file.name } });
      throw error;
    }
  };
};

export const deleteFile = (file) => {
  return async (dispatch, _, config) => {
    try {
      const fileLinks = file.meta?.links || file.links;
      await config.service.files.delete(fileLinks);

      dispatch({
        type: FILE_DELETED_SUCCESS,
        payload: {
          filename: file.name,
        },
      });
    } catch (error) {
      if (
        error.response?.status === 404 &&
        (file.uploadState?.isPending || !file.progress?.uploadComplete)
      ) {
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

export const setUploadProgress = (file, percent) => {
  return async (dispatch, getState, config) => {
    await config.service.files.progressNotifier.onUploadProgress(file.name, percent);
  };
};
