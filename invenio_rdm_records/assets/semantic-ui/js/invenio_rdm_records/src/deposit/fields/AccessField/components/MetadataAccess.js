// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

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
      return !isGracePeriodOver();
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
  record: PropTypes.object.isRequired,
  recordRestrictionGracePeriod: PropTypes.number.isRequired,
  allowRecordRestriction: PropTypes.bool.isRequired,
};
