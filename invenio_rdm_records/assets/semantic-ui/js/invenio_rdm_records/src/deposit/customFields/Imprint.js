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

class ImprintComponent extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      title,
      place,
      isbn,
      pages,
      edition,
      label,
      labelIcon,
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
              fieldPath={`${fieldPath}.isbn`}
              label={isbn.label}
              placeholder={isbn.placeholder}
              helpText={isbn.description}
            />
          </Grid.Column>
          <Grid.Column width="6">
            <InputComponent
              fieldPath={`${fieldPath}.place`}
              label={place.label}
              placeholder={place.placeholder}
              helpText={place.description}
            />
          </Grid.Column>
          <Grid.Column width="6">
            <InputComponent
              fieldPath={`${fieldPath}.pages`}
              label={pages.label}
              placeholder={pages.placeholder}
              helpText={pages.description}
            />
          </Grid.Column>
          <Grid.Column width="4">
            <InputComponent
              fieldPath={`${fieldPath}.edition`}
              label={edition.label}
              placeholder={edition.placeholder}
              helpText={edition.description}
            />
          </Grid.Column>
        </Grid>
      </>
    );
  }
}

ImprintComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  title: PropTypes.object.isRequired,
  place: PropTypes.object.isRequired,
  isbn: PropTypes.object.isRequired,
  pages: PropTypes.object.isRequired,
  edition: PropTypes.object.isRequired,
  labelIcon: PropTypes.string,
  label: PropTypes.string,
};

ImprintComponent.defaultProps = {
  labelIcon: undefined,
  label: undefined,
};

export const Imprint = showHideOverridableWithDynamicId(ImprintComponent);
