// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

export class DepositDraftsService {
  /* eslint-disable no-unused-vars */
  constructor(apiClient) {
    if (this.constructor === DepositDraftsService) {
      throw new Error("Abstract");
    }
  }
  async read(draftLinks) {
    throw new Error("Not implemented.");
  }
  async create(draft) {
    throw new Error("Not implemented.");
  }
  async save(draft) {
    throw new Error("Not implemented.");
  }
  async publish(draftLinks) {
    throw new Error("Not implemented.");
  }
  async delete(draftLinks) {
    throw new Error("Not implemented.");
  }
  async reservePID(draftLinks, pidType) {
    throw new Error("Not implemented.");
  }
  async discardPID(draftLinks, pidType) {
    throw new Error("Not implemented.");
  }
  async createOrUpdateReview(draftLinks, newCommunityId) {
    throw new Error("Not implemented.");
  }
  async deleteReview(draftLinks) {
    throw new Error("Not implemented.");
  }
  async submitReview(draftLinks) {
    throw new Error("Not implemented.");
  }
}

export class RDMDepositDraftsService extends DepositDraftsService {
  constructor(apiClient) {
    super();
    this.apiClient = apiClient;
  }

  _draftAlreadyCreated(record) {
    return !!record.id;
  }

  /**
   * Creates the current draft (backend) and changes URL to match its edit URL.
   */
  async create(draft) {
    return this.apiClient.createDraft(draft);
  }

  /**
   * Read the current draft (backend).
   */
  async read(draftLinks) {
    return this.apiClient.readDraft(draftLinks);
  }

  /**
   * Saves the current draft (backend) and changes URL to match its edit URL.
   */
  async save(draft) {
    return this._draftAlreadyCreated(draft)
      ? this.apiClient.saveDraft(draft, draft.links)
      : this.create(draft);
  }

  /**
   * Publishes the current draft (backend) and redirects to its view URL.
   */
  async publish(draftLinks) {
    return this.apiClient.publishDraft(draftLinks);
  }

  /**
   * Deletes the current draft and redirects to uploads page.
   */
  async delete(draftLinks) {
    return this.apiClient.deleteDraft(draftLinks);
  }

  /**
   * Reserve a PID
   */
  async reservePID(draftLinks, pidType) {
    return this.apiClient.reservePID(draftLinks, pidType);
  }

  /**
   * Discard a previously reserved PID
   */
  async discardPID(draftLinks, pidType) {
    return this.apiClient.discardPID(draftLinks, pidType);
  }

  /**
   * Creates or updates a review request.
   */
  async createOrUpdateReview(draftLinks, newCommunityId) {
    return this.apiClient.createOrUpdateReview(draftLinks, newCommunityId);
  }

  /**
   * Deletes a review request associated with the draft.
   */
  async deleteReview(draftLinks) {
    return this.apiClient.deleteReview(draftLinks);
  }

  /**
   * Submits the draft for review.
   */
  async submitReview(draftLinks, reviewComment) {
    return this.apiClient.submitReview(draftLinks, reviewComment);
  }
}
