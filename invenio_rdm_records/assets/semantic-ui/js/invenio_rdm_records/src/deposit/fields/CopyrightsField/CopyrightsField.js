// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import {
  showHideOverridable,
  fieldCommonProps,
  FieldLabel,
  TextField,
} from "react-invenio-forms";

class CopyrightsFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      required,
      disabled,
      helpText,
      placeholder,
      optimized,
    } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.CopyrightsField.Container"
        label={label}
        labelIcon={labelIcon}
        required={required}
        disabled={disabled}
        helpText={helpText}
        placeholder={placeholder}
        optimized={optimized}
      >
        <TextField
          fieldPath={fieldPath}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          required={required}
          disabled={disabled}
          helpText={helpText}
          placeholder={placeholder}
          optimized={optimized}
        />
      </Overridable>
    );
  }
}

CopyrightsFieldComponent.propTypes = {
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

CopyrightsFieldComponent.defaultProps = {
  label: i18next.t("Copyright"),
  labelIcon: "copyright outline",
  required: false,
  helpText: i18next.t(
    "A copyright statement describing the ownership of the uploaded resource."
  ),
  placeholder: i18next.t("Copyright (C) {{currentYear}} The Authors.", {
    currentYear: new Date().getFullYear(),
  }),
  optimized: true,
};

export const CopyrightsField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.CopyrightsField",
  CopyrightsFieldComponent
);
