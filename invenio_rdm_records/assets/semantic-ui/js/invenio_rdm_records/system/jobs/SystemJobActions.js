/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 * Copyright (C) 2024 KTH Royal Institute of Technology.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

export class SystemJobActions extends Component {
  constructor(props) {
    super(props);
  }

  handleAction = async (action) => {
    const actionConfig = {
      restore: {
        label: i18next.t("Settings"),
        icon: "cogwheel",
        notificationTitle: i18next.t("Settings"),
      },
      block: {
        label: i18next.t("Schedule"),
        icon: "calendar",
        notificationTitle: i18next.t("Schedule"),
      },
      deactivate: {
        label: i18next.t("Run now"),
        icon: "pause",
        notificationTitle: i18next.t("Run now"),
      },
    }[action];
  };

  render() {
    const actionItems = [
      { key: "settings", label: "Settings", icon: "cog" },
      { key: "schedule", label: "Schedule", icon: "calendar" },
      { key: "run", label: "Run now", icon: "play" },
    ];

    const generateActions = () => {
      return (
        <>
          {actionItems.map((actionItem) => (
            <Button key={actionItem.key} icon fluid basic labelPosition="left">
              <Icon name={actionItem.icon} />
              {i18next.t(actionItem.label)}
            </Button>
          ))}
        </>
      );
    };

    return (
      <div>
        <Button.Group basic widths={5} compact className="margined">
          {generateActions()}
        </Button.Group>
      </div>
    );
  }
}

SystemJobActions.propTypes = {};

SystemJobActions.defaultProps = {};
