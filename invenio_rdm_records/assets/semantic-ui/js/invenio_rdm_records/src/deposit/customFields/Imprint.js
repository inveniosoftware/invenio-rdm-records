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

export class Imprint extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      title,
      place,
      isbn,
      pages,
      edition,
      label,
      icon,
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
              fieldPath={`${fieldPath}.isbn`}
              label={isbn.label}
              placeholder={isbn.placeholder}
            />
            {isbn.description && (
              <label className="helptext mb-0">{isbn.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="6">
            <Input
              fieldPath={`${fieldPath}.place`}
              label={place.label}
              placeholder={place.placeholder}
            />
            {place.description && (
              <label className="helptext mb-0">{place.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="6">
            <Input
              fieldPath={`${fieldPath}.pages`}
              label={pages.label}
              placeholder={pages.placeholder}
            />
            {pages.description && (
              <label className="helptext mb-0">{pages.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="4">
            <Input
              fieldPath={`${fieldPath}.edition`}
              label={edition.label}
              placeholder={edition.placeholder}
            />
            {edition.description && (
              <label className="helptext mb-0">{edition.description}</label>
            )}
          </Grid.Column>
        </Grid>
      </>
    );
  }
}

Imprint.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  title: PropTypes.object.isRequired,
  place: PropTypes.object.isRequired,
  isbn: PropTypes.object.isRequired,
  pages: PropTypes.object.isRequired,
  edition: PropTypes.object.isRequired,
  icon: PropTypes.string,
  label: PropTypes.string,
};

Imprint.defaultProps = {
  icon: undefined,
  label: undefined,
};
