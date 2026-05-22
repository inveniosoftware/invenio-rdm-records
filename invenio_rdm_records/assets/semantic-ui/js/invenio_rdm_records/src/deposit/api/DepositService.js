/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

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
