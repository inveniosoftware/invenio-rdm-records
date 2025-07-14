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
import { AdditionalTitlesField } from "./AdditionalTitlesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { createFieldComponent, fieldCommonProps } from "../common/fieldComponents";

class TitlesFieldComponent extends Component {
  render() {
    const { fieldPath, options, label, labelIcon, required, disabled, recordUI } =
      this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.TitlesField.container"
        required={required}
        disabled={disabled}
        optimized
        options={options}
        recordUI={recordUI}
      >
        <>
          <Overridable
            id="InvenioRdmRecords.TitlesField.field"
            required={required}
            disabled={disabled}
            optimized
          >
            <TextField
              fieldPath={fieldPath}
              label={
                <Overridable
                  id="InvenioRdmRecords.TitlesField.label"
                  labelIcon={labelIcon}
                  label={label}
                >
                  <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
                </Overridable>
              }
              required={required}
              className="title-field"
              optimized
            />
          </Overridable>
          <Overridable
            id="InvenioRdmRecords.TitlesField.additional"
            options={options}
            recordUI={recordUI}
          >
            <AdditionalTitlesField
              options={options}
              recordUI={recordUI}
              fieldPath="metadata.additional_titles"
            />
          </Overridable>
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
  ...fieldCommonProps,
};

TitlesFieldComponent.defaultProps = {
  label: i18next.t("Title"),
  labelIcon: "book",
  required: false,
  recordUI: undefined,
};

export const TitlesField = createFieldComponent(
  "InvenioRdmRecords.TitlesField",
  TitlesFieldComponent
);
