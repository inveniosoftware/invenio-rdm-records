/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2025 CESNET.
 * SPDX-License-Identifier: MIT
 */

// Drives the business logic of the InvenioFormApp.
// Defines what happens when a button is clicked.

import { UploadState } from "../state/reducers/files";

class UploaderQueue {
  currents = [];
  pending = [];
  cancelled = new Set();

  put(initializeUploadURL, file) {
    this.pending.push({
      initializeUploadURL: initializeUploadURL,
      file: file,
    });
  }

  get totalInProgress() {
    return this.currents.length;
  }

  get next() {
    // remove from the pending and add it to the currents
    const nextFile = this.pending.shift();
    if (nextFile !== undefined) {
      this.currents.push(nextFile.file);
    }

    return nextFile;
  }

  markCompleted(file) {
    this.cancelled.delete(file);
    const index = this.currents.indexOf(file);
    if (index >= 0) {
      // remove from the current
      this.currents.splice(index, 1);
    }
  }

  // Drops an upload that hasn't started yet, returning whether it was found.
  remove(fileName) {
    const matchesName = (file) => file.name.normalize() === fileName?.normalize();
    const index = this.pending.findIndex((pendingUpload) =>
      matchesName(pendingUpload.file)
    );

    if (index >= 0) {
      this.pending.splice(index, 1);
      return true;
    }

    // An upload already being initialized can only be discarded once that finishes.
    const startingUpload = this.currents.find(matchesName);

    if (startingUpload) {
      this.cancelled.add(startingUpload);
      return true;
    }

    return false;
  }

  // One-shot check, the cancellation is forgotten once read.
  isCancelled(file) {
    return this.cancelled.delete(file);
  }
}

export class UploadProgressNotifier {
  /* eslint-disable no-unused-vars */
  constructor(dispatcher) {
    this.dispatcher = dispatcher;
  }
  onUploadAdded(filename) {
    throw new Error("Not implemented.");
  }
  onUploadInitialized(filename, links) {
    throw new Error("Not implemented.");
  }
  onUploadStarted(filename, cancelFunc) {
    throw new Error("Not implemented.");
  }
  onUploadProgress(filename, percent) {
    throw new Error("Not implemented.");
  }
  onUploadCompleted(filename, size, checksum, links) {
    throw new Error("Not implemented.");
  }
  onUploadCancelled(filename) {
    throw new Error("Not implemented.");
  }
  onUploadFailed(filename) {
    throw new Error("Not implemented.");
  }
}

export class DepositFilesService {
  constructor(fileApiClient, fileUploadConcurrency) {
    if (this.constructor === DepositFilesService) {
      throw new Error("Abstract");
    }
  }

  setProgressNotifier(progressNotifier) {
    if (!(progressNotifier instanceof UploadProgressNotifier)) {
      throw new Error(
        "Progress notifier must be an instance of `UploadProgressNotifier`"
      );
    }
    this.progressNotifier = progressNotifier;
  }

  async initializeUpload(initializeUploadURL, file) {
    throw new Error("Not implemented.");
  }

  async upload(initializeUploadURL, file, progressNotifier) {
    throw new Error("Not implemented.");
  }

  /**
   * Cancels an upload that hasn't started yet, returning whether it was found.
   * A no-op by default, as services without an upload queue have nothing to cancel.
   */
  cancelQueuedUpload(fileName) {
    return false;
  }

  async uploadPart(uploadParams) {
    throw new Error("Not implemented.");
  }

  async finalizeUpload(commitFileURL, file) {
    throw new Error("Not implemented.");
  }

  async getFileMetadata(fileLinks) {
    throw new Error("Not implemented.");
  }

  async delete(fileLinks) {
    throw new Error("Not implemented.");
  }

  async importParentRecordFiles(draftLinks) {
    throw new Error("Not implemented.");
  }
}

export class RDMDepositFilesService extends DepositFilesService {
  constructor(fileApiClient, fileUploadConcurrency) {
    super();
    this.fileApiClient = fileApiClient;
    this.maxConcurrentUploads = fileUploadConcurrency || 3;
    this.uploaderQueue = new UploaderQueue();
  }

  _initializeUpload = async (initializeUploadURL, file) => {
    const response = await this.fileApiClient.initializeFileUpload(
      initializeUploadURL,
      file.name,
      file.transferOptions
    );

    // get the init file with the sent filename
    const initializedFile = response.data.entries.filter(
      (entry) => entry.key.normalize() === file.name.normalize()
    )[0]; // this should throw an error if not found

    return initializedFile;
  };

