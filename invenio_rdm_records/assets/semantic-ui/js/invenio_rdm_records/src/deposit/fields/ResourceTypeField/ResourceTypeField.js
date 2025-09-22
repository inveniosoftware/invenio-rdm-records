// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
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

export class ResourceTypeFieldComponent extends Component {
  groupErrors = (errors, fieldPath) => {
    const fieldErrors = _get(errors, fieldPath);
    if (fieldErrors) {
      return { content: fieldErrors };
    }
    return null;
  };

  /**
   * Generate label value
   *
   * @param {object} option - back-end option
   * @returns {string} label
   */
  _label = (option) => {
    return option.type_name + (option.subtype_name ? " / " + option.subtype_name : "");
  };

  /**
   * Convert back-end options to front-end options.
   *
   * @param {array} propsOptions - back-end options
   * @returns {array} front-end options
   */
  createOptions = (propsOptions) => {
    return propsOptions
      .map((o) => ({ ...o, label: this._label(o) }))
      .sort((o1, o2) => o1.label.localeCompare(o2.label))
      .map((o) => {
        return {
          value: o.id,
          icon: o.icon,
          text: o.label,
        };
      });
  };

  render() {
    const {
      fieldPath,
      label,
      labelIcon: propLabelIcon,
      options,
      placeholder,
      helpText: propHelpText,
      schema,
      optimized,
      ...restProps
    } = this.props;
    const frontEndOptions = this.createOptions(options);

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

ResourceTypeFieldComponent.defaultProps = {
  label: i18next.t("Resource type"),
  labelIcon: "tag",
  labelclassname: "field-label-class",
  schema: "record",
  optimized: true,
};

export const ResourceTypeField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.ResourceTypeField",
  ResourceTypeFieldComponent
);
