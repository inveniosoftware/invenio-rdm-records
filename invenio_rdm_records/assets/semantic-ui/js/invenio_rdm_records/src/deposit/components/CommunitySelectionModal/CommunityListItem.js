// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import React, { useContext } from "react";
import { Button, Icon, Label } from "semantic-ui-react";
import { CommunityCompactItem } from "@js/invenio_communities/community";
import { CommunityContext } from "./CommunityContext";
import { InvenioPopup } from "react-invenio-forms";

export const CommunityListItem = ({ result, record }) => {
  const {
    setLocalCommunity,
    getChosenCommunity,
    userCommunitiesMemberships,
    displaySelected,
  } = useContext(CommunityContext);

  const { metadata } = result;
  const itemSelected = getChosenCommunity()?.id === result.id;
  const userMembership = userCommunitiesMemberships[result["id"]];
  const invalidPermissionLevel =
    record.access.record === "public" && result.access.visibility === "restricted";

  const actions = (
    <>
      {invalidPermissionLevel && (
        <InvenioPopup
          popupId="community-inclusion-info-popup"
          size="small"
          trigger={
            <Icon className="mb-5" color="grey" name="question circle outline" />
          }
          ariaLabel={i18next.t("Community inclusion information")}
          content={i18next.t(
            "Submission to this community is only allowed if the record is restricted."
          )}
        />
      )}
      <Button
        content={
          displaySelected && itemSelected ? i18next.t("Selected") : i18next.t("Select")
        }
        size="tiny"
        positive={displaySelected && itemSelected}
        onClick={() => setLocalCommunity(result)}
        disabled={invalidPermissionLevel}
        aria-label={i18next.t("Select {{title}}", { title: metadata.title })}
      />
    </>
  );

  const extraLabels = userMembership && (
    <Label size="small" horizontal color="teal">
      <Icon name="key" />
      {_capitalize(userMembership)}
    </Label>
  );

  return (
    <CommunityCompactItem
      result={result}
      actions={actions}
      extraLabels={extraLabels}
      showPermissionLabel
    />
  );
};

CommunityListItem.propTypes = {
  result: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
};
