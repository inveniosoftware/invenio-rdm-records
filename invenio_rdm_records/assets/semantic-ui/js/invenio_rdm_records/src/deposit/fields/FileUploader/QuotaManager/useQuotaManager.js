/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { useState } from "react";

/** Manage the additional quota selected for a draft. */
export const useQuotaManager = (quota, filesSize) => {
  const [showQuotaSection, setShowQuotaSection] = useState(false);
  const [additionalQuota, _setAdditionalQuota] = useState(
    quota.quotaIncrease?.additionalStorage / Math.pow(10, 9) || 0
  );

  const toggleQuotaSection = () => {
    setShowQuotaSection(!showQuotaSection);
  };

  // Rescale quota from bytes to GB, as user input requires GB.
  const quotaInGB = Object.keys(quota.quotaIncrease ?? {}).reduce((obj, key) => {
    if (typeof quota.quotaIncrease[key] === "number") {
      obj[key] = quota.quotaIncrease[key] / Math.pow(10, 9);
    } else {
      obj[key] = quota.quotaIncrease[key];
    }
    return obj;
  }, {});

  const setAdditionalQuota = (value) => {
    // If a user uploads a file without publishing, we cannot get the minimum
    // additional quota from the backend, so use the uploaded files size instead.
    const additionalFilesSize =
      Math.ceil(filesSize / Math.pow(10, 9)) - quotaInGB.defaultStorage;
    const minAdditional = Math.max(
      quotaInGB.minAdditionalQuotaValue,
      additionalFilesSize
    );
    const maxAdditional = quotaInGB.maxAdditionalQuotaValue;

    if (value < minAdditional) {
      _setAdditionalQuota(minAdditional);
    } else if (minAdditional <= value && value <= maxAdditional) {
      _setAdditionalQuota(value);
    } else if (value > maxAdditional) {
      _setAdditionalQuota(maxAdditional);
    } else if (isNaN(value)) {
      _setAdditionalQuota(minAdditional);
    }
  };

  return {
    additionalQuota,
    quotaInGB,
    setAdditionalQuota,
    showQuotaSection,
    toggleQuotaSection,
  };
};
