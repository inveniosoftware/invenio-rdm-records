// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

// NOTE: If WASM undesirable, we can use library like Crypto-JS
import { md5 } from "hash-wasm";
import AwsS3Multipart from "@uppy/aws-s3-multipart";
import { fetcher } from "@uppy/utils/lib/fetcher";
import { humanReadableBytes } from "react-invenio-forms";

import { FileSizeError, InvalidPartNumberError, SignedUrlExpiredError } from "./error";

const defaultOptions = {
  // NOTE: null here means “include all”, [] means include none.
  // This is inconsistent with @uppy/aws-s3 and @uppy/transloadit
  allowedMetaFields: null,
  limit: 3,
  getTemporarySecurityCredentials: false,
  getUploadParameters: null,
  shouldUseMultipart: null,
  uploadPartBytes: null,
  retryDelays: [0, 1000, 3000, 5000],
  companionHeaders: {},
  checkPartIntegrity: false,
};

export class RDMUppyUploaderPlugin extends AwsS3Multipart {
  #maxMultipartParts = 10_000;

  constructor(uppy, opts) {
    super(uppy, {
      ...defaultOptions,
      fieldName: opts.bundle ? "files[]" : "file",
      ...opts,
    });
    this.type = "uploader";
    this.draftRecord = this.opts.draftRecord;
    this.id = this.opts.id || "RDMUppyUploaderPlugin";
    this.getChunkSize = this.opts.getChunkSize || this.getChunkSize;
    this.shouldUseMultipart = this.opts.shouldUseMultipart || this.shouldUseMultipart;
    this.isTransferSupported = this.opts.isTransferSupported;
    this.transferType = this.opts.transferType;

    this.i18nInit();
    super.setOptions({
      // Here we override default implementation in AwsS3Multipart
      getChunkSize: this.getChunkSize.bind(this),
      shouldUseMultipart: this.shouldUseMultipart.bind(this),
      uploadPartBytes: this.uploadPartBytes.bind(this),
    });
  }

