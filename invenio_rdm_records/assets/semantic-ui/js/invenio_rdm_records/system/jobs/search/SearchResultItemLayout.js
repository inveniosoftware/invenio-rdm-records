/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { BoolFormatter, DateFormatter } from "@js/invenio_administration";
import { SystemJobActions } from "../SystemJobActions";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Table, Dropdown, Icon } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { UserListItemCompact } from "react-invenio-forms";

class SearchResultItemComponent extends Component {
  render() {
    const { result } = this.props;

    return (
      <Table.Row>
        <Table.Cell
          key={`job-name-${result.name}`}
          data-label={i18next.t("Name")}
          collapsing
          className="word-break-all"
        >
          <a href={result.links.admin_self_html}>{result.name}</a>
        </Table.Cell>
        <Table.Cell
          key={`job-last-run-${result.last_run_start_time}`}
          data-label={i18next.t("Last run")}
          collapsing
          className=""
        >
          {result.last_run_start_time}
        </Table.Cell>
        <Table.Cell
          collapsing
          key={`job-status${result.status}`}
          data-label={i18next.t("Next run")}
          className="word-break-all"
        >
          <BoolFormatter
            tooltip={i18next.t("Status")}
            icon="check"
            color="green"
            value={result.last_run_status === "Success"}
          />
          <BoolFormatter
            tooltip={i18next.t("Status")}
            icon="ban"
            color="red"
            value={result.last_run_status === "Failed"}
          />
        </Table.Cell>
        <Table.Cell
          key={`job-user-${result.user.id}`}
          data-label={i18next.t("Started by")}
          collapsing
          className="word-break-all"
        >
          <UserListItemCompact user={result.user} id={result.user.id} />
        </Table.Cell>
        <Table.Cell
          collapsing
          key={`job-next-run${result.next_run}`}
          data-label={i18next.t("Next run")}
          className="word-break-all"
        >
          {result.next_run}
        </Table.Cell>
        <Table.Cell collapsing>
          <SystemJobActions />
        </Table.Cell>
      </Table.Row>
    );
  }
}

SearchResultItemComponent.propTypes = {
  result: PropTypes.object.isRequired,
};

SearchResultItemComponent.defaultProps = {};

export const SearchResultItemLayout = withState(SearchResultItemComponent);
