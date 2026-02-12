// This file is part of InvenioRdmRecords
// Copyright (C) 2026 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import React, { useCallback, useEffect, useState } from "react";
import PropTypes from "prop-types";
import { sendEnableDisableRequest } from "./api";
import { CommunitySelectionModalComponent } from "../src/deposit/components/CommunitySelectionModal/CommunitySelectionModal.js";
import { i18next } from "@translations/invenio_rdm_records/i18next";

const getRepositoryItemContainer = (repoSwitchElement) => {
  let currentEl = repoSwitchElement.parentElement;
  while (!currentEl.classList.contains("repository-item") || currentEl === null) {
    currentEl = currentEl.parentElement;
  }
  return currentEl;
};

export const VCSCommunitiesApp = ({ communityRequiredToPublish }) => {
  const [selectedRepoSwitch, setSelectedRepoSwitch] = useState(null);

  useEffect(() => {
    const repoSwitchElements = document.getElementsByClassName(
      "repo-switch-with-communities"
    );

    const toggleListener = (event) => {
      if (communityRequiredToPublish && event.target.checked) {
        // If the instance requires communities, we need to ask the user's community of choice
        // before sending the request to enable the repo.
        setSelectedRepoSwitch(event.target);
        return;
      }

      sendEnableDisableRequest(
        event.target.checked,
        getRepositoryItemContainer(event.target)
      );
    };

    for (const repoSwitchElement of repoSwitchElements) {
      repoSwitchElement.addEventListener("change", toggleListener);
    }

    return () => {
      for (const repoSwitchElement of repoSwitchElements) {
        repoSwitchElement.removeEventListener("change", toggleListener);
      }
    };
  }, [communityRequiredToPublish]);

  const onCommunitySelect = useCallback(
    (community) => {
      if (selectedRepoSwitch === null) return;
      sendEnableDisableRequest(
        true,
        getRepositoryItemContainer(selectedRepoSwitch),
        community.id
      );
      setSelectedRepoSwitch(null);
    },
    [selectedRepoSwitch]
  );

  const onModalClose = useCallback(() => {
    if (selectedRepoSwitch === null) return;
    // Uncheck the box so the user can clearly see the repo wasn't enabled
    selectedRepoSwitch.checked = false;
    setSelectedRepoSwitch(null);
  }, [selectedRepoSwitch]);

  if (!selectedRepoSwitch) return null;

  return (
    <CommunitySelectionModalComponent
      modalOpen
      onCommunityChange={onCommunitySelect}
      // This prop isn't used seemingly, but we need a default value
      userCommunitiesMemberships={{}}
      modalHeader={i18next.t("Select a community for this repository's records")}
      onModalChange={onModalClose}
      handleClose={onModalClose}
      isInitialSubmission
    />
  );
};

VCSCommunitiesApp.propTypes = {
  communityRequiredToPublish: PropTypes.bool,
};

VCSCommunitiesApp.defaultProps = {
  communityRequiredToPublish: false,
};
