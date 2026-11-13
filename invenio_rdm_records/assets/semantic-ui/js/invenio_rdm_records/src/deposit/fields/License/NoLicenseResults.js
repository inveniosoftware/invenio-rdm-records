/*
 * SPDX-FileCopyrightText: 2021-2024 CERN.
 * SPDX-FileCopyrightText: 2021 Northwestern University.
 * SPDX-FileCopyrightText: 2025 ZBW – Leibniz-Informationszentrum Wirtschaft.
 * SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Trans } from "react-i18next";
import PropTypes from "prop-types";

import { Segment } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export function NoLicenseResults({ switchToCustom }) {
  return (
    <Segment
      basic
      content={
        <p>
          <Trans
            i18n={i18next}
            defaults={
              "Did not find your license? <customLink>Add a custom license.</customLink>"
            }
            components={{
              customLink: (
                <a
                  href="/"
                  onClick={(e) => {
                    e.preventDefault();
                    switchToCustom();
                  }}
                />
              ),
            }}
          />
        </p>
      }
    />
  );
}

NoLicenseResults.propTypes = {
  switchToCustom: PropTypes.func.isRequired,
};
