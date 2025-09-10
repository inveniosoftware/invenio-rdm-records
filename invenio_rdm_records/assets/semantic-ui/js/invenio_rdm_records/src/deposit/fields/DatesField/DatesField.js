// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2024 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  ArrayField,
  GroupField,
  SelectField,
  TextField,
  showHideOverridable,
  fieldCommonProps,
} from "react-invenio-forms";
import { Button, Form } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _matches from "lodash/matches";
import _filter from "lodash/filter";
import _isEqual from "lodash/isEqual";
import _has from "lodash/has";
import { emptyDate } from "./initialValues";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { sortOptions } from "../../utils";
import Overridable from "react-overridable";

class DatesFieldComponent extends Component {
  /** Top-level Dates Component */

  /**
   * Returns the required option if the current value passed does match it
   * @param  {Object} currentValue The current value
   * @param  {Array} arrayOfValues The array of values for the field
   * @return {Object} The required option if any
   */
  getRequiredOption = (currentValue, arrayOfValues) => {
    const { requiredOptions } = this.props;
    for (const requiredOption of requiredOptions) {
      // If more values matched we do take the first value
      const matchingValue = _filter(arrayOfValues, _matches(requiredOption))[0];
      if (_isEqual(matchingValue, currentValue)) {
        return requiredOption;
      }
    }
    return null;
  };

  render() {
    const {
      fieldPath,
      options,
      label,
      labelIcon,
      required,
      requiredOptions,
      showEmptyValue,
      placeholder,
      helpText,
      addButtonLabel,
      optimized,
    } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.DatesField.Container"
        fieldPath={fieldPath}
        defaultNewValue={emptyDate}
        label={label}
        labelIcon={labelIcon}
        required={required}
        requiredOptions={requiredOptions}
        showEmptyValue={showEmptyValue}
        placeholder={placeholder}
        helpText={helpText}
        addButtonLabel={addButtonLabel}
        optimized={optimized}
      >
        <ArrayField
          addButtonLabel={addButtonLabel}
          defaultNewValue={emptyDate}
          fieldPath={fieldPath}
          helpText={helpText}
          label={label}
          labelIcon={labelIcon}
          required={required}
          requiredOptions={requiredOptions}
          showEmptyValue={showEmptyValue}
        >
          {({ array, arrayHelpers, indexPath, value }) => {
            const fieldPathPrefix = `${fieldPath}.${indexPath}`;
            const requiredOption = this.getRequiredOption(value, array);
            const hasRequiredDateValue = _has(requiredOption, "date");
            const hasRequiredTypeValue = _has(requiredOption, "type");
            const hasRequiredDescriptionValue = _has(requiredOption, "description");
            return (
              <GroupField fieldPath={fieldPath} optimized={optimized}>
                <Overridable
                  id="InvenioRdmRecords.DepositForm.DatesField.DateField"
                  fieldPath={`${fieldPathPrefix}.date`}
                >
                  <TextField
                    fieldPath={`${fieldPathPrefix}.date`}
                    label={i18next.t("Date")}
                    placeholder={placeholder}
                    disabled={hasRequiredDateValue}
                    required
                    width={5}
                  />
                </Overridable>
                <Overridable
                  id="InvenioRdmRecords.DepositForm.DatesField.TypeField"
                  fieldPath={`${fieldPathPrefix}.type`}
                >
                  <SelectField
                    fieldPath={`${fieldPathPrefix}.type`}
                    label={i18next.t("Type")}
                    aria-label={i18next.t("Type")}
                    options={sortOptions(options.type)}
                    disabled={hasRequiredTypeValue}
                    required
                    width={5}
                    optimized={optimized}
                  />
                </Overridable>
                <Overridable
                  id="InvenioRdmRecords.DepositForm.DatesField.DescriptionField"
                  disabled={hasRequiredDescriptionValue}
                  width={5}
                >
                  <TextField
                    fieldPath={`${fieldPathPrefix}.description`}
                    label={i18next.t("Description")}
                    disabled={hasRequiredDescriptionValue}
                    width={5}
                  />
                </Overridable>
                <Overridable id="InvenioRdmRecords.DepositForm.DatesField.RemoveButton">
                  <Form.Field>
                    <Button
                      aria-label={i18next.t("Remove field")}
                      className="close-btn"
                      disabled={!_isEmpty(requiredOption)}
                      icon="close"
                      onClick={() => arrayHelpers.remove(indexPath)}
                      type="button"
                    />
                  </Form.Field>
                </Overridable>
              </GroupField>
            );
          }}
        </ArrayField>
      </Overridable>
    );
  }
}

DatesFieldComponent.propTypes = {
  options: PropTypes.shape({
    type: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
  }).isRequired,
  requiredOptions: PropTypes.array,
  showEmptyValue: PropTypes.bool,
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

DatesFieldComponent.defaultProps = {
  label: i18next.t("Dates"),
  labelIcon: "calendar",
  placeholder: i18next.t("YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD"),
  helpText: i18next.t(
    "Format: DATE or DATE/DATE where DATE is YYYY or YYYY-MM or YYYY-MM-DD."
  ),
  addButtonLabel: i18next.t("Add date"),
  required: false,
  requiredOptions: [],
  showEmptyValue: false,
  optimized: true,
};

export const DatesField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.DatesField",
  DatesFieldComponent
);
