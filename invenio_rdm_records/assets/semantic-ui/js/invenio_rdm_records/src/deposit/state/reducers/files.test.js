/*
 * SPDX-FileCopyrightText: 2025 CESNET.
 * SPDX-License-Identifier: MIT
 */

import fileReducer, { UploadState } from "./files";
import {
  FILE_DELETED_SUCCESS,
  FILE_UPLOAD_FAILED,
  FILE_UPLOAD_IN_PROGRESS,
} from "../types";

const uploadingState = {
  entries: {
    "test.txt": {
      name: "test.txt",
      size: 1024,
      progressPercentage: 42,
      status: UploadState.uploading,
    },
  },
  isFileUploadInProgress: true,
};

describe("files reducer", () => {
  it("marks a failed upload", () => {
    const state = fileReducer(uploadingState, {
      type: FILE_UPLOAD_FAILED,
      payload: { filename: "test.txt" },
    });

    expect(state.entries["test.txt"].status).toEqual(UploadState.failed);
    expect(state.isFileUploadInProgress).toBe(false);
  });

  it("removes a deleted upload", () => {
    const state = fileReducer(uploadingState, {
      type: FILE_DELETED_SUCCESS,
      payload: { filename: "test.txt" },
    });

    expect(state.entries).toEqual({});
  });

  it.each([FILE_UPLOAD_IN_PROGRESS, FILE_UPLOAD_FAILED])(
    "ignores a %s update of an already deleted upload",
    (type) => {
      const deletedState = { entries: {}, isFileUploadInProgress: false };

      const state = fileReducer(deletedState, {
        type,
        payload: { filename: "test.txt", percent: 50 },
      });

      expect(state).toBe(deletedState);
    }
  );
});
