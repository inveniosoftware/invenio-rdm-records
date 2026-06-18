/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2022 Graz University of Technology.
 * SPDX-FileCopyrightText: 2022 TU Wien.
 * SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import _map from "lodash/map";
import { UploadState } from "../../state/reducers/files";

export const getFilesList = (filesState) => {
  const filesList = Object.values(filesState).map((fileState) => {
    return {
      name: fileState.name,
      size: fileState.size,
      checksum: fileState.checksum,
      links: fileState.links,
      mimetype: fileState.mimetype,
      uploadState: {
        // initial: fileState.status === UploadState.initial,
        isFailed: fileState.status === UploadState.failed,
        isUploading: fileState.status === UploadState.uploading,
        isFinished: fileState.status === UploadState.completed,
        isPending: fileState.status === UploadState.pending,
      },
      progressPercentage: fileState.progressPercentage,
      cancelUploadFn: fileState.cancelUploadFn,
    };
  });

  const filesNames = _map(filesList, "name");
  const filesNamesSet = new Set(filesNames);

  const filesSize = filesList.reduce((totalSize, file) => (totalSize += file.size), 0);

  return { filesList, filesNamesSet, filesSize };
};
