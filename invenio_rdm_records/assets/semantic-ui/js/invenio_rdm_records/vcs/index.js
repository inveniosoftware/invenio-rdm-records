/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import ReactDOM from "react-dom";
import "./api";
import { VCSCommunitiesApp } from "./VCSCommunitiesApp";
import { OverridableContext, overrideStore } from "react-overridable";

const domContainer = document.getElementById("invenio-vcs-communities-app");
const communityRequiredToPublish =
  domContainer.dataset["communityRequiredToPublish"] === "True";
const overriddenComponents = overrideStore.getAll();

if (domContainer) {
  ReactDOM.render(
    <OverridableContext.Provider value={overriddenComponents}>
      <VCSCommunitiesApp communityRequiredToPublish={communityRequiredToPublish} />
    </OverridableContext.Provider>,
    domContainer
  );
}
