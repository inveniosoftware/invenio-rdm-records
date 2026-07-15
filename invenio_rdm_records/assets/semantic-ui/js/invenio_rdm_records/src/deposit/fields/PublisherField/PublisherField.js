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

function PublisherFieldComponent({fieldPath, label = i18next.t("Publisher"), labelIcon = "building outline", placeholder = i18next.t("Publisher"), disabled, required, helpText = i18next.t(
    "The publisher is used to formulate the citation, so consider the prominence of the role."
  )}) {
  return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.PublisherField.Container"
        fieldPath={fieldPath}
        icon={labelIcon}
        label={label}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        helpText={helpText}
      >
        <TextField
          fieldPath={fieldPath}
          helpText={helpText}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
        />
      </Overridable>
    );
}

PublisherFieldComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  ...fieldCommonProps,
};

export const PublisherField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.PublisherField",
  PublisherFieldComponent
);
