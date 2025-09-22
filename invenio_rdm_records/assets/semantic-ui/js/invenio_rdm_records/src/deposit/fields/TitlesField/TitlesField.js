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
import { AdditionalTitlesField } from "./AdditionalTitlesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";

class TitlesFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      options,
      label,
      labelIcon,
      recordUI,
      helpText,
      placeholder,
      optimized,
    } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.TitlesField.Container"
        options={options}
        recordUI={recordUI}
        helpText={helpText}
        placeholder={placeholder}
        optimized={optimized}
      >
        <>
          <TextField
            fieldPath={fieldPath}
            helpText={helpText}
            placeholder={placeholder}
            label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
            required
            className="title-field"
            optimized={optimized}
          />
          <AdditionalTitlesField
            options={options}
            recordUI={recordUI}
            fieldPath="metadata.additional_titles"
            optimized={optimized}
          />
        </>
      </Overridable>
    );
  }
}

TitlesFieldComponent.propTypes = {
  options: PropTypes.shape({
    type: PropTypes.arrayOf(
      PropTypes.shape({
        icon: PropTypes.string,
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
    lang: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
  }).isRequired,
  recordUI: PropTypes.object,
  ...mandatoryFieldCommonProps,
};

TitlesFieldComponent.defaultProps = {
  label: i18next.t("Title"),
  labelIcon: "book",
  required: false,
  recordUI: undefined,
  optimized: true,
};

export const TitlesField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.TitlesField",
  TitlesFieldComponent
);
