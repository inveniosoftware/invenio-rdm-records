// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
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

class ThesisComponent extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      university,
      department,
      type,
      date_submitted: dateSubmitted,
      date_defended: dateDefended,
      labelIcon,
      label,
    } = this.props;
    // For backwards compability added conditional rendering for fields; it is based on their definition in the props in THESIS_CUSTOM_FIELDS_UI
    const uniWidth = department && type ? 6 : 16;
    return (
      <>
        {label && (
          <>
            <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            <Divider fitted />
          </>
        )}
        <Grid padded>
          {university && (
            <Grid.Column width={uniWidth}>
              <InputComponent
                fieldPath={`${fieldPath}.university`}
                label={university.label}
                placeholder={university.placeholder}
                helpText={university.description}
              />
            </Grid.Column>
          )}

          {department && (
            <Grid.Column width={6}>
              <InputComponent
                fieldPath={`${fieldPath}.department`}
                label={department.label}
                placeholder={department.placeholder}
                helpText={department.description}
              />
            </Grid.Column>
          )}

          {type && (
            <Grid.Column width={4}>
              <InputComponent
                fieldPath={`${fieldPath}.type`}
                label={type.label}
                placeholder={type.placeholder}
                helpText={type.description}
              />
            </Grid.Column>
          )}
          <Grid.Column width="8">
            <InputComponent
              fieldPath={`${fieldPath}.date_submitted`}
              label={dateSubmitted.label}
              placeholder={dateSubmitted.placeholder}
              helpText={dateSubmitted.description}
            />
          </Grid.Column>
          <Grid.Column width="8">
            <InputComponent
              fieldPath={`${fieldPath}.date_defended`}
              label={dateDefended.label}
              placeholder={dateDefended.placeholder}
              helpText={dateDefended.description}
            />
          </Grid.Column>
        </Grid>
      </>
    );
  }
}

ThesisComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  university: PropTypes.object.isRequired,
  department: PropTypes.object.isRequired,
  type: PropTypes.object.isRequired,
  date_submitted: PropTypes.object.isRequired,
  date_defended: PropTypes.object.isRequired,
  labelIcon: PropTypes.string,
  label: PropTypes.string,
};

ThesisComponent.defaultProps = {
  labelIcon: undefined,
  label: undefined,
};

export const Thesis = showHideOverridableWithDynamicId(ThesisComponent);
