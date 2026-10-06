/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2025 KTH Royal Institute of Technology.
 * SPDX-FileCopyrightText: 2026 University of Münster.
 * SPDX-License-Identifier: MIT
 */

import { DateTime } from "luxon";
import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Trans } from "react-i18next";
import { Icon, Message } from "semantic-ui-react";

export const AccessMessage = ({ access, metadataOnly, accessCommunity }) => {
  const recordPublic = access.record === "public";
  const filesPublic = access.files === "public";
  const communityPublic = accessCommunity === "public";
  const embargoActive = access.embargo?.active || false;

  // restriction logic
  const fullyRestricted = !communityPublic || (!recordPublic && !embargoActive);
  const fullyPublic = communityPublic && recordPublic && (metadataOnly || filesPublic);

  const embargoedFiles = embargoActive && !filesPublic && recordPublic;
  const restrictedFiles = !embargoActive && !filesPublic && recordPublic;
  const fullEmbargo = !recordPublic && embargoActive;

  const fmtDate = access.embargo?.until
    ? DateTime.fromISO(access.embargo.until)
        .setLocale(i18next.language)
        .toLocaleString(DateTime.DATE_FULL)
    : "???";

  if (fullyPublic) {
    return (
      <Message icon positive visible data-testid="access-message">
        <Icon name="lock open" />
        <Message.Content>
          <Message.Header>{i18next.t("Public")}</Message.Header>
          {metadataOnly
            ? i18next.t("The record is publicly accessible.")
            : i18next.t("The record and files are publicly accessible.")}
        </Message.Content>
      </Message>
    );
  }

  if (fullEmbargo) {
    return (
      <Message icon warning visible data-testid="access-message">
        <Icon name="lock" />
        <Message.Content>
          <Message.Header>{i18next.t("Embargoed (full record)")}</Message.Header>
          <Trans
            defaults="On <bold>{{date}}</bold> the record will automatically be made publicly accessible. Until then, the record can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions."
            values={{ date: fmtDate }}
            components={{ bold: <b /> }}
          />
        </Message.Content>
      </Message>
    );
  }

  if (fullyRestricted) {
    return (
      <Message icon negative visible data-testid="access-message">
        <Icon name="lock" />
        <Message.Content>
          <Message.Header>{i18next.t("Restricted")}</Message.Header>
          <Trans
            defaults="The record can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions."
            components={{ bold: <b /> }}
          />
        </Message.Content>
      </Message>
    );
  }

  if (restrictedFiles) {
    return (
      <Message icon warning visible data-testid="access-message">
        <Icon name="lock" />
        <Message.Content>
          <Message.Header>{i18next.t("Public with restricted files")}</Message.Header>
          <Trans
            defaults="The record is publicly accessible. The files can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions."
            components={{ bold: <b /> }}
          />
        </Message.Content>
      </Message>
    );
  }

  if (embargoedFiles) {
    return (
      <Message icon warning visible data-testid="access-message">
        <Icon name="lock" />
        <Message.Content>
          <Message.Header>{i18next.t("Embargoed (files-only)")}</Message.Header>
          <Trans
            defaults="The record is publicly accessible. On <bold>{{date}}</bold> the files will automatically be made publicly accessible. Until then, the files can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions."
            values={{ date: fmtDate }}
            components={{ bold: <b /> }}
          />
        </Message.Content>
      </Message>
    );
  }
};

AccessMessage.propTypes = {
  access: PropTypes.object.isRequired,
  metadataOnly: PropTypes.bool,
  accessCommunity: PropTypes.string.isRequired,
};

AccessMessage.defaultProps = {
  metadataOnly: false,
};
