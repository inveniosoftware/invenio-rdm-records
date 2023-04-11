// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

export class DepositService {
  constructor(draftsService, filesService) {
    this.draftsService = draftsService;
    this.filesService = filesService;
  }

  get drafts() {
    return this.draftsService;
  }

  get files() {
    return this.filesService;
  }
}
