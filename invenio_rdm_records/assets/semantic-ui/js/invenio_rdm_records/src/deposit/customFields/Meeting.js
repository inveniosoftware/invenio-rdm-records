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

class MeetingComponent extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      title,
      acronym,
      dates,
      place,
      url,
      session,
      session_part: sessionPart,
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
              fieldPath={`${fieldPath}.acronym`}
              label={acronym.label}
              placeholder={acronym.placeholder}
              helpText={acronym.description}
            />
          </Grid.Column>
          <Grid.Column width="12">
            <InputComponent
              fieldPath={`${fieldPath}.place`}
              label={place.label}
              placeholder={place.placeholder}
              helpText={place.description}
            />
          </Grid.Column>
          <Grid.Column width="4">
            <InputComponent
              fieldPath={`${fieldPath}.dates`}
              label={dates.label}
              placeholder={dates.placeholder}
              helpText={dates.description}
            />
          </Grid.Column>
          <Grid.Column width="6">
            <InputComponent
              fieldPath={`${fieldPath}.session`}
              label={session.label}
              placeholder={session.placeholder}
              helpText={session.description}
            />
          </Grid.Column>
          <Grid.Column width="6">
            <InputComponent
              fieldPath={`${fieldPath}.session_part`}
              label={sessionPart.label}
              placeholder={sessionPart.placeholder}
              helpText={sessionPart.description}
            />
          </Grid.Column>
          {url && (
            <Grid.Column width="12">
              <InputComponent
                fieldPath={`${fieldPath}.url`}
                label={url.label}
                placeholder={url.placeholder}
                helpText={url.description}
              />
            </Grid.Column>
          )}
        </Grid>
      </>
    );
  }
}

MeetingComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  title: PropTypes.object.isRequired,
  acronym: PropTypes.object.isRequired,
  session_part: PropTypes.object.isRequired,
  session: PropTypes.object.isRequired,
  dates: PropTypes.object.isRequired,
  place: PropTypes.object.isRequired,
  labelIcon: PropTypes.string,
  label: PropTypes.string,
  url: PropTypes.object.isRequired,
};

MeetingComponent.defaultProps = {
  labelIcon: undefined,
  label: undefined,
};

export const Meeting = showHideOverridableWithDynamicId(MeetingComponent);
