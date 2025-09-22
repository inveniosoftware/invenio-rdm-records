// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  FieldLabel,
  RichInputField,
  showHideOverridable,
  fieldCommonProps,
} from "react-invenio-forms";
import { AdditionalDescriptionsField } from "./components";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import Overridable from "react-overridable";

class DescriptionsFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      options,
      editorConfig: propEditorConfig,
      recordUI,
      disabled,
      required,
      placeholder,
      optimized,
      helpText,
    } = this.props;

    const editorConfig = {
      placeholder,
      ...propEditorConfig,
    };

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.DescriptionsField.Container"
        fieldPath={fieldPath}
        editorConfig={editorConfig}
        htmlFor={fieldPath}
        icon={labelIcon}
        label={label}
        recordUI={recordUI}
        options={options}
        disabled={disabled}
        required={required}
        optimized={optimized}
        helpText={helpText}
      >
        <>
          <RichInputField
            className="description-field rel-mb-1 rel-mt-2"
            fieldPath={fieldPath}
            editorConfig={editorConfig}
            label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
            optimized={optimized}
            disabled={disabled}
            required={required}
            helpText={helpText}
          />
          <AdditionalDescriptionsField
            recordUI={recordUI}
            options={options}
            editorConfig={editorConfig}
            optimized={optimized}
            fieldPath="metadata.additional_descriptions"
          />
        </>
      </Overridable>
    );
  }
}

DescriptionsFieldComponent.propTypes = {
  editorConfig: PropTypes.object,
  recordUI: PropTypes.object,
  options: PropTypes.object.isRequired,
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

DescriptionsFieldComponent.defaultProps = {
  label: i18next.t("Description"),
  labelIcon: "pencil",
  editorConfig: undefined,
  recordUI: undefined,
  optimized: true,
};

export const DescriptionsField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.DescriptionsField",
  DescriptionsFieldComponent
);
