/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2025 CESNET.
 * SPDX-License-Identifier: MIT
 */

export class FileSizeError extends Error {
  isUserFacing;
  file;

  constructor(message, opts) {
    super(message);
    this.isUserFacing = opts?.isUserFacing ?? true;
    if (opts?.file) {
      this.file = opts.file;
    }
  }

  isRestriction = true;
}

export class InvalidPartNumberError extends Error {
  file;
  partNumber;
  isUserFacing;

  constructor(message, opts) {
    super(message);
    this.isUserFacing = opts?.isUserFacing ?? false;
    if (opts?.file) {
      this.file = opts.file;
    }
    if (opts?.partNumber) {
      this.partNumber = opts.partNumber;
    }
  }
}

export class SignedUrlExpiredError extends Error {
  file;
  partNumber;
  isUserFacing;

  constructor(message, opts) {
    super(message);
    this.isUserFacing = opts?.isUserFacing ?? false;
    if (opts?.file) {
      this.file = opts.file;
    }
    if (opts?.partNumber) {
      this.partNumber = opts.partNumber;
    }
  }
}
