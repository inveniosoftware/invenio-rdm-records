/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Component } from "react";
import PropTypes from "prop-types";
import _get from "lodash/get";
import {
  FieldLabel,
  SelectField,
  showHideOverridable,
  mandatoryFieldCommonProps,
} from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import Overridable from "react-overridable";

export function ResourceTypeFieldComponent({fieldPath, label = i18next.t("Resource type"), labelIcon = "tag", options, placeholder, helpText, schema = "record", optimized = true, ...restProps}) {
  restProps = {
    ...restProps,
    labelclassname: typeof restProps.labelclassname === "undefined" ? "field-label-class" : restProps.labelclassname
  };

  const groupErrors = (errors, fieldPath) => {
    const fieldErrors = _get(errors, fieldPath);
    if (fieldErrors) {
      return { content: fieldErrors };
    }
    return null;
  };

  const _label = (option) => {
    return option.type_name + (option.subtype_name ? " / " + option.subtype_name : "");
  };

  const createOptions = (propsOptions) => {
    return propsOptions
      .map((o) => ({ ...o, label: _label(o) }))
      .sort((o1, o2) => o1.label.localeCompare(o2.label))
      .map((o) => {
        return {
          value: o.id,
          icon: o.icon,
          text: o.label,
        };
      });
  };

  const frontEndOptions = createOptions(options);

    // Cannot show helpText or labelIcon when the field is inside an ArrayField
    const helpText = schema === "record" ? propHelpText : undefined;
    const labelIcon = schema === "record" ? propLabelIcon : undefined;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.ResourceTypeField.Container"
        fieldPath={fieldPath}
        labelIcon={labelIcon}
        label={label}
        aria-label={label}
        options={frontEndOptions}
        placeholder={placeholder}
        helpText={helpText}
        optimized={optimized}
      >
        <SelectField
          fieldPath={fieldPath}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          optimized={optimized}
          aria-label={label}
          options={frontEndOptions}
          selectOnBlur={false}
          helpText={helpText}
          placeholder={placeholder}
          required
          {...restProps}
        />
      </Overridable>
    );
}

ResourceTypeFieldComponent.propTypes = {
  labelclassname: PropTypes.string,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.string,
      type_name: PropTypes.string,
      subtype_name: PropTypes.string,
      id: PropTypes.string,
    })
  ).isRequired,
  schema: PropTypes.oneOf(["record", "relatedWork"]).isRequired,
  optimized: PropTypes.bool,
  ...mandatoryFieldCommonProps,
};

export const ResourceTypeField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.ResourceTypeField",
  ResourceTypeFieldComponent
);
