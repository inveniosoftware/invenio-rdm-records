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
  FieldLabel,
  TextField,
  createCommonDepositFieldComponent,
  fieldCommonProps,
} from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Trans } from "react-i18next";

class VersionFieldComponent extends Component {
  render() {
    const { fieldPath, label, labelIcon, placeholder, disabled, required } = this.props;
    const helpText = (
      <Overridable id="InvenioRdmRecords.DepositForm.VersionField.Help">
        <span>
          <Trans>
            Mostly relevant for software and dataset uploads. A{" "}
            <a href="https://semver.org/" target="_blank" rel="noopener noreferrer">
              semantic version string
            </a>{" "}
            is preferred, but any version string is accepted.
          </Trans>
        </span>
      </Overridable>
    );

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.VersionField.Container"
        fieldPath={fieldPath}
        helpText={helpText}
        labelIcon={labelIcon}
        label={label}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
      >
        <TextField
          fieldPath={fieldPath}
          helpText={helpText}
          label={
            <Overridable
              id="InvenioRdmRecords.DepositForm.VersionField.Label"
              labelIcon={labelIcon}
              label={label}
            >
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            </Overridable>
          }
          placeholder={placeholder}
          disabled={disabled}
          required={required}
        />
      </Overridable>
    );
  }
}

VersionFieldComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  ...fieldCommonProps,
};

VersionFieldComponent.defaultProps = {
  label: i18next.t("Version"),
  labelIcon: "code branch",
  placeholder: "",
};

export const VersionField = createCommonDepositFieldComponent(
  "InvenioRdmRecords.DepositForm.VersionField",
  VersionFieldComponent
);
