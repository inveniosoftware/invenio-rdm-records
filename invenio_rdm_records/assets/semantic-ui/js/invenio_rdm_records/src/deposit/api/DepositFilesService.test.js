// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import FakeTimers from "@sinonjs/fake-timers";
import { DepositFileApiClient } from "./DepositApiClient";
import { RDMDepositFilesService, UploadProgressNotifier } from "./DepositFilesService";

let fakeApiIsCancelled;
let fakeApiInitializeFileUpload;
let fakeApiUploadFile;
let fakeApiFinalizeFileUpload;
let fakeApiDeleteFile;
class FakeFileApiClient extends DepositFileApiClient {
  isCancelled(error) {
    return fakeApiIsCancelled(error);
  }

  initializeFileUpload(initializeUploadUrl, filename) {
    return fakeApiInitializeFileUpload(initializeUploadUrl, filename);
  }

  uploadFile(uploadUrl, file, onUploadProgress, cancel) {
    return fakeApiUploadFile(uploadUrl, file, onUploadProgress, cancel);
  }

  finalizeFileUpload(finalizeUploadUrl) {
    return fakeApiFinalizeFileUpload(finalizeUploadUrl);
  }

  deleteFile(fileLinks) {
    return fakeApiDeleteFile(fileLinks);
  }
}

let fakeOnUploadAdded;
let fakeOnUploadStarted;
let fakeOnUploadProgress;
let fakeOnUploadCompleted;
let fakeOnUploadCancelled;
let fakeOnUploadFailed;
class FakeProgressNotifier extends UploadProgressNotifier {
  onUploadAdded(filename) {
    fakeOnUploadAdded(filename);
  }
  onUploadStarted(filename, cancelFunc) {
    fakeOnUploadStarted(filename, cancelFunc);
  }
  onUploadProgress(filename, percent) {
    fakeOnUploadProgress(filename, percent);
  }
  onUploadCompleted(filename, size, checksum, links) {
    fakeOnUploadCompleted(filename, size, checksum, links);
  }
  onUploadCancelled(filename) {
    fakeOnUploadCancelled(filename);
  }
  onUploadFailed(filename) {
    fakeOnUploadFailed(filename);
  }
}

const fileApiClient = new FakeFileApiClient();
const progressNotifier = new FakeProgressNotifier();
let filesService;

