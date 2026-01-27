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
  TextField,
  GroupField,
  ArrayField,
  SelectField,
  showHideOverridable,
  fieldCommonProps,
} from "react-invenio-forms";
import { Button, Form } from "semantic-ui-react";
import Overridable from "react-overridable";
import { emptyRelatedWork } from "./initialValues";
import { ResourceTypeField } from "../ResourceTypeField";
import { i18next } from "@translations/invenio_rdm_records/i18next";

class RelatedWorksFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      required,
      disabled,
      options,
      showEmptyValue,
      helpText,
      addButtonLabel,
      optimized,
    } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.RelatedWorksField.Container"
        required={required}
        disabled={disabled}
        showEmptyValue={showEmptyValue}
        defaultNewValue={emptyRelatedWork}
        labelIcon={labelIcon}
        label={label}
        helpText={helpText}
        addButtonLabel={addButtonLabel}
        optimized={optimized}
      >
        <ArrayField
          addButtonLabel={addButtonLabel}
          defaultNewValue={emptyRelatedWork}
          fieldPath={fieldPath}
          helpText={helpText}
          label={label}
          labelIcon={labelIcon}
          required={required}
          disabled={disabled}
          showEmptyValue={showEmptyValue}
        >
          {({ arrayHelpers, indexPath }) => {
            const fieldPathPrefix = `${fieldPath}.${indexPath}`;

            return (
              <GroupField optimized={optimized}>
                <SelectField
                  clearable
                  fieldPath={`${fieldPathPrefix}.relation_type`}
                  label={i18next.t("Relation")}
                  aria-label={i18next.t("Relation")}
                  optimized={optimized}
                  options={options.relations}
                  placeholder={{
                    role: "option",
                    content: "Select relation...",
                  }}
                  required
                  width={3}
                />

                <TextField
                  fieldPath={`${fieldPathPrefix}.identifier`}
                  label={i18next.t("Identifier")}
                  required
                  width={4}
                />

                <SelectField
                  clearable
                  fieldPath={`${fieldPathPrefix}.scheme`}
                  label={i18next.t("Scheme")}
                  aria-label={i18next.t("Scheme")}
                  optimized={optimized}
                  options={options.scheme}
                  required
                  width={2}
                />

                <Overridable
                  id="InvenioRdmRecords.DepositForm.RelatedWorksField.ResourceType"
                  clearable
                  options={options.resource_type}
                  width={7}
                  optimized={optimized}
                >
                  <ResourceTypeField
                    optimized={optimized}
                    clearable
                    fieldPath={`${fieldPathPrefix}.resource_type`}
                    options={options.resource_type}
                    width={7}
                    labelclassname="small field-label-class"
                    schema="relatedWork"
                  />
                </Overridable>

                <Form.Field>
                  <Button
                    type="button"
                    aria-label={i18next.t("Remove field")}
                    className="close-btn"
                    icon="close"
                    onClick={() => arrayHelpers.remove(indexPath)}
                  />
                </Form.Field>
              </GroupField>
            );
          }}
        </ArrayField>
      </Overridable>
    );
  }
}

RelatedWorksFieldComponent.propTypes = {
  options: PropTypes.object.isRequired,
  showEmptyValue: PropTypes.bool,
  addButtonLabel: PropTypes.string,
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

RelatedWorksFieldComponent.defaultProps = {
  label: i18next.t("Related works"),
  labelIcon: "barcode",
  required: undefined,
  showEmptyValue: false,
  helpText: i18next.t(
    "Specify identifiers of related works. Supported identifiers include DOI, Handle, ARK, PURL, ISSN, ISBN, PubMed ID, PubMed Central ID, ADS Bibliographic Code, arXiv, Life Science Identifiers (LSID), EAN-13, ISTC, URNs, and URLs."
  ),
  addButtonLabel: i18next.t("Add related work"),
  optimized: true,
};

export const RelatedWorksField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.RelatedWorksField",
  RelatedWorksFieldComponent
);
