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
  createCommonDepositFieldComponent,
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
      >
        <>
          <Overridable
            id="InvenioRdmRecords.DepositForm.DescriptionsField.Input"
            fieldPath={fieldPath}
            editorConfig={editorConfig}
            htmlFor={fieldPath}
            icon={labelIcon}
            label={label}
            disabled={disabled}
            required={required}
          >
            <RichInputField
              className="description-field rel-mb-1 rel-mt-2"
              fieldPath={fieldPath}
              editorConfig={editorConfig}
              label={
                <Overridable
                  id="InvenioRdmRecords.DepositForm.DescriptionsField.Input.Label"
                  htmlFor={fieldPath}
                  icon={labelIcon}
                  label={label}
                >
                  <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
                </Overridable>
              }
              optimized
              disabled={disabled}
              required={required}
            />
          </Overridable>
          <Overridable
            id="InvenioRdmRecords.DepositForm.DescriptionsField.Additional"
            recordUI={recordUI}
            options={options}
            editorConfig={editorConfig}
          >
            <AdditionalDescriptionsField
              recordUI={recordUI}
              options={options}
              editorConfig={editorConfig}
              fieldPath="metadata.additional_descriptions"
            />
          </Overridable>
        </>
      </Overridable>
    );
  }
}

DescriptionsFieldComponent.propTypes = {
  editorConfig: PropTypes.object,
  recordUI: PropTypes.object,
  options: PropTypes.object.isRequired,
  ...fieldCommonProps,
};

DescriptionsFieldComponent.defaultProps = {
  label: i18next.t("Description"),
  labelIcon: "pencil",
  editorConfig: undefined,
  recordUI: undefined,
};

export const DescriptionsField = createCommonDepositFieldComponent(
  "InvenioRdmRecords.DepositForm.DescriptionsField",
  DescriptionsFieldComponent
);
