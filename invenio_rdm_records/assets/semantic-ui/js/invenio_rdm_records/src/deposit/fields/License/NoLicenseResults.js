/*
 * SPDX-FileCopyrightText: 2021-2024 CERN.
 * SPDX-FileCopyrightText: 2021 Northwestern University.
 * SPDX-FileCopyrightText: 2025 ZBW – Leibniz-Informationszentrum Wirtschaft.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";

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
