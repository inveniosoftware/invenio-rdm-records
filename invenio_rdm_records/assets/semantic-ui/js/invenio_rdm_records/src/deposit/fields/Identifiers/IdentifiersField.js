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
  showHideOverridable,
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
      optimized,
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
        optimized={optimized}
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
              <GroupField>
                <TextField
                  fieldPath={`${fieldPathPrefix}.identifier`}
                  label={i18next.t("Identifier")}
                  required
                  width={11}
                  placeholder={placeholder}
                />
                {schemeOptions && (
                  <SelectField
                    fieldPath={`${fieldPathPrefix}.scheme`}
                    label={i18next.t("Scheme")}
                    aria-label={i18next.t("Scheme")}
                    options={schemeOptions}
                    optimized={optimized}
                    required
                    width={5}
                  />
                )}
                {!schemeOptions && (
                  <TextField
                    fieldPath={`${fieldPathPrefix}.scheme`}
                    label={i18next.t("Scheme")}
                    aria-label={i18next.t("Scheme")}
                    required
                    width={5}
                  />
                )}

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

IdentifiersFieldComponent.propTypes = {
  schemeOptions: PropTypes.arrayOf(
    PropTypes.shape({
      text: PropTypes.string,
      value: PropTypes.string,
    })
  ),
  showEmptyValue: PropTypes.bool,
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

IdentifiersFieldComponent.defaultProps = {
  label: i18next.t("Identifiers"),
  labelIcon: "barcode",
  required: false,
  schemeOptions: undefined,
  showEmptyValue: false,
  optimized: true,
};

export const IdentifiersField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.IdentifiersField",
  IdentifiersFieldComponent
);
