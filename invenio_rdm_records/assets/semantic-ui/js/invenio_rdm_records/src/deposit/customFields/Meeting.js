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

export class Meeting extends Component {
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
              fieldPath={`${fieldPath}.acronym`}
              label={acronym.label}
              placeholder={acronym.placeholder}
            />
            {acronym.description && (
              <label className="helptext mb-0">{acronym.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="12">
            <Input
              fieldPath={`${fieldPath}.place`}
              label={place.label}
              placeholder={place.placeholder}
            />
            {place.description && (
              <label className="helptext mb-0">{place.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="4">
            <Input
              fieldPath={`${fieldPath}.dates`}
              label={dates.label}
              placeholder={dates.placeholder}
            />
            {dates.description && (
              <label className="helptext mb-0">{dates.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="12">
            <Input
              fieldPath={`${fieldPath}.url`}
              label={url.label}
              placeholder={url.placeholder}
            />
            {url.description && (
              <label className="helptext mb-0">{url.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="6">
            <Input
              fieldPath={`${fieldPath}.session`}
              label={session.label}
              placeholder={session.placeholder}
            />
            {session.description && (
              <label className="helptext mb-0">{session.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="6">
            <Input
              fieldPath={`${fieldPath}.session_part`}
              label={sessionPart.label}
              placeholder={sessionPart.placeholder}
            />
            {sessionPart.description && (
              <label className="helptext mb-0">{sessionPart.description}</label>
            )}
          </Grid.Column>
        </Grid>
      </>
    );
  }
}

Meeting.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  title: PropTypes.object.isRequired,
  acronym: PropTypes.object.isRequired,
  session_part: PropTypes.object.isRequired,
  session: PropTypes.object.isRequired,
  url: PropTypes.object.isRequired,
  dates: PropTypes.object.isRequired,
  place: PropTypes.object.isRequired,
  icon: PropTypes.string,
  label: PropTypes.string,
};

Meeting.defaultProps = {
  icon: undefined,
  label: undefined,
};
