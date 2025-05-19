// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2022 Graz University of Technology.
// Copyright (C)      2022 TU Wien.
// Copyright (C)      2024 KTH Royal Institute of Technology.
// Copyryght (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _map from "lodash/map";
import { UploadState } from "../../state/reducers/files";

export const useFilesList = (filesState) => {
  const filesList = Object.values(filesState).map((fileState) => {
    return {
      name: fileState.name,
      size: fileState.size,
      checksum: fileState.checksum,
      links: fileState.links,
      uploadState: {
        // initial: fileState.status === UploadState.initial,
        isFailed: fileState.status === UploadState.error,
        isUploading: fileState.status === UploadState.uploading,
        isFinished: fileState.status === UploadState.finished,
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
