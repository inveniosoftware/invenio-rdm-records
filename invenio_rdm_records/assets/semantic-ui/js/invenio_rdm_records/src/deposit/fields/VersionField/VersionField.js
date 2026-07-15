/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import {
  FieldLabel,
  TextField,
  showHideOverridable,
  fieldCommonProps,
} from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";

function VersionFieldComponent({fieldPath, label = i18next.t("Version"), labelIcon = "code branch", placeholder = "", disabled, required}) {
  const helpText = (
      <span>
        {i18next.t(
          "Mostly relevant for software and dataset uploads. A semantic version string is preferred see"
        )}
        <a href="https://semver.org/" target="_blank" rel="noopener noreferrer">
          {" "}
          semver.org
        </a>
        {i18next.t(", but any version string is accepted.")}{" "}
        {i18next.t(
          "Maximum 191 characters. For longer descriptions, use 'Additional descriptions' with type 'Note'."
        )}
      </span>
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
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          maxLength={191}
        />
      </Overridable>
    );
}

VersionFieldComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  ...fieldCommonProps,
};

export const VersionField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.VersionField",
  VersionFieldComponent
);
