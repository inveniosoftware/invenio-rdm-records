// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import {
  ArrayField,
  GroupField,
  SelectField,
  TextField,
  createCommonDepositFieldComponent,
  fieldCommonProps,
} from "react-invenio-forms";
import { Button, Form } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { emptyIdentifier } from "./initialValues";
import Overridable from "react-overridable";

class IdentifiersFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      required,
      disabled,
      schemeOptions,
      showEmptyValue,
      helpText,
      placeholder,
    } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.IdentifiersField.Container"
        defaultNewValue={emptyIdentifier}
        labelIcon={labelIcon}
        label={label}
        required={required}
        disabled={disabled}
        showEmptyValue={showEmptyValue}
        options={schemeOptions}
        placeholder={placeholder}
      >
        <ArrayField
          addButtonLabel={i18next.t("Add identifier")}
          defaultNewValue={emptyIdentifier}
          fieldPath={fieldPath}
          label={label}
          labelIcon={labelIcon}
          helpText={helpText}
          required={required}
          disabled={disabled}
          showEmptyValue={showEmptyValue}
        >
          {({ arrayHelpers, indexPath }) => {
            const fieldPathPrefix = `${fieldPath}.${indexPath}`;
            return (
              <Overridable
                id="InvenioRdmRecords.DepositForm.IdentifiersField.Item"
                optimized={false}
                placeholder={placeholder}
              >
                <GroupField>
                  <Overridable
                    id="InvenioRdmRecords.DepositForm.IdentifiersField.Identifier.Field"
                    required
                    width={11}
                    placeholder={placeholder}
                  >
                    <TextField
                      fieldPath={`${fieldPathPrefix}.identifier`}
                      label={i18next.t("Identifier")}
                      required
                      width={11}
                      placeholder={placeholder}
                    />
                  </Overridable>
                  {schemeOptions && (
                    <Overridable
                      id="InvenioRdmRecords.DepositForm.IdentifiersField.Scheme.Select"
                      options={schemeOptions}
                      optimized
                      required
                      width={5}
                    >
                      <SelectField
                        fieldPath={`${fieldPathPrefix}.scheme`}
                        label={i18next.t("Scheme")}
                        aria-label={i18next.t("Scheme")}
                        options={schemeOptions}
                        optimized
                        required
                        width={5}
                      />
                    </Overridable>
                  )}
                  {!schemeOptions && (
                    <Overridable
                      id="InvenioRdmRecords.DepositForm.IdentifiersField.Scheme.Text"
                      required
                      width={5}
                    >
                      <TextField
                        fieldPath={`${fieldPathPrefix}.scheme`}
                        label={i18next.t("Scheme")}
                        aria-label={i18next.t("Scheme")}
                        required
                        width={5}
                      />
                    </Overridable>
                  )}

                  <Overridable
                    id="InvenioRdmRecords.DepositForm.IdentifiersField.Remove.Container"
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

IdentifiersFieldComponent.propTypes = {
  schemeOptions: PropTypes.arrayOf(
    PropTypes.shape({
      text: PropTypes.string,
      value: PropTypes.string,
    })
  ),
  showEmptyValue: PropTypes.bool,
  ...fieldCommonProps,
};

IdentifiersFieldComponent.defaultProps = {
  label: i18next.t("Identifiers"),
  labelIcon: "barcode",
  required: false,
  schemeOptions: undefined,
  showEmptyValue: false,
};

export const IdentifiersField = createCommonDepositFieldComponent(
  "InvenioRdmRecords.DepositForm.IdentifiersField",
  IdentifiersFieldComponent
);
