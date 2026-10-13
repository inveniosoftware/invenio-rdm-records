/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import PropTypes from "prop-types";
import { ProtectionButtons } from "./ProtectionButtons";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import Overridable from "react-overridable";
import { DateTime } from "luxon";

export const MetadataAccess = (props) => {
  const {
    recordAccess,
    communityAccess,
    permissions,
    record,
    recordRestrictionGracePeriod,
    allowRecordRestriction,
  } = props;
  const publicMetadata = recordAccess === "public";
  const publicCommunity = communityAccess === "public";

  const isGracePeriodOver = () => {
    const createdDate = DateTime.fromISO(record.created);
    const endOfGracePeriod = createdDate.plus({ days: recordRestrictionGracePeriod });

    return endOfGracePeriod < DateTime.now();
  };

  const canRestrictRecord = () => {
    if (
      !allowRecordRestriction &&
      record?.created &&
      record?.access?.record !== "restricted" &&
      record.is_published
    ) {
      return permissions?.can_moderate || !isGracePeriodOver();
    }
    return true;
  };

  return (
    <Overridable id="ReactInvenioDeposit.MetadataAccess.layout" {...props}>
      <>
        {i18next.t("Full record")}
        <ProtectionButtons
          canRestrictRecord={canRestrictRecord()}
          record={record}
          active={publicMetadata && publicCommunity}
          disabled={!publicCommunity}
          fieldPath="access.record"
        />
      </>
    </Overridable>
  );
};

MetadataAccess.propTypes = {
  recordAccess: PropTypes.string.isRequired,
  communityAccess: PropTypes.string.isRequired,
  permissions: PropTypes.object,
  record: PropTypes.object.isRequired,
  recordRestrictionGracePeriod: PropTypes.number.isRequired,
  allowRecordRestriction: PropTypes.bool.isRequired,
};
