// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2022 Graz University of Technology.
// Copyright (C)      2022 TU Wien.
// Copyright (C)      2024 KTH Royal Institute of Technology.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

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
