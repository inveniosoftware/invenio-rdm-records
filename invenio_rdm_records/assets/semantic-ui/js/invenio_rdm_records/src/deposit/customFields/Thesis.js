// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
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
      department,
      type,
      date_submitted: dateSubmitted,
      date_defended: dateDefended,
      icon,
      label,
    } = this.props;
    // For backwards compability added conditional rendering for fields; it is based on their definition in the props in THESIS_CUSTOM_FIELDS_UI
    const uniWidth = department && type ? 6 : 16;
    return (
      <>
        {label && (
          <>
            <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
            <Divider fitted />
          </>
        )}
        <Grid padded>
          {university && (
            <Grid.Column width={uniWidth}>
              <Input
                fieldPath={`${fieldPath}.university`}
                label={university.label}
                placeholder={university.placeholder}
              />
              {university.description && (
                <label className="helptext mb-0">{university.description}</label>
              )}
            </Grid.Column>
          )}

          {department && (
            <Grid.Column width={6}>
              <Input
                fieldPath={`${fieldPath}.department`}
                label={department.label}
                placeholder={department.placeholder}
              />
              {department.description && (
                <label className="helptext mb-0">{department.description}</label>
              )}
            </Grid.Column>
          )}

          {type && (
            <Grid.Column width={4}>
              <Input
                fieldPath={`${fieldPath}.type`}
                label={type.label}
                placeholder={type.placeholder}
              />
              {type.description && (
                <label className="helptext mb-0">{type.description}</label>
              )}
            </Grid.Column>
          )}
          <Grid.Column width="8">
            <Input
              fieldPath={`${fieldPath}.date_submitted`}
              label={dateSubmitted.label}
              placeholder={dateSubmitted.placeholder}
            />
            {dateSubmitted.description && (
              <label className="helptext mb-0">{dateSubmitted.description}</label>
            )}
          </Grid.Column>
          <Grid.Column width="8">
            <Input
              fieldPath={`${fieldPath}.date_defended`}
              label={dateDefended.label}
              placeholder={dateDefended.placeholder}
            />
            {dateDefended.description && (
              <label className="helptext mb-0">{dateDefended.description}</label>
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
  department: PropTypes.object.isRequired,
  type: PropTypes.object.isRequired,
  date_submitted: PropTypes.object.isRequired,
  date_defended: PropTypes.object.isRequired,
  icon: PropTypes.string,
  label: PropTypes.string,
};

Thesis.defaultProps = {
  icon: undefined,
  label: undefined,
};
