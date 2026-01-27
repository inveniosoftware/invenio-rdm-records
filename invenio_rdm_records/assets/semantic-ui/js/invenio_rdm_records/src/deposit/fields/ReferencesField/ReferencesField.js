// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import {
  TextField,
  GroupField,
  ArrayField,
  FieldLabel,
  showHideOverridable,
  fieldCommonProps,
} from "react-invenio-forms";
import { Button, Form } from "semantic-ui-react";
import { emptyReference } from "./initialValues";
import { i18next } from "@translations/invenio_rdm_records/i18next";

class ReferencesFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      required,
      disabled,
      showEmptyValue,
      helpText,
      addButtonLabel,
      optimized,
    } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.ReferencesField.Container"
        defaultNewValue={emptyReference}
        required={required}
        disabled={disabled}
        showEmptyValue={showEmptyValue}
        helpText={helpText}
        addButtonLabel={addButtonLabel}
        optimized={optimized}
      >
        <ArrayField
          addButtonLabel={addButtonLabel}
          defaultNewValue={emptyReference}
          fieldPath={fieldPath}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          required={required}
          disabled={disabled}
          showEmptyValue={showEmptyValue}
          helpText={helpText}
        >
          {({ arrayHelpers, indexPath }) => {
            const fieldPathPrefix = `${fieldPath}.${indexPath}`;

            return (
              <GroupField optimized={optimized}>
                <TextField
                  fieldPath={`${fieldPathPrefix}.reference`}
                  label={i18next.t("Reference string")}
                  required
                  width={16}
                  optimized={optimized}
                />

                <Form.Field>
                  <Button
                    aria-label={i18next.t("Remove field")}
                    className="close-btn"
                    icon="close"
                    type="button"
                    onClick={() => arrayHelpers.remove(indexPath)}
                  />
                </Form.Field>
              </GroupField>
            );
          }}
        </ArrayField>
      </Overridable>
    );
  }
}

ReferencesFieldComponent.propTypes = {
  showEmptyValue: PropTypes.bool,
  addButtonLabel: PropTypes.string,
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

ReferencesFieldComponent.defaultProps = {
  label: i18next.t("References"),
  labelIcon: "bookmark",
  required: false,
  showEmptyValue: false,
  addButtonLabel: i18next.t("Add reference"),
  optimized: true,
};

export const ReferencesField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.ReferencesField",
  ReferencesFieldComponent
);
