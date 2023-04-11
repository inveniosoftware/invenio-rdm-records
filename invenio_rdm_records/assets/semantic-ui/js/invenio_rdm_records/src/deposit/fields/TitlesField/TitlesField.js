// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";

import { FieldLabel, TextField } from "react-invenio-forms";
import { AdditionalTitlesField } from "./AdditionalTitlesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class TitlesField extends Component {
  render() {
    const { fieldPath, options, label, required, recordUI } = this.props;

    return (
      <>
        <TextField
          fieldPath={fieldPath}
          label={<FieldLabel htmlFor={fieldPath} icon="book" label={label} />}
          required={required}
          className="title-field"
          optimized
        />
        <AdditionalTitlesField
          options={options}
          recordUI={recordUI}
          fieldPath="metadata.additional_titles"
        />
      </>
    );
  }
}

TitlesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
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
  required: PropTypes.bool,
  recordUI: PropTypes.object,
};

TitlesField.defaultProps = {
  label: i18next.t("Title"),
  required: false,
  recordUI: undefined,
};
