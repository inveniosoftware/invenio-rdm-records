// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import axios from "axios";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";

const BASE_HEADERS = {
  "json": { "Content-Type": "application/json" },
  "vnd+json": {
    "Content-Type": "application/json",
    "Accept": "application/vnd.inveniordm.v1+json",
  },
  "octet-stream": { "Content-Type": "application/octet-stream" },
};

class UnsupportedTransferTypeError extends Error {
  filename;
  transferType;
  isUserFacing;

  constructor(message, opts) {
    super(message);
    this.isUserFacing = opts?.isUserFacing ?? false;
    if (opts?.filename) {
      this.filename = opts.filename;
    }
    if (opts?.transferType) {
      this.transferType = opts.transferType;
    }
  }
}

/**
 * API client response.
 */
export class DepositApiClientResponse {
  constructor(data, errors) {
    this.data = data;
    this.errors = errors;
  }
}

export class DepositApiClient {
  /* eslint-disable no-unused-vars */
  constructor(additionalApiConfig, createDraftURL, recordSerializer) {
    if (this.constructor === DepositApiClient) {
      throw new Error("Abstract");
    }

    const additionalHeaders = _get(additionalApiConfig, "headers");
    this.apiHeaders = Object.assign({}, BASE_HEADERS, additionalHeaders);

    this.apiConfig = {
      withCredentials: true,
      xsrfCookieName: "csrftoken",
      xsrfHeaderName: "X-CSRFToken",
      headers: this.apiHeaders["vnd+json"],
    };
    this.axiosWithConfig = axios.create(this.apiConfig);
    this.cancelToken = axios.CancelToken;
  }

  async createDraft(draft) {
    throw new Error("Not implemented.");
  }

  async saveDraft(draft, draftLinks) {
    throw new Error("Not implemented.");
  }

  async publishDraft(draftLinks) {
    throw new Error("Not implemented.");
  }

  async deleteDraft(draftLinks) {
    throw new Error("Not implemented.");
  }

  async reservePID(draftLinks, pidType) {
    throw new Error("Not implemented.");
  }

  async discardPID(draftLinks, pidType) {
    throw new Error("Not implemented.");
  }

  async createOrUpdateReview(draftLinks, communityId) {
    throw new Error("Not implemented.");
  }

  async deleteReview(draftLinks) {
    throw new Error("Not implemented.");
  }

  async submitReview(draftLinks) {
    throw new Error("Not implemented.");
  }
}

/**
 * API Client for deposits.
 */
export class RDMDepositApiClient extends DepositApiClient {
  constructor(additionalApiConfig, createDraftURL, recordSerializer) {
    super(additionalApiConfig);
    this.createDraftURL = createDraftURL;
    this.recordSerializer = recordSerializer;
  }

  async _createResponse(axiosRequest) {
    try {
      const response = await axiosRequest();
      const data = this.recordSerializer.deserialize(response.data || {});
      const errors = this.recordSerializer.deserializeErrors(
        response.data.errors || []
      );
      return new DepositApiClientResponse(data, errors);
    } catch (error) {
      let errorData = error.response.data;
      const errors = this.recordSerializer.deserializeErrors(
        error.response.data.errors || []
      );
      // this is to serialize raised error from the backend on publish
      if (!_isEmpty(errors)) errorData = errors;
      throw new DepositApiClientResponse({}, errorData);
    }
  }

  /**
   * Calls the API to create a new draft.
   *
   * @param {object} draft - Serialized draft
   */
  async createDraft(draft) {
    const payload = this.recordSerializer.serialize(draft);
    return this._createResponse(() =>
      this.axiosWithConfig.post(this.createDraftURL, payload, {
        params: { expand: 1 },
      })
    );
  }

  /**
   * Calls the API to read a pre-existing draft.
   *
   * @param {object} draftLinks - the draft links object
   */
  async readDraft(draftLinks) {
    return this._createResponse(() =>
      this.axiosWithConfig.get(draftLinks.self, {
        params: { expand: 1 },
      })
    );
  }

  /**
   * Calls the API to save a pre-existing draft.
   *
   * @param {object} draft - the draft payload
   */
  async saveDraft(draft, draftLinks) {
    const payload = this.recordSerializer.serialize(draft);
    return this._createResponse(() =>
      this.axiosWithConfig.put(draftLinks.self, payload, {
        params: { expand: 1 },
      })
    );
  }

  /**
   * Publishes the draft by calling its publish link.
   *
   * @param {string} draftLinks - the URL to publish the draft
   */
  async publishDraft(draftLinks) {
    return this._createResponse(() =>
      this.axiosWithConfig.post(draftLinks.publish, {}, { params: { expand: 1 } })
    );
  }

  /**
   * Deletes the draft by calling DELETE on its self link.
   *
   * @param {string} draftLinks - the URL to delete the draft
   */
  async deleteDraft(draftLinks) {
    return this._createResponse(() => this.axiosWithConfig.delete(draftLinks.self, {}));
  }

  /**
   * Calls the API to reserve a PID.
   *
   */
  async reservePID(draftLinks, pidType) {
    return this._createResponse(() => {
      const linkName = `reserve_${pidType}`;
      const link = draftLinks[linkName];
      return this.axiosWithConfig.post(
        link,
        {},
        {
          params: { expand: 1 },
        }
      );
    });
  }

