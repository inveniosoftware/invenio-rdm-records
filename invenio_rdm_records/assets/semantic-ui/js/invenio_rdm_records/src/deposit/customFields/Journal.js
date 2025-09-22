// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";

import {
  FieldLabel,
  InputComponent,
  showHideOverridableWithDynamicId,
} from "react-invenio-forms";
import { Divider, Grid } from "semantic-ui-react";

import PropTypes from "prop-types";

class JournalComponent extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      title,
      volume,
      issue,
      pages,
      issn,
      labelIcon,
      label,
    } = this.props;
    return (
      <>
        {label && (
          <>
            <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            <Divider fitted />
          </>
        )}
        <Grid padded>
          <Grid.Column width="12">
            <InputComponent
              fieldPath={`${fieldPath}.title`}
              label={title.label}
              placeholder={title.placeholder}
              helpText={title.description}
            />
          </Grid.Column>
          <Grid.Column width="4">
            <InputComponent
              fieldPath={`${fieldPath}.issn`}
              label={issn.label}
              placeholder={issn.placeholder}
              helpText={issn.description}
            />
          </Grid.Column>
          <Grid.Column width="6">
            <InputComponent
              fieldPath={`${fieldPath}.volume`}
              label={volume.label}
              placeholder={volume.placeholder}
              helpText={volume.description}
            />
          </Grid.Column>
          <Grid.Column width="6">
            <InputComponent
              fieldPath={`${fieldPath}.issue`}
              label={issue.label}
              placeholder={issue.placeholder}
              helpText={issue.description}
            />
          </Grid.Column>
          <Grid.Column width="4">
            <InputComponent
              fieldPath={`${fieldPath}.pages`}
              label={pages.label}
              placeholder={pages.placeholder}
              helpText={pages.description}
            />
          </Grid.Column>
        </Grid>
      </>
    );
  }
}

JournalComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  title: PropTypes.object.isRequired,
  volume: PropTypes.object.isRequired,
  issue: PropTypes.object.isRequired,
  pages: PropTypes.object.isRequired,
  issn: PropTypes.object.isRequired,
  labelIcon: PropTypes.string,
  label: PropTypes.string,
};

JournalComponent.defaultProps = {
  labelIcon: undefined,
  label: undefined,
};

export const Journal = showHideOverridableWithDynamicId(JournalComponent);
