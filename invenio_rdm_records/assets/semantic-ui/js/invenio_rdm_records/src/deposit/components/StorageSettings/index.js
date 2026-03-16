// This file is part of Invenio-RDM-Records
// Copyright (C) 2026 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import StorageOverview from "./StorageOverview";

const root = document.getElementById("storage-overview-root");

if (root) {
  const storage = JSON.parse(root.dataset.storage);

  ReactDOM.render(<StorageOverview storage={storage} />, root);
}
