/*
 * SPDX-FileCopyrightText: 2025 CESNET.
 * SPDX-License-Identifier: MIT
 */

import { checkFileExists, deleteFile } from "./files";
import {
  FILE_DELETED_SUCCESS,
  FILE_DELETE_FAILED,
  FILE_DELETE_STARTED,
} from "../types";

const httpError = (status) =>
  Object.assign(new Error(`Request failed with status code ${status}`), {
    response: { status },
  });

const fileLinks = { self: "/api/records/abcd-1234/draft/files/test.txt" };

let dispatch;
let filesService;
let config;

beforeEach(() => {
  dispatch = jest.fn();
  filesService = { getFileMetadata: jest.fn(), delete: jest.fn() };
  config = { service: { files: filesService } };
  jest.spyOn(console, "error").mockImplementation(() => {});
});

afterEach(() => {
  jest.restoreAllMocks();
});

const dispatchAction = (action) => action(dispatch, undefined, config);

describe("deleteFile", () => {
  const deletedSuccess = {
    type: FILE_DELETED_SUCCESS,
    payload: { filename: "test.txt" },
  };

  it("deletes an uploaded file", async () => {
    await dispatchAction(deleteFile({ name: "test.txt", links: fileLinks }));

    expect(filesService.delete).toHaveBeenCalledWith(fileLinks);
    expect(dispatch).toHaveBeenCalledWith({ type: FILE_DELETE_STARTED });
    expect(dispatch).toHaveBeenCalledWith(deletedSuccess);
  });

  it("takes the links of Uppy files from their metadata", async () => {
    await dispatchAction(deleteFile({ name: "test.txt", meta: { links: fileLinks } }));

    expect(filesService.delete).toHaveBeenCalledWith(fileLinks);
  });

  it("removes an entry of an upload that was never initialized", async () => {
    await dispatchAction(deleteFile({ name: "test.txt", links: null }));

    expect(filesService.delete).not.toHaveBeenCalled();
    expect(dispatch).toHaveBeenCalledWith(deletedSuccess);
  });

  it.each([404, 410])(
    "removes an entry of an unfinished upload that is gone (HTTP %s)",
    async (status) => {
      filesService.delete.mockRejectedValue(httpError(status));

      await dispatchAction(
        deleteFile({
          name: "test.txt",
          meta: { links: fileLinks },
          progress: { uploadComplete: false },
        })
      );

      expect(dispatch).toHaveBeenCalledWith(deletedSuccess);
    }
  );

  it("removes an entry of an upload that failed to be finalized", async () => {
    filesService.delete.mockRejectedValue(httpError(404));

    await dispatchAction(
      deleteFile({
        name: "test.txt",
        meta: { links: fileLinks },
        progress: { uploadComplete: true },
        error: "Failed to commit the upload",
      })
    );

    expect(dispatch).toHaveBeenCalledWith(deletedSuccess);
  });

  it("reports a failed deletion of a finished upload", async () => {
    filesService.delete.mockRejectedValue(httpError(404));

    await expect(
      dispatchAction(
        deleteFile({
          name: "test.txt",
          links: fileLinks,
          uploadState: { isFinished: true },
        })
      )
    ).rejects.toThrow();

    expect(dispatch).toHaveBeenCalledWith({ type: FILE_DELETE_FAILED });
    expect(dispatch).not.toHaveBeenCalledWith(deletedSuccess);
  });

  it("reports any other deletion failure", async () => {
    filesService.delete.mockRejectedValue(httpError(500));

    await expect(
      dispatchAction(
        deleteFile({
          name: "test.txt",
          meta: { links: fileLinks },
          progress: { uploadComplete: false },
        })
      )
    ).rejects.toThrow();

    expect(dispatch).toHaveBeenCalledWith({ type: FILE_DELETE_FAILED });
  });
});

describe("checkFileExists", () => {
  it("confirms an existing file", async () => {
    filesService.getFileMetadata.mockResolvedValue({ key: "test.txt" });

    await expect(
      dispatchAction(checkFileExists({ name: "test.txt", meta: { links: fileLinks } }))
    ).resolves.toBe(true);
    expect(filesService.getFileMetadata).toHaveBeenCalledWith(fileLinks);
  });

  it.each([404, 410])("detects a file that is gone (HTTP %s)", async (status) => {
    filesService.getFileMetadata.mockRejectedValue(httpError(status));

    await expect(
      dispatchAction(checkFileExists({ name: "test.txt", meta: { links: fileLinks } }))
    ).resolves.toBe(false);
  });

  it("detects a file that is not reported by the backend", async () => {
    filesService.getFileMetadata.mockResolvedValue(undefined);

    await expect(
      dispatchAction(checkFileExists({ name: "test.txt", meta: { links: fileLinks } }))
    ).resolves.toBe(false);
  });

  it("detects an upload that was never initialized", async () => {
    await expect(
      dispatchAction(checkFileExists({ name: "test.txt", meta: {} }))
    ).resolves.toBe(false);
    expect(filesService.getFileMetadata).not.toHaveBeenCalled();
  });

  it("reports a failed check instead of assuming the result", async () => {
    filesService.getFileMetadata.mockRejectedValue(httpError(500));

    await expect(
      dispatchAction(checkFileExists({ name: "test.txt", meta: { links: fileLinks } }))
    ).rejects.toThrow();
  });
});
