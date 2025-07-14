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
import { FieldLabel, TextField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { createFieldComponent, fieldCommonProps } from "../common/fieldComponents";

class VersionFieldComponent extends Component {
  render() {
    const { fieldPath, label, labelIcon, placeholder, disabled, required } = this.props;
    const helpText = (
      <Overridable id="InvenioRdmRecords.VersionField.help">
        <span>
          {i18next.t(
            "Mostly relevant for software and dataset uploads. A semantic version string is preferred see"
          )}
          <a href="https://semver.org/" target="_blank" rel="noopener noreferrer">
            {" "}
            semver.org
          </a>
          {i18next.t(", but any version string is accepted.")}
        </span>
      </Overridable>
    );

    return (
      <Overridable
        id="InvenioRdmRecords.VersionField.input"
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
              id="InvenioRdmRecords.VersionField.label"
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

export const VersionField = createFieldComponent(
  "InvenioRdmRecords.VersionField",
  VersionFieldComponent
);
