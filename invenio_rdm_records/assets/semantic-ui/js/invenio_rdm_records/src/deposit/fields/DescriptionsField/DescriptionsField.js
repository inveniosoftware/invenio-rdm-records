/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Component } from "react";
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

function DescriptionsFieldComponent({fieldPath, label = i18next.t("Description"), labelIcon = "pencil", options, editorConfig = undefined, recordUI = undefined, disabled, required, placeholder, optimized = true, helpText}) {
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

DescriptionsFieldComponent.propTypes = {
  editorConfig: PropTypes.object,
  recordUI: PropTypes.object,
  options: PropTypes.object.isRequired,
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

export const DescriptionsField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.DescriptionsField",
  DescriptionsFieldComponent
);
