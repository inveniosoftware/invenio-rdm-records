/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { ProtectionButtons } from "./ProtectionButtons";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Card } from "semantic-ui-react";

export const FilesAccess = ({ access, accessCommunity, metadataOnly = false }) => {
  const publicFiles = access.files === "public";
  const publicMetadata = access.record === "public";
  const publicCommunity = accessCommunity === "public";

  const fullRecordRestricted = !publicCommunity || !publicMetadata;
  const filesRestricted = publicCommunity && !publicFiles && publicMetadata;

  const filesButtonsDisplayed = !metadataOnly && publicCommunity && publicMetadata;

  if (metadataOnly) {
    return (
      <Card.Meta data-testid="access-files">
        <em>{i18next.t("The record has no files.")}</em>
      </Card.Meta>
    );
  }

  return (
    <div data-testid="access-files">
      {filesButtonsDisplayed && (
        <>
          {i18next.t("Files only")}
          <ProtectionButtons
            active={publicFiles}
            disable={!publicCommunity}
            fieldPath="access.files"
          />
        </>
      )}
      {fullRecordRestricted && (
        <Card.Description>
          <em>{i18next.t("The full record is restricted.")}</em>
        </Card.Description>
      )}
      {filesRestricted && (
        <Card.Description>
          <em>{i18next.t("The files of this record are restricted.")}</em>
        </Card.Description>
      )}
    </div>
  );
};

FilesAccess.propTypes = {
  access: PropTypes.object.isRequired,
  metadataOnly: PropTypes.bool,
  accessCommunity: PropTypes.string.isRequired,
};
