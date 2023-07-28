// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";

import { TextField, GroupField, ArrayField, FieldLabel } from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";

import { emptyReference } from "./initialValues";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class ReferencesField extends Component {
  render() {
    const { fieldPath, label, labelIcon, required, showEmptyValue } = this.props;

    return (
      <ArrayField
        addButtonLabel={i18next.t("Add reference")}
        defaultNewValue={emptyReference}
        fieldPath={fieldPath}
        label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
        required={required}
        showEmptyValue={showEmptyValue}
      >
        {({ arrayHelpers, indexPath }) => {
          const fieldPathPrefix = `${fieldPath}.${indexPath}`;

          return (
            <GroupField optimized>
              <TextField
                fieldPath={`${fieldPathPrefix}.reference`}
                label={i18next.t("Reference string")}
                required
                width={16}
              />

              <Form.Field>
                <Button
                  aria-label={i18next.t("Remove field")}
                  className="close-btn"
                  icon
                  onClick={() => arrayHelpers.remove(indexPath)}
                >
                  <Icon name="close" />
                </Button>
              </Form.Field>
            </GroupField>
          );
        }}
      </ArrayField>
    );
  }
}

ReferencesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  showEmptyValue: PropTypes.bool,
};

ReferencesField.defaultProps = {
  label: i18next.t("References"),
  labelIcon: "bookmark",
  required: false,
  showEmptyValue: false,
};
