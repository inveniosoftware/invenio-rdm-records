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
  showHideOverridable,
  mandatoryFieldCommonProps,
} from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";

class PublicationDateFieldComponent extends Component {
  render() {
    const { fieldPath, helpText, label, labelIcon, placeholder } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.PublicationDateField.Container"
        fieldPath={fieldPath}
        helpText={helpText}
        placeholder={placeholder}
        icon={labelIcon}
        label={label}
      >
        <TextField
          fieldPath={fieldPath}
          helpText={helpText}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          placeholder={placeholder}
        />
      </Overridable>
    );
  }
}

PublicationDateFieldComponent.propTypes = {
  helpText: PropTypes.string,
  placeholder: PropTypes.string,
  ...mandatoryFieldCommonProps,
};

PublicationDateFieldComponent.defaultProps = {
  helpText: i18next.t(
    "In case your upload was already published elsewhere, please use the date of the first publication. Format: YYYY-MM-DD, YYYY-MM, or YYYY. For intervals use DATE/DATE, e.g. 1939/1945."
  ),
  label: i18next.t("Publication date"),
  labelIcon: "calendar",
  placeholder: i18next.t(
    "YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD for intervals. MM and DD are optional."
  ),
};

export const PublicationDateField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.PublicationDateField",
  PublicationDateFieldComponent
);