  install() {
    AwsS3Multipart.prototype.install.apply(this);
    this.uppy.on("upload-success", this.#completeSinglePartUpload);
    this.uppy.on("upload-progress", this.#onUploadProgress);
    this.uppy.on("file-removed", this.#onFileRemoved);
    this.uppy.on("complete", this.#resetOnComplete);
    this.uppy.addPreProcessor(this.#saveDraftBeforeUpload);
    // Disable resumable uploads Uppy capability.
    // Currently unsupported, as it requires missing API
    // implementation for the `listParts` method.
    this.uppy.addPreProcessor(this.#disableResumableUploadsCapability);
  }

  uninstall() {
    AwsS3Multipart.prototype.uninstall.apply(this);
    this.uppy.off("upload-success", this.#completeSinglePartUpload);
    this.uppy.off("upload-progress", this.#onUploadProgress);
    this.uppy.off("file-removed", this.#onFileRemoved);
    this.uppy.off("complete", this.#resetOnComplete);
    this.uppy.removePreProcessor(this.#saveDraftBeforeUpload);
    this.uppy.removePreProcessor(this.#disableResumableUploadsCapability);
  }

  async uploadPartBytes({ signature, body, onProgress, onComplete, signal }) {
    const { headers = {} } = signature;

    if (this.opts.checkPartIntegrity) {
      headers["Content-MD5"] = await this.#getPartDigest(body);
    }

    const response = await this.opts.uploadPart({
      signature: { ...signature, headers },
      body,
      onProgress,
      onComplete,
      signal,
    });
    onProgress?.({
      loaded: body.size,
      lengthComputable: true,
    });
    onComplete?.(response.etag);
    return {
      ...response,
      ETag: response.etag,
    };
  }

  #onUploadProgress = (file, progress) => {
    const percentage =
      progress.bytesTotal > 0
        ? Math.floor((progress.bytesUploaded / progress.bytesTotal) * 100)
        : 0;
    this.opts.setUploadProgress(file, percentage);
  };

  #onFileRemoved = (file) => {
    if (!file.progress.uploadComplete) {
      file.links = file.meta.links;
      this.opts.abortUpload(file);
    }
  };

  #resetOnComplete = (result) => {
    this.uppy.cancelAll();
  };

  #saveDraftBeforeUpload = async (fileIDs) => {
    this.draftRecord = await this.opts.saveAndFetchDraft(this.draftRecord);
  };

  #completeSinglePartUpload = (file, response) => {
    const { uploadURL } = response;
    if (!uploadURL) {
      // Ignore cases when uploadURL missing - not a single-part upload
      return;
    }
    return this.completeMultipartUpload(file);
  };

  #disableResumableUploadsCapability = () => {
    const { capabilities } = this.uppy.getState();
    this.uppy.setState({
      capabilities: {
        ...capabilities,
        resumableUploads: false,
      },
    });
  };

  #getFetcher = (file) => {
    return async (url, options) => {
      try {
        const res = await fetcher(url, {
          ...options,
          shouldRetry: this.opts.shouldRetry,
          onTimeout: (timeout) => {
            const seconds = Math.ceil(timeout / 1000);
            const error = new Error(this.i18n("uploadStalled", { seconds }));
            this.uppy.emit("upload-stalled", error, [file]);
          },
        });

        const body = JSON.parse(res.responseText);
        return body;
      } catch (error) {
        if (error.name === "AbortError") {
          return undefined;
        }
        const request = error.request;
        this.uppy.emit("upload-error", this.uppy.getFile(file.id), error, request);

        throw error;
      }
    };
  };

  async #getPartDigest(blob) {
    const arrayBuffer = await blob.arrayBuffer();
    const digest = await md5(new Uint8Array(arrayBuffer));
    // Convert hex digest to bytestring
    const byteString = digest
      .match(/.{2}/g)
      .map((byte) => String.fromCharCode(parseInt(byte, 16)))
      .join("");
    // Convert bytestring to base64
    return btoa(byteString);
  }

  /**
   * A boolean, or a function that returns a boolean which is called for each file that is uploaded with the corresponding UppyFile instance as argument.
   *
   * By default, all files with a file.size ≤ getChunkSize will be uploaded in a single chunk, all files larger than that as multipart.
   * @param {*} file the file object from Uppy’s state. The most relevant keys are file.name and file.type
   */
  shouldUseMultipart(file) {
    if (!this.isTransferSupported(this.transferType.MULTIPART)) {
      return false;
    }
    const chunkSize = this.getChunkSize(file);
    const partCount = Math.ceil(file.size / chunkSize);
    return partCount > 1;
  }

  /**
   * A function used for single-part upload initialization.
   *
   * @param {*} file UppyFile the file that will be uploaded
   * @param options object
   * @param signal AbortSignal
   * @returns object | Promise<object>
   *   - **method**: string, the HTTP method to be used for the upload. This should be one of either PUT or POST, depending on the type of upload used.
   *   - **url**: string, the URL to which the upload request will be sent. When using a presigned PUT upload, this should be the URL to the S3 object with signing parameters included in the query string. When using a POST upload with a policy document, this should be the root URL of the bucket.
   *   - **fields**: object, an object with form fields to send along with the upload request. For presigned PUT uploads (which are default), this should be left empty.
   *   - **headers**: object, an object with request headers to send along with the upload request. When using a presigned PUT upload, it’s a good idea to provide headers['content-type']. That will make sure that the request uses the same content-type that was used to generate the signature. Without it, the browser may decide on a different content-type instead, causing S3 to reject the upload.
   */
  async getUploadParameters(file, options, signal) {
    file.transferOptions = {
      fileSize: file.size,
      type: this.transferType.LOCAL,
      cancelFn: () => this.uppy.removeFile(file.id),
    };

    try {
      const response = await this.opts.initializeFileUpload(this.draftRecord, file);
      this.uppy.setFileMeta(file.id, {
        file_id: response.file_id,
        links: response.links,
      });
      return {
        headers: {
          "Content-Type": "application/octet-stream",
        },
        url: response.links.content,
        method: "PUT",
        signal,
      };
    } catch (error) {
      this.uppy.info(error.message, "error");
      throw error;
    }
  }

  /**
   * Calculates the optimal file part size for multipart uploads using logarithmic scaling.
   *
   * For multipart uploads, chunks are sent in batches to have presigned URLs generated with signPart() and then to be uploaded.
   *
   * The chunk sizes are distributed evenly on a logarithmic scale between the minimum
   * part size (5 MiB) and the maximum allowed part size (capped by AWS S3 limits and
   * the provided maximum file size). This means each step increases by a constant
   * multiplicative factor, resulting in more balanced and meaningful increments
   * across a wide size range.
   *
   * Logarithmic scaling is chosen because chunk sizes can vary over several orders
   * of magnitude (from megabytes to gigabytes). Using a log scale ensures that
   * smaller chunk sizes get fine-grained steps and larger chunk sizes don’t jump
   * too abruptly, providing better granularity for different file sizes.
   * This approach helps optimize multipart upload performance and retry costs,
   * since chunk sizes increase smoothly relative to file size.
   *
   * AWS S3 constraints: https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html.
   * @param {*} file the file object from Uppy’s state.
   * @param maxFileSize maximum permissible file byte size to be chunked (5 TiB by default)
   * @returns byte size of individual part chunk
   */
  getChunkSize(file, maxFileSize = 5497558138880) {
    const MiB = 1024 * 1024;
    const GiB = 1024 * MiB;
    const minPartSize = 5 * MiB;
    const maxPartSize = 5 * GiB;
    const maxParts = this.#maxMultipartParts;

    // Calculate max allowed part size based on maxFileSize and maxParts, capped by S3 limit
    const maxAllowedPartSize = Math.min(maxPartSize, Math.ceil(maxFileSize / maxParts));

    const steps = 5;
    const logMin = Math.log(minPartSize);
    const logMax = Math.log(maxAllowedPartSize);
    const stepSize = (logMax - logMin) / (steps - 1);

    const chunkSizes = Array.from({ length: steps }, (_, i) =>
      Math.round(Math.exp(logMin + i * stepSize))
    ).reverse(); // reverse to try larger chunk sizes first

    for (const chunkSize of chunkSizes) {
      if (chunkSize > file.size) continue;

      const numParts = Math.ceil(file.size / chunkSize);
      if (numParts <= maxParts) {
        return chunkSize;
      }
    }

    // File is smaller than all chunk sizes, use file size as one-part chunk
    if (file.size <= maxAllowedPartSize * maxParts) {
      return file.size;
    }

    throw new FileSizeError(
      this.i18n("exceedsSize", {
        size: humanReadableBytes(maxAllowedPartSize * maxParts),
        file: file.name ?? this.getI18n()("unnamed"),
      }),
      { file }
    );
  }

  /**
   * A function used for multipart upload initialization.
   * @param {*} file the file object from Uppy’s state. The most relevant keys are file.name and file.type
   * @returns a Promise for an object with keys:
   *   - **uploadId**: The UploadID returned by S3.
   *   - **key**: The object key for the file. This needs to be returned to allow it to be different from the file.name.
   */
  async createMultipartUpload(file) {
    const chunkSize = this.getChunkSize(file);

    file.transferOptions = {
      fileSize: file.size,
      parts: Math.ceil(file.size / chunkSize),
      part_size: chunkSize,
      type: this.transferType.MULTIPART,
      cancelFn: () => this.uppy.removeFile(file.id),
    };
    const response = await this.opts.initializeFileUpload(this.draftRecord, file);

    // Map any links to Uppy file state for further use (e.g. to fetch signed part URLs)
    this.uppy.setFileMeta(file.id, {
      file_id: response.file_id,
      links: response.links,
    });
    return { uploadId: file.file_id, key: response.key };
  }

  /**
   * A function to obtain a signed upload URL for the given part number.
   * @param {*} file the file object from Uppy’s state. The most relevant keys are file.name and file.type
   * @param {*} partData an object with the keys:
   *   - **uploadId**: The UploadID of this Multipart upload.
   *   - **key**: The object key in the S3 bucket.
   *   - **partNumber**: can’t be zero.
   *   - **body**: The data that will be signed.
   *   - **signal**: An AbortSignal that may be used to abort an ongoing request.
   * @returns This function should return a object, or a promise that resolves to an object, with the following keys:
   *   - **url**: the pre-signed URL, as a string.
   *   - **headers**: (Optional) Custom headers to send along with the request to S3 endpoint.
   */
  async signPart(file, partData) {
    const { partNumber, signal } = partData;
    const signedPartUrls = file.meta.links.parts;
    const headers = {};

    if (partNumber < 1 || partNumber > signedPartUrls.length) {
      throw new InvalidPartNumberError(
        this.i18n("invalidPartNumber", {
          partNumber: partNumber,
          file: file.name ?? this.getI18n()("unnamed"),
        }),
        { file, partNumber }
      );
    }

    const { expiration, url } = signedPartUrls.find(({ part }) => part === partNumber);

    const expiryDate = new Date(expiration);
    const now = new Date();
    if (now > expiryDate) {
      const fetch = this.#getFetcher(file, { signal });
      // Re-fetching file metadata will re-generate signed part URLs
      const response = await fetch(file.meta.links.self);

      file.meta.links = response.links;
      this.uppy.setFileMeta(file.id, {
        links: response.links,
      });

      // Throw an error to let Uppy retry with fresh state
      throw new SignedUrlExpiredError(
        this.i18n("signedUrlExpired", {
          partNumber: partNumber,
          file: file.name ?? this.getI18n()("unnamed"),
        }),
        { file, partNumber }
      );
    }

    return { url, headers };
  }

  /**
   * A function that calls the S3 Multipart API to complete a Multipart upload, combining all parts into a single object in the S3 bucket.
   * @param {*} file the file object from Uppy’s state. The most relevant keys are file.name and file.type
   * @param {*}  params an object with keys:
   *   - **uploadId**: The UploadID of this Multipart upload.
   *   - **key**: The object key of this Multipart upload.
   *   - **parts**: S3-style list of parts, an array of objects with ETag and PartNumber properties. This can be passed straight to S3’s Multipart API.
   * @returns a Promise for an object with properties:
   *  - **location**: (Optional) A publicly accessible URL to the object in the S3 bucket.
   *  - The default implementation calls out to Companion’s S3 signing endpoints.
   */
  async completeMultipartUpload(file) {
    const response = await this.opts.finalizeUpload(file);
    return response.links.content;
  }

  /**
   * A function that calls the S3 Multipart API to abort a Multipart upload,
   * and removes all parts that have been uploaded so far.
   *
   * Disabled/Noop as upload abortion is handled by the `#onFileRemoved` event handler for all upload flows.
   */
  async abortMultipartUpload(file) {}
}

export default RDMUppyUploaderPlugin;
