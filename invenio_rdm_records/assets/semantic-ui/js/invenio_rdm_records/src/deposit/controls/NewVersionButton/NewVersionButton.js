// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2024 CERN.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import React, { useState } from "react";
import { http } from "react-invenio-forms";
import { Icon, Button, Popup } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";

export const NewVersionButton = ({ onError, record, disabled, ...uiProps }) => {
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
  );
};

NewVersionButton.propTypes = {
  onError: PropTypes.func.isRequired,
  record: PropTypes.object.isRequired,
  disabled: PropTypes.bool,
};

NewVersionButton.defaultProps = {
  disabled: false,
};
