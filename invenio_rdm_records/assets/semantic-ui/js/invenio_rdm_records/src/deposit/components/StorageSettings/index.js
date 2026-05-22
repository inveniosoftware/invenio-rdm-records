/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import ReactDOM from "react-dom";
import StorageOverview from "./StorageOverview";

const root = document.getElementById("storage-overview-root");

if (root) {
  const storage = JSON.parse(root.dataset.storage);

  ReactDOM.render(<StorageOverview storage={storage} />, root);
}
