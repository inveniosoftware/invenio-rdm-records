// This file is part of Invenio-RDM-Records
// Copyright (C) 2021-2024 CERN.
// Copyright (C) 2021 Northwestern University.
// Copyright (C) 2025 ZBW – Leibniz-Informationszentrum Wirtschaft.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React from "react";
import { Segment } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export function NoLicenseResults({ switchToCustom }) {
  return (
    <Segment
      basic
      content={
        <p>
          {i18next.t("Did not find your license? ")}
          <a
            href="/"
            onClick={(e) => {
              e.preventDefault();
              switchToCustom();
            }}
          >
            {i18next.t("Add a custom license.")}
          </a>
        </p>
      }
    />
  );
}

NoLicenseResults.propTypes = {
  switchToCustom: PropTypes.func.isRequired,
};
