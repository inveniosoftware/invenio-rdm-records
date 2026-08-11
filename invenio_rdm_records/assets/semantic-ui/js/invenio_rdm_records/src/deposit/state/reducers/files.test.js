/*
 * SPDX-FileCopyrightText: 2025 CESNET.
 * SPDX-License-Identifier: MIT
 */

import fileReducer, { UploadState } from "./files";
import {
  FILE_DELETED_SUCCESS,
  FILE_DELETE_FAILED,
  FILE_DELETE_STARTED,
  FILE_UPLOAD_FAILED,
  FILE_UPLOAD_FINISHED,
  FILE_UPLOAD_INITIALIZED,
  FILE_UPLOAD_IN_PROGRESS,
  FILE_UPLOAD_SET_CANCEL_FUNCTION,
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

  it.each([
    FILE_UPLOAD_INITIALIZED,
    FILE_UPLOAD_IN_PROGRESS,
    FILE_UPLOAD_FINISHED,
    FILE_UPLOAD_FAILED,
    FILE_UPLOAD_SET_CANCEL_FUNCTION,
  ])("ignores a %s update of an already deleted upload", (type) => {
    const deletedState = { entries: {}, isFileUploadInProgress: false };

    const state = fileReducer(deletedState, {
      type,
      payload: { filename: "test.txt", percent: 50, size: 1024, links: {} },
    });

    expect(state).toBe(deletedState);
  });

  describe("pending deletions", () => {
    it("counts a started deletion", () => {
      const state = fileReducer(uploadingState, { type: FILE_DELETE_STARTED });

      expect(state.pendingDeletions).toBe(1);
    });

    it.each([FILE_DELETED_SUCCESS, FILE_DELETE_FAILED])(
      "stops counting a deletion settled with %s",
      (type) => {
        const state = fileReducer(
          { ...uploadingState, pendingDeletions: 2 },
          { type, payload: { filename: "test.txt" } }
        );

        expect(state.pendingDeletions).toBe(1);
      }
    );
  });
});