beforeEach(() => {
  fakeApiIsCancelled = jest.fn();
  fakeApiInitializeFileUpload = jest.fn();
  fakeApiUploadFile = jest.fn((url, file, progressFn, cancelFn) => {
    cancelFn(() => "cancelled");
    progressFn(20);
  });
  fakeApiFinalizeFileUpload = jest.fn();
  fakeApiDeleteFile = jest.fn();

  fakeOnUploadAdded = jest.fn();
  fakeOnUploadStarted = jest.fn();
  fakeOnUploadProgress = jest.fn();
  fakeOnUploadCompleted = jest.fn();
  fakeOnUploadCancelled = jest.fn();
  fakeOnUploadFailed = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

describe("DepositFilesService tests", () => {
  describe("Upload success/fails tests", () => {
    const expectedFilename = "file1";
    const fakeFileData = {
      key: expectedFilename,
      size: "100",
      checksum: "abcd",
      links: {
        self: "self URL",
        content: "start upload URL",
        commit: "finalize upload URL",
      },
    };
    const fakeDataAfterInit = {
      data: {
        entries: [fakeFileData],
      },
    };

    filesService = new RDMDepositFilesService(fileApiClient, 1);
    filesService.setProgressNotifier(progressNotifier);

    it("it should add a new file to upload to the queue and start the upload", async () => {
      fakeApiInitializeFileUpload.mockReturnValueOnce(fakeDataAfterInit);
      fakeApiFinalizeFileUpload.mockReturnValueOnce({
        data: fakeFileData,
      });

      await filesService.upload("init upload URL", { name: "file1" });

      let params, filename;
      expect(fakeOnUploadAdded).toHaveBeenCalledTimes(1);
      filename = fakeOnUploadAdded.mock.calls[0][0];
      expect(filename).toEqual(expectedFilename);

      expect(fakeOnUploadStarted).toHaveBeenCalledTimes(1);
      params = fakeOnUploadStarted.mock.calls[0];
      filename = params[0];
      let cancelFn = params[1];
      expect(filename).toEqual(expectedFilename);
      expect(cancelFn()).toEqual("cancelled");

      expect(fakeOnUploadProgress).toHaveBeenCalledTimes(1);
      params = fakeOnUploadProgress.mock.calls[0];
      filename = params[0];
      let percent = params[1];
      expect(filename).toEqual(expectedFilename);
      expect(percent).toBeGreaterThan(0);

      expect(fakeOnUploadCompleted).toHaveBeenCalledTimes(1);
      params = fakeOnUploadCompleted.mock.calls[0];
      expect({
        key: params[0],
        size: params[1],
        checksum: params[2],
        links: params[3],
      }).toEqual(fakeFileData);
    });

    it("it should call the error callback when the init upload fails", async () => {
      fakeApiIsCancelled.mockReturnValueOnce(false);
      fakeApiInitializeFileUpload.mockRejectedValueOnce(new Error("init upload error"));

      await filesService.upload("init upload URL", { name: "file1" });

      expect(fakeOnUploadAdded).toHaveBeenCalledTimes(1);
      expect(fakeOnUploadStarted).not.toHaveBeenCalled();
      expect(fakeOnUploadFailed).toHaveBeenCalledTimes(1);
    });

    it("it should call the error callback when the upload fails and delete file", async () => {
      fakeApiIsCancelled.mockReturnValueOnce(false);
      fakeApiInitializeFileUpload.mockReturnValueOnce(fakeDataAfterInit);
      fakeApiUploadFile.mockRejectedValueOnce(new Error("upload error"));

      await filesService.upload("init upload URL", { name: "file1" });

      expect(fakeOnUploadAdded).toHaveBeenCalledTimes(1);
      expect(fakeOnUploadFailed).toHaveBeenCalledTimes(1);
      let filename = fakeOnUploadFailed.mock.calls[0][0];
      expect(filename).toEqual(expectedFilename);
      expect(fakeOnUploadStarted).not.toHaveBeenCalled();
      expect(fakeOnUploadProgress).not.toHaveBeenCalled();
      expect(fakeOnUploadCompleted).not.toHaveBeenCalled();
      expect(fakeOnUploadCancelled).not.toHaveBeenCalled();
    });

    it("it should call the error callback when the finalize upload fails and delete file", async () => {
      fakeApiIsCancelled.mockReturnValueOnce(false);
      fakeApiInitializeFileUpload.mockReturnValueOnce(fakeDataAfterInit);
      fakeApiFinalizeFileUpload.mockRejectedValueOnce(
        new Error("finalize upload error")
      );

      await filesService.upload("init upload URL", { name: "file1" });

      expect(fakeOnUploadAdded).toHaveBeenCalledTimes(1);
      expect(fakeOnUploadStarted).toHaveBeenCalledTimes(1);
      expect(fakeOnUploadProgress).toHaveBeenCalledTimes(1);
      expect(fakeOnUploadFailed).toHaveBeenCalledTimes(1);
      let filename = fakeOnUploadFailed.mock.calls[0][0];
      expect(filename).toEqual(expectedFilename);
      expect(fakeOnUploadCompleted).not.toHaveBeenCalled();
      expect(fakeOnUploadCancelled).not.toHaveBeenCalled();
    });

    it("it should call the cancel callback when the upload is cancelled and delete file", async () => {
      fakeApiIsCancelled.mockReturnValueOnce(true);
      fakeApiInitializeFileUpload.mockReturnValueOnce(fakeDataAfterInit);
      fakeApiUploadFile.mockRejectedValueOnce(new Error("upload error"));

      await filesService.upload("init upload URL", { name: "file1" });

      expect(fakeOnUploadAdded).toHaveBeenCalledTimes(1);
      expect(fakeOnUploadCancelled).toHaveBeenCalledTimes(1);
      let filename = fakeOnUploadCancelled.mock.calls[0][0];
      expect(filename).toEqual(expectedFilename);
      expect(fakeOnUploadStarted).not.toHaveBeenCalled();
      expect(fakeOnUploadProgress).not.toHaveBeenCalled();
      expect(fakeOnUploadCompleted).not.toHaveBeenCalled();
      expect(fakeOnUploadFailed).not.toHaveBeenCalled();
    });
  });

  describe("Concurrent uploads tests", () => {
    let clock;
    beforeEach(() => {
      clock = FakeTimers.install();
    });
    afterEach(() => {
      clock.uninstall();
    });

    const fakeFileData = (filename) => {
      return {
        key: filename,
        size: "100",
        checksum: "abcd",
        links: {
          self: filename,
          content: filename,
          commit: filename,
        },
      };
    };

    const fakeDataAfterInit = (fakeFileData) => {
      return {
        data: {
          entries: [fakeFileData],
        },
      };
    };

    filesService = new RDMDepositFilesService(fileApiClient, 2);
    filesService.setProgressNotifier(progressNotifier);

    function promiseDelay(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    }

    it("it should have max 2 concurrent uploads", async () => {
      fakeApiInitializeFileUpload.mockImplementation((_, filename) =>
        fakeDataAfterInit(fakeFileData(filename))
      );
      fakeApiFinalizeFileUpload.mockImplementation((finalizeUploadUrl) => {
        return { data: fakeFileData(finalizeUploadUrl) };
      });

      fakeApiUploadFile = jest
        .fn()
        .mockImplementationOnce(() => promiseDelay(1000))
        .mockImplementationOnce(() => promiseDelay(100))
        .mockImplementationOnce(() => promiseDelay(200));

      filesService.upload("init upload URL file1", { name: "file1" });
      filesService.upload("init upload URL file2", { name: "file2" });
      filesService.upload("init upload URL file3", { name: "file3" });
      expect(fakeOnUploadAdded).toHaveBeenCalledTimes(3);
      expect(fakeOnUploadCompleted).not.toHaveBeenCalled();
      const queue = filesService.uploaderQueue;
      expect(queue.totalInProgress).toEqual(2);
      expect(queue.currents.length).toEqual(2);
      expect(queue.pending.length).toEqual(1);

      await clock.tickAsync(150);
      expect(fakeOnUploadCompleted).toHaveBeenCalledTimes(1);
      expect(fakeOnUploadCompleted.mock.calls[0][0]).toEqual("file2");
      expect(queue.totalInProgress).toEqual(2);
      expect(queue.currents.length).toEqual(2);
      expect(queue.pending.length).toEqual(0);

      await clock.tickAsync(250);
      expect(fakeOnUploadCompleted).toHaveBeenCalledTimes(2);
      expect(fakeOnUploadCompleted.mock.calls[1][0]).toEqual("file3");
      expect(queue.totalInProgress).toEqual(1);
      expect(queue.currents.length).toEqual(1);
      expect(queue.pending.length).toEqual(0);

      await clock.tickAsync(1050);
      expect(fakeOnUploadCompleted).toHaveBeenCalledTimes(3);
      expect(fakeOnUploadCompleted.mock.calls[2][0]).toEqual("file1");
      expect(queue.totalInProgress).toEqual(0);
      expect(queue.currents.length).toEqual(0);
      expect(queue.pending.length).toEqual(0);
    });
  });
});