  _doUpload = async (uploadUrl, file) =>
    await this.fileApiClient.uploadFile(
      uploadUrl,
      file,
      (percent) => this.progressNotifier.onUploadProgress(file.name, percent),
      (cancelFn) => this.progressNotifier.onUploadStarted(file.name, cancelFn)
    );

  _finalizeUpload = async (commitFileURL, file) => {
    // Regardless of what is the status of the finalize step we start
    // the next upload in the queue
    this.uploaderQueue.markCompleted(file);
    this._startNextUpload();
    const response = await this.fileApiClient.finalizeFileUpload(commitFileURL);
    return response.data;
  };

  _onError = (file, isCancelled = false) => {
    if (isCancelled) {
      this.progressNotifier.onUploadCancelled(file.name);
    } else {
      this.progressNotifier.onUploadFailed(file.name);
    }
    this.uploaderQueue.markCompleted(file);
    this._startNextUpload();
  };

  // Deletes the backend entry of an upload cancelled during its initialization.
  _discardCancelledUpload = async (file, fileLinks) => {
    // Free the slot first, the cleanup must not hold up the queued uploads.
    this.uploaderQueue.markCompleted(file);
    this._startNextUpload();

    try {
      await this.delete(fileLinks);
    } catch (error) {
      console.error("Error deleting a cancelled upload", error, file);
    }
  };

  _startNewUpload = async (initializeUploadURL, file) => {
    let initializedFileMetadata;
    try {
      initializedFileMetadata = await this._initializeUpload(initializeUploadURL, file);

      if (this.uploaderQueue.isCancelled(file)) {
        await this._discardCancelledUpload(file, initializedFileMetadata.links);
        return;
      }

      this.progressNotifier.onUploadInitialized(
        file.name,
        initializedFileMetadata.links
      );
    } catch (error) {
      this._onError(file);
      return;
    }

    const startUploadURL = initializedFileMetadata.links.content;
    const commitFileURL = initializedFileMetadata.links.commit;
    try {
      await this._doUpload(startUploadURL, file);
      const fileData = await this._finalizeUpload(commitFileURL, file);
      this.progressNotifier.onUploadCompleted(
        fileData.key,
        fileData.size,
        fileData.checksum,
        fileData.links
      );
    } catch (error) {
      console.error(error);
      const isCancelled = this.fileApiClient.isCancelled(error);
      this._onError(file, isCancelled);
    }
  };

  _startNextUpload = async () => {
    const shouldStartNewUpload =
      this.uploaderQueue.totalInProgress < this.maxConcurrentUploads;

    if (shouldStartNewUpload) {
      const nextFile = this.uploaderQueue.next;
      if (nextFile) {
        await this._startNewUpload(nextFile.initializeUploadURL, nextFile.file);
      }
    }
  };

  initializeUpload = async (initializeUploadURL, file) => {
    const initializedFile = await this._initializeUpload(initializeUploadURL, file);
    this.progressNotifier.onUploadStarted(file.name, file.transferOptions.cancelFn);
    return initializedFile;
  };

  upload = async (initializeUploadURL, file) => {
    this.uploaderQueue.put(initializeUploadURL, file);
    this.progressNotifier.onUploadAdded(file.name);

    await this._startNextUpload();
  };

  cancelQueuedUpload = (fileName) => {
    return this.uploaderQueue.remove(fileName);
  };

  getFileMetadata = async (fileLinks) => {
    return (await this.fileApiClient.getFileMetadata(fileLinks)).data;
  };

  delete = async (fileLinks) => {
    return await this.fileApiClient.deleteFile(fileLinks);
  };

  uploadPart = async (uploadParams) => {
    return await this.fileApiClient.uploadPart(uploadParams);
  };

  finalizeUpload = async (commitFileURL, file) => {
    return (await this.fileApiClient.finalizeFileUpload(commitFileURL)).data;
  };

  importParentRecordFiles = async (draftLinks) => {
    const response = await this.fileApiClient.importParentRecordFiles(draftLinks);

    return response.data.entries.reduce(
      (acc, file) => ({
        ...acc,
        [file.key]: {
          status: UploadState.completed,
          size: file.size,
          name: file.key,
          progressPercentage: 100,
          checksum: file.checksum,
          links: file.links,
        },
      }),
      {}
    );
  };
}
