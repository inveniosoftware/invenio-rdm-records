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
import { TextField, GroupField, ArrayField, FieldLabel } from "react-invenio-forms";
import { Button, Form } from "semantic-ui-react";
import { emptyReference } from "./initialValues";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import {
  createCommonDepositFieldComponent,
  fieldCommonProps,
} from "../common/fieldComponents";

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
      >
        <ArrayField
          addButtonLabel={addButtonLabel}
          defaultNewValue={emptyReference}
          fieldPath={fieldPath}
          label={
            <Overridable
              id="InvenioRdmRecords.DepositForm.ReferencesField.Label"
              labelIcon={labelIcon}
              label={label}
            >
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            </Overridable>
          }
          required={required}
          disabled={disabled}
          showEmptyValue={showEmptyValue}
          helpText={helpText}
        >
          {({ arrayHelpers, indexPath }) => {
            const fieldPathPrefix = `${fieldPath}.${indexPath}`;

            return (
              <Overridable
                id="InvenioRdmRecords.DepositForm.ReferencesField.Item"
                optimized
              >
                <GroupField optimized>
                  <Overridable
                    id="InvenioRdmRecords.DepositForm.ReferencesField.Reference.Field"
                    required
                    width={16}
                  >
                    <TextField
                      fieldPath={`${fieldPathPrefix}.reference`}
                      label={i18next.t("Reference string")}
                      required
                      width={16}
                    />
                  </Overridable>

                  <Overridable
                    id="InvenioRdmRecords.DepositForm.ReferencesField.Remove.Container"
                    icon="close"
                  >
                    <Form.Field>
                      <Button
                        aria-label={i18next.t("Remove field")}
                        className="close-btn"
                        icon="close"
                        onClick={() => arrayHelpers.remove(indexPath)}
                      />
                    </Form.Field>
                  </Overridable>
                </GroupField>
              </Overridable>
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
  ...fieldCommonProps,
};

ReferencesFieldComponent.defaultProps = {
  label: i18next.t("References"),
  labelIcon: "bookmark",
  required: false,
  showEmptyValue: false,
  addButtonLabel: i18next.t("Add reference"),
};

export const ReferencesField = createCommonDepositFieldComponent(
  "InvenioRdmRecords.DepositForm.ReferencesField",
  ReferencesFieldComponent
);
