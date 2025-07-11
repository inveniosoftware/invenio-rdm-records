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
import { createFieldComponent, fieldCommonProps } from "../common/propTypes";

class PublisherFieldComponent extends Component {
  render() {
    const { fieldPath, label, labelIcon, placeholder, disabled, required } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.PublisherField.input"
        fieldPath={fieldPath}
        icon={labelIcon}
        label={label}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
      >
        <TextField
          fieldPath={fieldPath}
          helpText={i18next.t(
            "The publisher is used to formulate the citation, so consider the prominence of the role."
          )}
          label={
            <Overridable
              id="InvenioRdmRecords.PublisherField.label"
              icon={labelIcon}
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

PublisherFieldComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  ...fieldCommonProps,
};

PublisherFieldComponent.defaultProps = {
  label: i18next.t("Publisher"),
  labelIcon: "building outline",
  placeholder: i18next.t("Publisher"),
};

export const PublisherField = createFieldComponent(
  "InvenioRdmRecords.PublisherField",
  PublisherFieldComponent
);
