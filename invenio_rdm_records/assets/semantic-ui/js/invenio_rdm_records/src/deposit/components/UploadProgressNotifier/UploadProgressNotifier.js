/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { UploadProgressNotifier } from "../../api/DepositFilesService";
import {
  FILE_UPLOAD_ADDED,
  FILE_UPLOAD_CANCELLED,
  FILE_UPLOAD_FAILED,
  FILE_UPLOAD_FINISHED,
  FILE_UPLOAD_INITIALIZED,
  FILE_UPLOAD_IN_PROGRESS,
  FILE_UPLOAD_SET_CANCEL_FUNCTION,
} from "../../state/types";

export class RDMUploadProgressNotifier extends UploadProgressNotifier {
  onUploadAdded(filename) {
    this.dispatcher &&
      this.dispatcher({
        type: FILE_UPLOAD_ADDED,
        payload: {
          filename: filename,
        },
      });
  }

  onUploadInitialized(filename, links) {
    this.dispatcher &&
      this.dispatcher({
        type: FILE_UPLOAD_INITIALIZED,
        payload: {
          filename: filename,
          links: links,
        },
      });
  }

  onUploadStarted(filename, cancelFn) {
    this.dispatcher &&
      this.dispatcher({
        type: FILE_UPLOAD_SET_CANCEL_FUNCTION,
        payload: { filename: filename, cancelUploadFn: cancelFn },
      });
  }

  onUploadProgress(filename, percent) {
    this.dispatcher &&
      this.dispatcher({
        type: FILE_UPLOAD_IN_PROGRESS,
        payload: {
          filename: filename,
          percent: percent,
        },
      });
  }

  onUploadCompleted(filename, size, checksum, links) {
    this.dispatcher &&
      this.dispatcher({
        type: FILE_UPLOAD_FINISHED,
        payload: {
          filename: filename,
          size: size,
          checksum: checksum,
          links: links,
        },
      });
  }

  onUploadCancelled(filename) {
    this.dispatcher &&
      this.dispatcher({
        type: FILE_UPLOAD_CANCELLED,
        payload: {
          filename: filename,
        },
      });
  }

  onUploadFailed(filename) {
    this.dispatcher &&
      this.dispatcher({
        type: FILE_UPLOAD_FAILED,
        payload: {
          filename: filename,
        },
      });
  }
}