  /**
   * Calls the API to discard a previously reserved PID.
   *
   */
  async discardPID(draftLinks, pidType) {
    return this._createResponse(() => {
      const linkName = `reserve_${pidType}`;
      const link = draftLinks[linkName];
      return this.axiosWithConfig.delete(link, {
        params: { expand: 1 },
      });
    });
  }

  /**
   * Creates a review request in initial state for draft by calling its
   * review link.
   *
   * @param {object} draftLinks - the draft links object
   */
  async createOrUpdateReview(draftLinks, communityId) {
    return this._createResponse(() =>
      this.axiosWithConfig.put(draftLinks.review, {
        receiver: {
          community: communityId,
        },
        type: "community-submission",
      })
    );
  }

  /**
   * Deletes a review request associated with the draft using its review link.
   *
   * @param {object} draftLinks - the draft links object
   */
  async deleteReview(draftLinks) {
    return this._createResponse(() =>
      this.axiosWithConfig.delete(draftLinks.review, {})
    );
  }

  /**
   * Submits the draft for review by calling its submit-review link.
   *
   * @param {object} draftLinks - the draft links object
   */
  async submitReview(draftLinks, reviewComment) {
    return this._createResponse(() => {
      const payload = reviewComment
        ? {
            payload: {
              content: reviewComment,
              format: "html",
            },
          }
        : {};
      return this.axiosWithConfig.post(draftLinks["submit-review"], payload);
    });
  }

  /**
   * Cancels the review for the draft by calling its cancel link.
   *
   * @param reviewLinks
   * @param reviewComment
   */
  async cancelReview(reviewLinks, reviewComment) {
    return this.axiosWithConfig.post(
      reviewLinks.actions.cancel,
      reviewComment
        ? {
            payload: {
              content: reviewComment,
              format: "html",
            },
          }
        : {}
    );
  }
}

/**
 * Abstract class for File API Client.
 * @constructor
 * @abstract
 */
export class DepositFileApiClient {
  constructor(additionalApiConfig) {
    if (this.constructor === DepositFileApiClient) {
      throw new Error("Abstract");
    }
    const additionalHeaders = _get(additionalApiConfig, "headers", {});
    this.apiHeaders = Object.assign({}, BASE_HEADERS, additionalHeaders);

    const apiConfig = {
      withCredentials: true,
      xsrfCookieName: "csrftoken",
      xsrfHeaderName: "X-CSRFToken",
      headers: this.apiHeaders["vnd+json"],
    };
    this.axiosWithConfig = axios.create(apiConfig);
  }

  isCancelled(error) {
    return axios.isCancel(error);
  }

  initializeFileUpload(initializeUploadUrl, filename, transferOptions) {
    throw new Error("Not implemented.");
  }

  uploadFile(uploadUrl, file, onUploadProgress, cancel) {
    throw new Error("Not implemented.");
  }

  uploadPart(uploadParams) {
    throw new Error("Not implemented.");
  }

  finalizeFileUpload(finalizeUploadUrl) {
    throw new Error("Not implemented.");
  }

  deleteFile(fileLinks) {
    throw new Error("Not implemented.");
  }
}

/**
 * Default File API Client for deposits.
 */
export class RDMDepositFileApiClient extends DepositFileApiClient {
  constructor(additionalApiConfig, defaultTransferType, enabledTransferTypes) {
    super(additionalApiConfig);
    this.defaultTransferType = defaultTransferType || "L";
    this.enabledTransferTypes = enabledTransferTypes || ["L"];
  }

  initializeFileUpload(initializeUploadUrl, filename, transferOptions = {}) {
    const { fileSize = 0, type = this.defaultTransferType, ...opts } = transferOptions;

    if (!this.enabledTransferTypes.includes(type)) {
      throw new UnsupportedTransferTypeError(
        `Unsupported upload TransferType "${type}".`,
        { file: filename, transferType: type }
      );
    }

    const payload = [
      {
        key: filename,
        size: fileSize,
        transfer: { type, ...opts },
      },
    ];
    return this.axiosWithConfig.post(initializeUploadUrl, payload, {});
  }

  uploadFile(uploadUrl, file, onUploadProgressFn, cancelFn) {
    return this.axiosWithConfig.put(uploadUrl, file, {
      headers: this.apiHeaders["octet-stream"],
      onUploadProgress: (event) => {
        const percent = Math.floor((event.loaded / event.total) * 100);
        onUploadProgressFn && onUploadProgressFn(percent);
      },
      cancelToken: new axios.CancelToken(cancelFn),
    });
  }

  finalizeFileUpload(finalizeUploadUrl) {
    return this.axiosWithConfig.post(finalizeUploadUrl, {});
  }

  importParentRecordFiles(draftLinks) {
    const link = `${draftLinks.self}/actions/files-import`;
    return this.axiosWithConfig.post(link, {});
  }

  deleteFile(fileLinks) {
    return this.axiosWithConfig.delete(fileLinks.self);
  }

  async uploadPart(uploadParams) {
    const {
      signature: { url, expires, headers, method = "PUT" },
      body,
      onProgress,
      signal,
    } = uploadParams;

    return this.axiosWithConfig.request({
      url,
      method,
      timeout: expires * 1000,
      data: body,
      headers: { ...this.apiHeaders["octet-stream"], ...headers },
      onUploadProgress: onProgress,
      signal,
    });
  }
}
