// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";

import { FieldLabel, Input } from "react-invenio-forms";
import { Divider, Grid } from "semantic-ui-react";

import PropTypes from "prop-types";

export class Journal extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      title,
      volume,
      issue,
      pages,
      issn,
      icon,
      label,
    } = this.props;
    return (
      <>
        {label && (
          <>
            <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
            <Divider fitted />
          </>
        )}
        <Grid padded>
          <Grid.Column width="12">
            <Input
              fieldPath={`${fieldPath}.title`}
              label={title.label}
              placeholder={title.placeholder}
            />
            {title.description && (
              <label className="helptext mb-0">{title.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="4">
            <Input
              fieldPath={`${fieldPath}.issn`}
              label={issn.label}
              placeholder={issn.placeholder}
            />
            {issn.description && (
              <label className="helptext mb-0">{issn.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="6">
            <Input
              fieldPath={`${fieldPath}.volume`}
              label={volume.label}
              placeholder={volume.placeholder}
            />
            {volume.description && (
              <label className="helptext mb-0">{volume.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="6">
            <Input
              fieldPath={`${fieldPath}.issue`}
              label={issue.label}
              placeholder={issue.placeholder}
            />
            {issue.description && (
              <label className="helptext mb-0">{issue.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="4">
            <Input
              fieldPath={`${fieldPath}.pages`}
              label={pages.label}
              placeholder={pages.placeholder}
            />
            {pages.description && (
              <label className="helptext mb-0">{pages.description}</label>
            )}
          </Grid.Column>
        </Grid>
      </>
    );
  }
}

Journal.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  title: PropTypes.object.isRequired,
  volume: PropTypes.object.isRequired,
  issue: PropTypes.object.isRequired,
  pages: PropTypes.object.isRequired,
  issn: PropTypes.object.isRequired,
  icon: PropTypes.string,
  label: PropTypes.string,
};

Journal.defaultProps = {
  icon: undefined,
  label: undefined,
};
