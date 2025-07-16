// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import Overridable from "react-overridable";
import { FieldLabel, TextField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import {
  createCommonDepositFieldComponent,
  fieldCommonProps,
} from "../common/fieldComponents";

class CopyrightsFieldComponent extends Component {
  render() {
    const { fieldPath, label, labelIcon, required, disabled, helpText, placeholder } =
      this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.CopyrightsField.Container"
        label={label}
        labelIcon={labelIcon}
        required={required}
        disabled={disabled}
        helpText={helpText}
        placeholder={placeholder}
      >
        <TextField
          fieldPath={fieldPath}
          label={
            <Overridable
              id="InvenioRdmRecords.DepositForm.CopyrightsField.Label"
              labelIcon={labelIcon}
              label={label}
            >
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            </Overridable>
          }
          required={required}
          disabled={disabled}
          helpText={helpText}
          placeholder={placeholder}
          optimized
        />
      </Overridable>
    );
  }
}

CopyrightsFieldComponent.propTypes = {
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
};

export const CopyrightsField = createCommonDepositFieldComponent(
  "InvenioRdmRecords.DepositForm.CopyrightsField",
  CopyrightsFieldComponent
);
