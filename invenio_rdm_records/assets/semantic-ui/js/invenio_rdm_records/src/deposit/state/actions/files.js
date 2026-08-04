/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2025 CESNET.
 * SPDX-License-Identifier: MIT
 */

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
  FILE_UPLOAD_INITIALIZED,
} from "../types";
import { saveDraftWithUrlUpdate } from "./deposit";

// Uppy files carry their links in `meta`, files list entries directly on the file
const getFileLinks = (file) => file.meta?.links || file.links;

// The backend reports files of aborted or expired uploads as no longer available
const isFileGone = (error) => [404, 410].includes(error.response?.status);

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
      const response = await config.service.files.initializeUpload(
        draft.links.files,
        file
      );
      dispatch({
        type: FILE_UPLOAD_INITIALIZED,
        payload: {
          filename: file.name,
          links: response.links,
        },
      });
      return response;
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

/**
 * Checks whether the file still exists on the backend.
 *
 * Used to tell apart upload failures that can be retried from uploads that
 * were aborted elsewhere (e.g. deleted from another browser tab).
 */
export const checkFileExists = (file) => {
  return async (dispatch, _, config) => {
    const fileLinks = getFileLinks(file);

    if (!fileLinks?.self) {
      // Upload was never initialized, so nothing exists on the backend
      return false;
    }

    try {
      await config.service.files.get(fileLinks);
      return true;
    } catch (error) {
      if (isFileGone(error)) {
        return false;
      }
      // Any other failure (e.g. a network issue) is inconclusive,
      // thus the file is assumed to still exist.
      console.error("Error fetching file", error, file);
      return true;
    }
  };
};

export const deleteFile = (file) => {
  return async (dispatch, _, config) => {
    const fileLinks = getFileLinks(file);
    const deletedSuccess = {
      type: FILE_DELETED_SUCCESS,
      payload: {
        filename: file.name,
      },
    };

    if (!fileLinks?.self) {
      // Upload initialization failed, so there is nothing to delete on the
      // backend and the file entry can be removed from the state right away.
      dispatch(deletedSuccess);
      return;
    }

    try {
      await config.service.files.delete(fileLinks);

      dispatch(deletedSuccess);
    } catch (error) {
      const isFinishedUpload =
        file.uploadState?.isFinished || (file.progress?.uploadComplete && !file.error);

      if (isFileGone(error) && !isFinishedUpload) {
        // upload that never finished was already removed from the backend
        // (e.g. aborted from another tab), thus it can be removed from the state
        dispatch(deletedSuccess);
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
