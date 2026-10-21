/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import StorageOverview from "./StorageOverview";

const rootElement = document.getElementById("storage-overview-root");

if (rootElement) {
  const storage = JSON.parse(rootElement.dataset.storage);
  const root = createRoot(rootElement);

  root.render(<StorageOverview storage={storage} />);
}
