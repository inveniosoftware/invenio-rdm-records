/*
 * SPDX-FileCopyrightText: 2020-2024 CERN.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import React, { useState } from "react";
import { http, showHideOverridable } from "react-invenio-forms";
import { Icon, Button, Popup } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import Overridable from "react-overridable";

const NewVersionButtonComponent = ({ onError, record, disabled, ...uiProps }) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);

    try {
      const response = await http.post(record.links.versions);
      window.location = response.data.links.self_html;
    } catch (error) {
      console.error(error);
      setLoading(false);
      onError(error.response.data.message);
    }
  };

  return (
    <Overridable
      id="InvenioRdmRecords.RecordLandingPage.RecordManagement.NewVersionButton.container"
      onError={onError}
      record={record}
      disabled={disabled}
    >
      <Popup
        content={i18next.t("You don't have permissions to create a new version.")}
        position="top center"
        disabled={!disabled}
        trigger={
          // Extra span needed since disabled buttons do not trigger hover events
          <span>
            <Button
              type="button"
              positive
              size="mini"
              onClick={handleClick}
              loading={loading}
              icon
              labelPosition="left"
              disabled={disabled}
              {...uiProps}
            >
              <Icon name="tag" />
              {i18next.t("New version")}
            </Button>
          </span>
        }
      />
    </Overridable>
  );
};

NewVersionButtonComponent.propTypes = {
  onError: PropTypes.func.isRequired,
  record: PropTypes.object.isRequired,
  disabled: PropTypes.bool,
};

NewVersionButtonComponent.defaultProps = {
  disabled: false,
};

export const NewVersionButton = showHideOverridable(
  "InvenioRdmRecords.RecordLandingPage.RecordManagement.NewVersionButton",
  NewVersionButtonComponent
);
