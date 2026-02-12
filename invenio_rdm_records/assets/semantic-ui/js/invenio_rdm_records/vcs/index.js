// This file is part of InvenioRdmRecords
// Copyright (C) 2026 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
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
