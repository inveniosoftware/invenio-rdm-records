/*
 * // This file is part of Invenio-Requests
 * // Copyright (C) 2023 CERN.
 * //
 * // Invenio-Requests is free software; you can redistribute it and/or modify it
 * // under the terms of the MIT License; see LICENSE file for more details.
 */

import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import PropTypes from "prop-types";
import React, { Component } from "react";

export class JobSearchLayout extends Component {
  render() {
    const { config, appName } = this.props;
    return (
      <SearchAppResultsPane layoutOptions={config.layoutOptions} appName={appName} />
    );
  }
}

JobSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

JobSearchLayout.defaultProps = {
  appName: "",
};
