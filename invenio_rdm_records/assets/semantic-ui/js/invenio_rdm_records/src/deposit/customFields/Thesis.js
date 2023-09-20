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

export class Thesis extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      university,
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
          <Grid.Column width="16">
            <Input
              fieldPath={fieldPath}
              label={university.label}
              placeholder={university.placeholder}
            />
            {university.description && (
              <label className="helptext mb-0">{university.description}</label>
            )}
          </Grid.Column>
        </Grid>
      </>
    );
  }
}

Thesis.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  university: PropTypes.object.isRequired,
  icon: PropTypes.string,
  label: PropTypes.string,
};

Thesis.defaultProps = {
  icon: undefined,
  label: undefined,
};
