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
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class CopyrightsField extends Component {
  render() {
    const { fieldPath, label, required } = this.props;
    return (
      <>
        <TextField
          fieldPath={fieldPath}
          label={
            <FieldLabel htmlFor={fieldPath} icon="copyright outline" label={label} />
          }
          required={required}
          helpText={i18next.t(
            "Optionally specify holder, year and copyright statement for this resource (if any)"
          )}
          optimized
        />
      </>
    );
  }
}

CopyrightsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  required: PropTypes.bool,
};

CopyrightsField.defaultProps = {
  label: i18next.t("Copyrights"),
  required: false,
};
